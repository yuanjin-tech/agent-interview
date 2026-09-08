#!/usr/bin/env python3
"""校验题目目录与 Markdown 正文是否完整一致。"""

from __future__ import annotations

import json
import re
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UUID_FILENAME = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\.md$"
)
TOP_LEVEL_HEADING = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
REQUIRED_SECTIONS = ("问题", "回答")


@dataclass(frozen=True, order=True)
class Issue:
    """一条可定位的校验错误。"""

    location: str
    message: str

    def __str__(self) -> str:
        return f"ERROR {self.location}\n  {self.message}"


def _load_yaml(path: Path) -> Any:
    yaml = YAML(typ="safe")
    with path.open("r", encoding="utf-8") as file:
        return yaml.load(file)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _canonical_uuid(value: str) -> str | None:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        return None
    return str(parsed) if str(parsed) == value else None


def parse_sections(markdown: str) -> dict[str, str]:
    """按一级标题分割题目正文。"""
    matches = list(TOP_LEVEL_HEADING.finditer(markdown))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[match.group(1).strip()] = markdown[start:end].strip()
    return sections


def _plain_question_title(value: str) -> str:
    """将问题段落规范化为可与目录比较的单行文本。"""
    return " ".join(line.strip() for line in value.splitlines() if line.strip())


def _validate_local_links(path: Path, markdown: str, root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for raw_target in MARKDOWN_LINK.findall(markdown):
        target = unquote(raw_target.strip("<>"))
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith(("#", "/")):
            continue
        linked_path = (path.parent / parsed.path).resolve()
        try:
            linked_path.relative_to(root.resolve())
        except ValueError:
            issues.append(Issue(str(path.relative_to(root)), f"本地链接超出项目目录：{target}"))
            continue
        if not linked_path.exists():
            issues.append(Issue(str(path.relative_to(root)), f"本地链接指向不存在的文件：{target}"))
    return issues


def validate_project(root: Path = PROJECT_ROOT) -> list[Issue]:
    """返回项目内所有题库一致性问题。"""
    issues: list[Issue] = []
    catalog_path = root / "catalog.yaml"
    questions_dir = root / "questions"
    schema_path = root / "schemas" / "question-metadata.schema.json"

    if not catalog_path.is_file():
        return [Issue("catalog.yaml", "题目目录不存在。")]
    if not questions_dir.is_dir():
        return [Issue("questions", "题目正文目录不存在。")]

    try:
        catalog = _load_yaml(catalog_path)
    except Exception as error:  # ruamel 的解析异常类型较多
        return [Issue("catalog.yaml", f"YAML 解析失败：{error}")]

    if not isinstance(catalog, dict):
        return [Issue("catalog.yaml", "顶层必须是“分类名称 -> 题目数组”的对象。")]

    try:
        metadata_validator = Draft202012Validator(_load_json(schema_path))
    except (OSError, json.JSONDecodeError) as error:
        return [Issue("schemas/question-metadata.schema.json", f"Schema 加载失败：{error}")]

    entries_by_id: dict[str, list[tuple[str, dict[str, Any], str]]] = defaultdict(list)
    indexed_ids: set[str] = set()

    for category, entries in catalog.items():
        category_location = f"catalog.yaml [{category}]"
        if not isinstance(category, str) or not category.strip():
            issues.append(Issue("catalog.yaml", "分类名称必须是非空字符串。"))
            continue
        if not isinstance(entries, list) or not entries:
            issues.append(Issue(category_location, "分类内必须是非空题目数组。"))
            continue

        seen_in_category: set[str] = set()
        for index, entry in enumerate(entries, start=1):
            location = f"{category_location} 第 {index} 项"
            if not isinstance(entry, dict):
                issues.append(Issue(location, "题目元数据必须是对象。"))
                continue

            for error in sorted(metadata_validator.iter_errors(entry), key=lambda item: list(item.path)):
                field = ".".join(str(part) for part in error.path)
                field_hint = f" ({field})" if field else ""
                issues.append(Issue(location, f"Schema 校验失败{field_hint}：{error.message}"))

            question_id = entry.get("id")
            if not isinstance(question_id, str):
                continue
            canonical_id = _canonical_uuid(question_id)
            if canonical_id is None:
                issues.append(Issue(location, f"id 不是标准小写 UUID：{question_id}"))
                continue
            if canonical_id in seen_in_category:
                issues.append(Issue(location, f"UUID {canonical_id} 在分类“{category}”中重复出现。"))
            seen_in_category.add(canonical_id)
            indexed_ids.add(canonical_id)
            entries_by_id[canonical_id].append((category, entry, location))

    for question_id, occurrences in entries_by_id.items():
        reference = occurrences[0][1]
        for category, entry, location in occurrences[1:]:
            for field in ("title", "difficulty"):
                if entry.get(field) != reference.get(field):
                    issues.append(
                        Issue(
                            location,
                            f"UUID {question_id} 跨分类复用时 {field} 不一致（分类：{category}）。",
                        )
                    )

    markdown_ids: set[str] = set()
    for question_path in sorted(questions_dir.glob("*.md")):
        relative_path = str(question_path.relative_to(root))
        if not UUID_FILENAME.fullmatch(question_path.name):
            issues.append(Issue(relative_path, "题目文件名必须是标准 UUID.md。"))
            continue
        question_id = question_path.stem.lower()
        if question_path.stem != question_id:
            issues.append(Issue(relative_path, "题目文件名中的 UUID 必须使用小写。"))
        if question_id in markdown_ids:
            issues.append(Issue(relative_path, f"UUID {question_id} 对应了多个正文文件。"))
        markdown_ids.add(question_id)

        markdown = question_path.read_text(encoding="utf-8")
        sections = parse_sections(markdown)
        for section in REQUIRED_SECTIONS:
            if not sections.get(section, "").strip():
                issues.append(Issue(relative_path, f"缺少非空的“# {section}”部分。"))

        occurrences = entries_by_id.get(question_id)
        if occurrences and sections.get("问题"):
            catalog_title = occurrences[0][1].get("title")
            markdown_title = _plain_question_title(sections["问题"])
            if isinstance(catalog_title, str) and markdown_title != catalog_title:
                issues.append(
                    Issue(relative_path, f"问题文字与 catalog.yaml 标题不一致：{markdown_title!r}。")
                )

        issues.extend(_validate_local_links(question_path, markdown, root))

    for question_id in sorted(indexed_ids - markdown_ids):
        issues.append(Issue("catalog.yaml", f"UUID {question_id} 缺少 questions/{question_id}.md。"))
    for question_id in sorted(markdown_ids - indexed_ids):
        issues.append(Issue(f"questions/{question_id}.md", "题目正文没有收录到 catalog.yaml。"))

    return sorted(set(issues))


def main() -> int:
    issues = validate_project()
    if issues:
        print("\n\n".join(str(issue) for issue in issues))
        print(f"\n校验失败：共发现 {len(issues)} 个问题。")
        return 1
    print("校验通过：catalog.yaml 与所有题目正文保持一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
