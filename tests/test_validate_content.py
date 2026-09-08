from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_content import validate_project


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["id", "title", "difficulty"],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "title": {"type": "string", "minLength": 1},
        "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
    },
}
QUESTION_ID = "550e8400-e29b-41d4-a716-446655440000"


class ValidateContentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "questions").mkdir()
        (self.root / "schemas").mkdir()
        (self.root / "schemas" / "question-metadata.schema.json").write_text(
            json.dumps(SCHEMA), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_valid_fixture(self) -> None:
        (self.root / "catalog.yaml").write_text(
            """概念题:\n  - id: 550e8400-e29b-41d4-a716-446655440000\n    title: Agent 如何调用工具？\n    difficulty: medium\n""",
            encoding="utf-8",
        )
        (self.root / "questions" / f"{QUESTION_ID}.md").write_text(
            "# 问题\n\nAgent 如何调用工具？\n\n# 回答\n\n参考回答。\n",
            encoding="utf-8",
        )

    def messages(self) -> list[str]:
        return [issue.message for issue in validate_project(self.root)]

    def test_valid_project_passes(self) -> None:
        self.write_valid_fixture()
        self.assertEqual(validate_project(self.root), [])

    def test_duplicate_id_in_same_category_fails(self) -> None:
        self.write_valid_fixture()
        catalog_path = self.root / "catalog.yaml"
        catalog_path.write_text(catalog_path.read_text(encoding="utf-8") + """  - id: 550e8400-e29b-41d4-a716-446655440000\n    title: Agent 如何调用工具？\n    difficulty: medium\n""", encoding="utf-8")
        self.assertTrue(any("重复出现" in message for message in self.messages()))

    def test_cross_category_metadata_must_match(self) -> None:
        self.write_valid_fixture()
        catalog_path = self.root / "catalog.yaml"
        catalog_path.write_text(catalog_path.read_text(encoding="utf-8") + """工具调用:\n  - id: 550e8400-e29b-41d4-a716-446655440000\n    title: 不同标题\n    difficulty: hard\n""", encoding="utf-8")
        messages = self.messages()
        self.assertTrue(any("title 不一致" in message for message in messages))
        self.assertTrue(any("difficulty 不一致" in message for message in messages))

    def test_missing_and_orphan_files_fail(self) -> None:
        self.write_valid_fixture()
        (self.root / "questions" / f"{QUESTION_ID}.md").unlink()
        orphan_id = "123e4567-e89b-12d3-a456-426614174000"
        (self.root / "questions" / f"{orphan_id}.md").write_text(
            "# 问题\n\n孤立题目\n\n# 回答\n\n回答\n", encoding="utf-8"
        )
        messages = self.messages()
        self.assertTrue(any("缺少 questions/" in message for message in messages))
        self.assertTrue(any("没有收录" in message for message in messages))

    def test_catalog_title_can_summarize_question(self) -> None:
        self.write_valid_fixture()
        (self.root / "questions" / f"{QUESTION_ID}.md").write_text(
            "# 问题\n\n这是一个比目录标题更长、更完整的问题描述吗？\n\n# 回答\n\n参考回答。\n",
            encoding="utf-8",
        )
        self.assertEqual(validate_project(self.root), [])

    def test_required_sections_are_checked(self) -> None:
        self.write_valid_fixture()
        (self.root / "questions" / f"{QUESTION_ID}.md").write_text(
            "# 问题\n\n另一个问题？\n\n# 回答\n\n", encoding="utf-8"
        )
        messages = self.messages()
        self.assertTrue(any("缺少非空的“# 回答”" in message for message in messages))

    def test_broken_local_link_fails(self) -> None:
        self.write_valid_fixture()
        question_path = self.root / "questions" / f"{QUESTION_ID}.md"
        question_path.write_text(
            question_path.read_text(encoding="utf-8") + "\n[文档](../docs/missing.md)\n",
            encoding="utf-8",
        )
        self.assertTrue(any("指向不存在" in message for message in self.messages()))

    def test_uppercase_uuid_fails(self) -> None:
        self.write_valid_fixture()
        catalog_path = self.root / "catalog.yaml"
        catalog_path.write_text(
            catalog_path.read_text(encoding="utf-8").replace(QUESTION_ID, QUESTION_ID.upper()),
            encoding="utf-8",
        )
        self.assertTrue(any("标准小写 UUID" in message for message in self.messages()))


if __name__ == "__main__":
    unittest.main()
