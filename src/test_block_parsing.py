import unittest

from block_parsing import markdown_to_blocks   # adjust import if function is elsewhere


class TestMarkdownToBlocks(unittest.TestCase):

    def test_basic_example(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        expected = [
            "This is **bolded** paragraph",
            "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
            "- This is a list\n- with items",
        ]
        self.assertEqual(blocks, expected)

    def test_heading_and_paragraph(self):
        md = """
# Heading 1

Some paragraph text here.

Another paragraph after a blank line.
"""
        blocks = markdown_to_blocks(md)
        expected = [
            "# Heading 1",
            "Some paragraph text here.",
            "Another paragraph after a blank line."
        ]
        self.assertEqual(blocks, expected)

    def test_multiple_blank_lines(self):
        md = """
Paragraph one


Paragraph two with extra blank lines above



Paragraph three
"""
        blocks = markdown_to_blocks(md)
        expected = [
            "Paragraph one",
            "Paragraph two with extra blank lines above",
            "Paragraph three"
        ]
        self.assertEqual(blocks, expected)

    def test_leading_trailing_newlines(self):
        md = """




First block

Second block



"""
        blocks = markdown_to_blocks(md)
        expected = [
            "First block",
            "Second block"
        ]
        self.assertEqual(blocks, expected)

    def test_single_block_no_newlines(self):
        md = "Just one paragraph with no blank lines."
        blocks = markdown_to_blocks(md)
        expected = ["Just one paragraph with no blank lines."]
        self.assertEqual(blocks, expected)

    def test_empty_input(self):
        md = ""
        self.assertEqual(markdown_to_blocks(md), [])

    def test_only_blank_lines(self):
        md = "\n\n\n\n"
        self.assertEqual(markdown_to_blocks(md), [])