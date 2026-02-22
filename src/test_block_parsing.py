import unittest

from block_parsing import markdown_to_blocks, BlockType, block_to_block_type, markdown_to_html_node, BlockType, extract_title

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


import unittest

class TestBlockToBlockType(unittest.TestCase):

    def test_paragraph(self):
        block = "This is just a normal paragraph with **bold** and _italic_."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_level_1(self):
        block = "# Main Title"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_level_3(self):
        block = "### Subsection"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_no_space_after_hash(self):
        block = "#No space here"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block(self):
        block = """```
print("Hello")
print("World")
```"""
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_single_line(self):
        block = "```\nhello\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote_single_line(self):
        block = "> This is a wise quote."
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_multi_line(self):
        block = """> First line
> Second line
> Third line"""
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_with_space_after_gt(self):
        block = """> Quote
>  Another line"""
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_unordered_list(self):
        block = """- Item one
- Item two
- Item three"""
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        block = """1. First
2. Second
3. Third"""
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_wrong_start(self):
        block = """2. Wrong start
3. Next"""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_not_incrementing(self):
        block = """1. First
3. Skipped two"""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_mixed_content_falls_to_paragraph(self):
        block = "- List item\n\nAnother paragraph"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

class TestMarkdownToHTMLNode(unittest.TestCase):

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        expected = (
            "<div>"
            "<p>This is <b>bolded</b> paragraph text in a p tag here</p>"
            "<p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p>"
            "</div>"
        )
        self.assertEqual(html, expected)


class TestExtractTitle(unittest.TestCase):

    def test_extract_title_basic(self):
        md = """
# My Awesome Page

Some content here
"""
        title = extract_title(md)
        self.assertEqual(title, "My Awesome Page")

    def test_extract_title_with_extra_spaces(self):
        md = """
   #    Tolkien Fan Club    

Paragraph
"""
        title = extract_title(md)
        self.assertEqual(title, "Tolkien Fan Club")

    def test_extract_title_no_h1(self):
        md = """
## This is H2, not H1

No title here
"""
        with self.assertRaises(ValueError) as cm:
            extract_title(md)
        self.assertEqual(str(cm.exception), "No H1 heading found in markdown document")

    def test_extract_title_multiple_h1(self):
        md = """
# First Title

Some text

# Second Title (should ignore this one)
"""
        title = extract_title(md)
        self.assertEqual(title, "First Title")  # only the first one counts

    def test_extract_title_empty(self):
        md = ""
        with self.assertRaises(ValueError):
            extract_title(md)