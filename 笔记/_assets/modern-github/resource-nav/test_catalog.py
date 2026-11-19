import tempfile
import unittest
from pathlib import Path

from build import render_page
from catalog import load_resources


class CatalogTests(unittest.TestCase):
    def load(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resources.csv"
            path.write_text(text, encoding="utf-8")
            return load_resources(path)

    def test_reads_utf8_and_csv_quoting(self):
        rows = self.load('title,url,category\n"文档,指南",https://example.com/, Git \n')
        self.assertEqual(rows, [{"title": "文档,指南", "url": "https://example.com/", "category": "Git"}])

    def test_requires_expected_header(self):
        with self.assertRaises(ValueError):
            self.load("name,url,category\nDocs,https://example.com/,Git\n")

    def test_rejects_empty_catalog(self):
        with self.assertRaises(ValueError):
            self.load("title,url,category\n")

    def test_rejects_blank_field(self):
        with self.assertRaises(ValueError):
            self.load("title,url,category\n ,https://example.com/,Git\n")

    def test_rejects_non_web_url(self):
        with self.assertRaises(ValueError):
            self.load("title,url,category\nBad,javascript:alert(1),Git\n")

    def test_rejects_url_without_host(self):
        with self.assertRaises(ValueError):
            self.load("title,url,category\nBad,https:///missing-host,Git\n")

    def test_rejects_extra_column(self):
        with self.assertRaises(ValueError):
            self.load("title,url,category\nDocs,https://example.com/,Git,extra\n")

    def test_rejects_duplicate_url(self):
        with self.assertRaises(ValueError):
            self.load("title,url,category\nOne,https://example.com/,Git\nTwo, https://example.com/ ,Python\n")

    def test_page_escapes_text_and_attribute_values(self):
        rows = self.load('title,url,category\n"<script>alert(1)</script>","https://example.com/?q=""x""&a=1",A&B\n')
        page = render_page(rows)
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script>", page)
        self.assertIn("&quot;x&quot;&amp;a=1", page)
        self.assertIn("A&amp;B", page)


if __name__ == "__main__":
    unittest.main()
