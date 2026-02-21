# src/block_parsing.py

from enum import Enum

from htmlnode import ParentNode, LeafNode, HTMLNode
from textnode import TextNode, TextType, text_to_textnodes
from textnode import text_node_to_html_node  # assuming this function exists in textnode.py


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown: str) -> list[str]:
    """
    Split full markdown document into separate blocks.
    Blocks are separated by blank lines (two newlines).
    """
    raw_blocks = markdown.split("\n\n")
    cleaned_blocks = []
    
    for block in raw_blocks:
        cleaned = block.strip()
        if cleaned:
            cleaned_blocks.append(cleaned)
    
    return cleaned_blocks


def block_to_block_type(block: str) -> BlockType:
    """
    Determine what kind of markdown block we are dealing with.
    Assumes the block is already stripped.
    """
    lines = block.split("\n")
    first_line = lines[0]

    # Heading: 1–6 # followed by space
    if first_line.startswith("#"):
        hash_count = 0
        while hash_count < len(first_line) and first_line[hash_count] == "#":
            hash_count += 1
        if 1 <= hash_count <= 6 and len(first_line) > hash_count and first_line[hash_count] == " ":
            return BlockType.HEADING

    # Code block: starts and ends with ```
    if block.startswith("```") and block.endswith("```") and "\n" in block:
        return BlockType.CODE

    # Quote: every line starts with >
    if all(line.lstrip().startswith(">") for line in lines):
        return BlockType.QUOTE

    # Unordered list: every line starts with - followed by space
    if all(line.lstrip().startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    # Ordered list: starts with 1. , 2. , 3. , etc.
    if first_line.lstrip().startswith("1. "):
        is_ordered = True
        expected = 1
        for line in lines:
            stripped = line.lstrip()
            if not stripped.startswith(f"{expected}. "):
                is_ordered = False
                break
            expected += 1
        if is_ordered:
            return BlockType.ORDERED_LIST

    # Default: paragraph
    return BlockType.PARAGRAPH


# ──────────────────────────────────────────────────────────────
# Helper: convert inline text → list of HTMLNodes
# ──────────────────────────────────────────────────────────────

def text_to_children(text: str) -> list[HTMLNode]:
    """
    Convert a string with inline markdown into list of HTMLNodes.
    This is used for paragraph, heading, list items, quotes, etc.
    """
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]


# ──────────────────────────────────────────────────────────────
# Block type → HTMLNode converters
# ──────────────────────────────────────────────────────────────

def paragraph_to_html_node(block: str) -> ParentNode:
    """Paragraph block → <p> with inline children"""
    # Replace internal newlines with spaces
    text = " ".join(block.splitlines())
    children = text_to_children(text)
    return ParentNode("p", children)


def heading_to_html_node(block: str) -> ParentNode:
    """Heading block → <h1> to <h6>"""
    # Count # symbols
    hash_count = 0
    while hash_count < len(block) and block[hash_count] == "#":
        hash_count += 1
    
    # Get text after # and space
    text = block[hash_count + 1:].strip()
    children = text_to_children(text)
    
    return ParentNode(f"h{hash_count}", children)


def code_to_html_node(block: str) -> ParentNode:
    """Code block → <pre><code> with raw text (no inline parsing)"""
    # Remove opening and closing ```
    code_content = block[3:-3].strip("\n")
    
    # Create plain text node
    text_node = TextNode(code_content, TextType.TEXT)
    code_child = text_node_to_html_node(text_node)
    
    code_node = ParentNode("code", [code_child])
    pre_node = ParentNode("pre", [code_node])
    
    return pre_node


def quote_to_html_node(block: str) -> ParentNode:
    """Quote block → <blockquote>"""
    # Remove > from each line
    cleaned_lines = []
    for line in block.splitlines():
        cleaned = line.lstrip(">").strip()
        if cleaned:
            cleaned_lines.append(cleaned)
    
    text = " ".join(cleaned_lines)
    children = text_to_children(text)
    
    return ParentNode("blockquote", children)


def unordered_list_to_html_node(block: str) -> ParentNode:
    """Unordered list → <ul> with <li> children"""
    items = []
    for line in block.splitlines():
        content = line.lstrip("-").strip()
        if content:
            li_children = text_to_children(content)
            items.append(ParentNode("li", li_children))
    
    return ParentNode("ul", items)


def ordered_list_to_html_node(block: str) -> ParentNode:
    """Ordered list → <ol> with <li> children"""
    items = []
    for line in block.splitlines():
        # Find position after the number and dot
        dot_pos = line.find(". ")
        if dot_pos != -1:
            content = line[dot_pos + 2:].strip()
            if content:
                li_children = text_to_children(content)
                items.append(ParentNode("li", li_children))
    
    return ParentNode("ol", items)


# ──────────────────────────────────────────────────────────────
# Main function – ties everything together
# ──────────────────────────────────────────────────────────────

def markdown_to_html_node(markdown: str) -> ParentNode:
    """
    Convert full markdown document to one big <div> containing all blocks.
    """
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.PARAGRAPH:
            node = paragraph_to_html_node(block)
        elif block_type == BlockType.HEADING:
            node = heading_to_html_node(block)
        elif block_type == BlockType.CODE:
            node = code_to_html_node(block)
        elif block_type == BlockType.QUOTE:
            node = quote_to_html_node(block)
        elif block_type == BlockType.UNORDERED_LIST:
            node = unordered_list_to_html_node(block)
        elif block_type == BlockType.ORDERED_LIST:
            node = ordered_list_to_html_node(block)
        else:
            raise ValueError(f"Unknown block type for block:\n{block}")

        children.append(node)

    # Wrap everything in a <div>
    return ParentNode("div", children=children)