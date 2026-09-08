#!/usr/bin/env python3
"""以交互方式创建一道面试题，并同步更新题目目录。"""

from __future__ import annotations

import os
import tempfile
import uuid
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

import questionary
from questionary import Choice
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = PROJECT_ROOT / "catalog.yaml"
QUESTIONS_DIR = PROJECT_ROOT / "questions"

NEW_CATEGORY = "__new_category__"
DIFFICULTIES = (
    Choice("初级", value="easy"),
    Choice("中级", value="medium"),
    Choice("高级", value="hard"),
)


def create_yaml() -> YAML:
    """创建用于读取和写入目录的 YAML 实例。"""
    yaml = YAML(typ="rt")
    yaml.allow_unicode = True
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def load_catalog(path: Path) -> MutableMapping[str, Any]:
    """读取题目目录，并检查其顶层结构。"""
    if not path.exists():
        raise FileNotFoundError(f"找不到题目目录：{path}")

    yaml = create_yaml()
    with path.open("r", encoding="utf-8") as file:
        catalog = yaml.load(file)

    if catalog is None:
        return CommentedMap()
    if not isinstance(catalog, MutableMapping):
        raise ValueError("catalog.yaml 的顶层必须是分类名称到题目数组的映射。")

    for category, questions in catalog.items():
        if not isinstance(category, str) or not category.strip():
            raise ValueError("catalog.yaml 中的分类名称必须是非空字符串。")
        if not isinstance(questions, list):
            raise ValueError(f"分类“{category}”的值必须是题目数组。")

    return catalog


def ask_non_empty_text(message: str) -> str | None:
    """询问一个不允许为空的文本值。"""
    answer = questionary.text(
        message,
        validate=lambda value: bool(value.strip()) or "内容不能为空，请重新输入。",
    ).ask()
    return answer.strip() if answer is not None else None


def ask_category(catalog: MutableMapping[str, Any]) -> str | None:
    """从现有分类中选择，或者输入一个新分类。"""
    choices = [Choice(category, value=category) for category in catalog]
    choices.append(Choice("新建分类", value=NEW_CATEGORY))

    category = questionary.select(
        "请选择这道题所属的分类：",
        choices=choices,
    ).ask()

    if category is None:
        return None
    if category == NEW_CATEGORY:
        return ask_non_empty_text("请输入新分类的名称：")
    return category


def collect_existing_ids(catalog: MutableMapping[str, Any]) -> set[str]:
    """收集目录中已经使用的题目 ID。"""
    existing_ids: set[str] = set()
    for questions in catalog.values():
        for question in questions:
            if isinstance(question, MutableMapping) and isinstance(question.get("id"), str):
                existing_ids.add(question["id"])
    return existing_ids


def generate_question_id(catalog: MutableMapping[str, Any]) -> str:
    """生成一个尚未出现在目录中的 UUID。"""
    existing_ids = collect_existing_ids(catalog)
    while True:
        question_id = str(uuid.uuid4())
        if question_id not in existing_ids:
            return question_id


def write_catalog_atomically(catalog: MutableMapping[str, Any], path: Path) -> None:
    """先写临时文件，再原子替换目录文件。"""
    yaml = create_yaml()
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=".catalog-",
        suffix=".yaml.tmp",
        dir=path.parent,
    )
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            yaml.dump(catalog, file)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def create_question(
    *,
    title: str,
    difficulty: str,
    category: str,
    catalog_path: Path = CATALOG_PATH,
    questions_dir: Path = QUESTIONS_DIR,
) -> Path:
    """创建题目文件，并将题目元数据加入指定分类。"""
    catalog = load_catalog(catalog_path)
    question_id = generate_question_id(catalog)
    question_path = questions_dir / f"{question_id}.md"

    metadata = CommentedMap(
        (
            ("id", question_id),
            ("title", title),
            ("difficulty", difficulty),
        )
    )

    if category not in catalog:
        catalog[category] = CommentedSeq()
    catalog[category].append(metadata)

    questions_dir.mkdir(parents=True, exist_ok=True)
    content = f"# 问题\n\n{title}\n\n# 回答\n\n<!-- 请在这里填写回答 -->\n"

    try:
        with question_path.open("x", encoding="utf-8") as file:
            file.write(content)
        write_catalog_atomically(catalog, catalog_path)
    except Exception:
        question_path.unlink(missing_ok=True)
        raise

    return question_path


def main() -> int:
    """运行交互式新建题目流程。"""
    try:
        catalog = load_catalog(CATALOG_PATH)

        title = ask_non_empty_text("请输入面试题的标题：")
        if title is None:
            print("已取消创建。")
            return 1

        difficulty = questionary.select(
            "请选择这道题的难度：",
            choices=DIFFICULTIES,
        ).ask()
        if difficulty is None:
            print("已取消创建。")
            return 1

        category = ask_category(catalog)
        if category is None:
            print("已取消创建。")
            return 1

        question_path = create_question(
            title=title,
            difficulty=difficulty,
            category=category,
        )
    except (KeyboardInterrupt, EOFError):
        print("\n已取消创建。")
        return 1
    except (OSError, ValueError) as error:
        print(f"创建失败：{error}")
        return 1

    relative_path = question_path.relative_to(PROJECT_ROOT)
    print("\n问题创建成功。")
    print(f"请继续编辑问题文件：{relative_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
