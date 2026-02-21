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

def split_nodes_image(old_nodes):
    new_nodes = []

    for old_node in old_nodes:
        # Only process TEXT nodes
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        remaining_text = old_node.text
        current_pos = 0

        while True:
            images = extract_markdown_images(remaining_text)
            if not images:
                # No (more) images → add whatever is left
                if remaining_text:
                    new_nodes.append(TextNode(remaining_text, TextType.TEXT))
                break

            # Take the first (leftmost) image
            alt_text, url = images[0]

            # The full markdown substring we want to remove
            full_match = f"![{alt_text}]({url})"

            # Find where it starts in the current remaining text
            match_start = remaining_text.find(full_match)
            if match_start == -1:
                # Should not happen if extract_markdown_images is correct
                raise ValueError("Inconsistent image extraction")

            # Text before the image
            before = remaining_text[:match_start]
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))

            # The image node itself
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))

            # Update remaining text (after this image)
            remaining_text = remaining_text[match_start + len(full_match):]

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        remaining_text = old_node.text

        while True:
            links = extract_markdown_links(remaining_text)
            if not links:
                if remaining_text:
                    new_nodes.append(TextNode(remaining_text, TextType.TEXT))
                break

            anchor_text, url = links[0]

            full_match = f"[{anchor_text}]({url})"

            match_start = remaining_text.find(full_match)
            if match_start == -1:
                raise ValueError("Inconsistent link extraction")

            before = remaining_text[:match_start]
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))

            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))

            remaining_text = remaining_text[match_start + len(full_match):]

    return new_nodes

def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    
    # Bold first (because ** contains *)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    
    # Now both *italic* and _italic_
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes
