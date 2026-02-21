from enum import Enum
from htmlnode import LeafNode
import re

class TextType(Enum):
    TEXT      = "text"        # normal plain text
    BOLD      = "bold"
    ITALIC    = "italic"
    CODE      = "code"
    LINK      = "link"
    IMAGE     = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str | None = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        
        return (self.text == other.text and
                self.text_type == other.text_type and
                self.url == other.url)

    def __repr__(self):
        url_part = f", {self.url}" if self.url is not None else ""
        return f"TextNode({self.text}, {self.text_type.value}{url_part})"


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(tag=None, value=text_node.text)

        case TextType.BOLD:
            return LeafNode(tag="b", value=text_node.text)

        case TextType.ITALIC:
            return LeafNode(tag="i", value=text_node.text)

        case TextType.CODE:
            return LeafNode(tag="code", value=text_node.text)

        case TextType.LINK:
            if text_node.url is None:
                raise ValueError("Link TextNode must have a url")
            return LeafNode(
                tag="a",
                value=text_node.text,
                props={"href": text_node.url}
            )

        case TextType.IMAGE:
            if text_node.url is None:
                raise ValueError("Image TextNode must have a url")
            return LeafNode(
                tag="img",
                value="",  # img tags are self-closing and have no inner text
                props={
                    "src": text_node.url,
                    "alt": text_node.text  # alt text comes from the "text" field
                }
            )

        case _:
            # This catches any unknown TextType (future-proofing + safety)
            raise ValueError(f"Unknown TextType: {text_node.text_type}")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Takes a list of TextNodes, finds any TEXT nodes that contain the given delimiter,
    and splits them into separate TextNodes of the specified text_type.
    
    Example:
        Input:  [TextNode("hello **world** today", TextType.TEXT)]
        delimiter: "**"
        text_type: TextType.BOLD
        Output: [
            TextNode("hello ", TextType.TEXT),
            TextNode("world", TextType.BOLD),
            TextNode(" today", TextType.TEXT)
        ]
    """
    new_nodes = []
    
    for old_node in old_nodes:
        # Only split TEXT nodes — everything else stays as-is
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        # If no delimiter at all → keep the whole node
        if delimiter not in old_node.text:
            new_nodes.append(old_node)
            continue
        
        # We have at least one delimiter → need to split
        parts = old_node.text.split(delimiter)
        
        # parts will have odd length if delimiters are balanced
        # even length → unbalanced → invalid Markdown
        if len(parts) % 2 == 0:
            raise ValueError(
                f"Invalid Markdown: unbalanced delimiter '{delimiter}' in text: "
                f"'{old_node.text}'"
            )
        
        # Now walk through the parts:
        # even indices = normal text
        # odd indices  = delimited (bold/italic/code/etc.)
        for i, part in enumerate(parts):
            if part == "":  # skip empty parts (e.g. "**" at start or double **)
                continue
                
            if i % 2 == 0:
                # normal text
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                # delimited text → new type
                new_nodes.append(TextNode(part, text_type))
    
    return new_nodes

def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    """
    Returns a list of tuples: [(alt_text, image_url), ...]
    for every Markdown image in the text: ![alt](url)
    """
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches  # already gives us list of (alt, url) tuples


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    """
    Returns a list of tuples: [(anchor_text, url), ...]
    for every Markdown link in the text: [text](url)
    IMPORTANT: excludes images (which start with !)
    """
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches