from enum import Enum
from htmlnode import LeafNode

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