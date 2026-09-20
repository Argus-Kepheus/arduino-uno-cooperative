from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from generate_docs import render_file, replace_region, target_files


HEADER_PATTERNS = {
    "doc_id": re.compile(r"<!--\s*doc-id:\s*([^>]+?)\s*-->"),
    "language": re.compile(r"<!--\s*language:\s*([^>]+?)\s*-->"),
    "revision": re.compile(r"<!--\s*content-revision:\s*([^>]+?)\s*-->"),
}
SECTION_PATTERN = re.compile(r"<!--\s*section:\s*([^>]+?)\s*-->")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class DocumentationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metadata = load_json(ROOT / "docs" / "metadata.json")
        cls.hardware = load_json(ROOT / "config" / "hardware.json")
        cls.runtime = load_json(ROOT / "config" / "runtime.json")
        cls.avr = load_json(ROOT / "config" / "avr.json")
        cls.toolchain = load_json(ROOT / "config" / "toolchain.json")

    def test_semantic_metadata_matches_all_language_documents(self) -> None:
        languages = self.metadata["languages"]
        for doc_id, spec in self.metadata["documents"].items():
            for language in languages:
                relative = spec["paths"][language]
                text = (ROOT / relative).read_text(encoding="utf-8")

                headers = {}
                for key, pattern in HEADER_PATTERNS.items():
                    match = pattern.search(text)
                    self.assertIsNotNone(match, f"{relative}: missing {key}")
                    headers[key] = match.group(1).strip()

                self.assertEqual(doc_id, headers["doc_id"], relative)
                self.assertEqual(language, headers["language"], relative)
                self.assertEqual(
                    str(spec["content_revision"]),
                    headers["revision"],
                    relative,
                )

                sections = [
                    match.group(1).strip()
                    for match in SECTION_PATTERN.finditer(text)
                ]
                self.assertEqual(spec["required_sections"], sections, relative)

    def test_generated_document_regions_round_trip_exactly(self) -> None:
        for relative, language, names in target_files():
            path = ROOT / relative
            actual = path.read_text(encoding="utf-8")
            expected = render_file(
                path,
                language,
                names,
                self.hardware,
                self.runtime,
                self.avr,
                self.toolchain,
            )
            self.assertEqual(actual, expected, relative)

    def test_generated_region_replacement_fails_if_region_is_missing(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing generated region"):
            replace_region("# document\n", "missing-region", "body")


if __name__ == "__main__":
    unittest.main()
