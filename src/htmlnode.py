class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: list["HTMLNode"] | None = None,
        props: dict[str, str] | None = None,
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("to_html method not implemented")

    def props_to_html(self) -> str:
        if self.props is None or len(self.props) == 0:
            return ""

        # Build strings like:  href="https://example.com" target="_blank"
        parts = []
        for key, value in self.props.items():
            parts.append(f' {key}="{value}"')

        return "".join(parts)

    def __repr__(self) -> str:
        # Make it nice to read when we print/debug
        children_count = len(self.children) if self.children else 0
        props_str = str(self.props) if self.props else "None"
        
        return (
            f"HTMLNode(tag={self.tag!r}, "
            f"value={self.value!r}, "
            f"children_count={children_count}, "
            f"props={props_str})"
        )


class LeafNode(HTMLNode):
    def __init__(
        self,
        tag: str | None,
        value: str,
        props: dict[str, str] | None = None,
    ):
        # Leaf nodes NEVER have children → we force it to None
        super().__init__(tag=tag, value=value, children=None, props=props)

        # Because value is required, we check it right away
        if value is None:
            raise ValueError("LeafNode must have a value (text content)")

    def to_html(self) -> str:
        if self.value is None:
            # This shouldn't happen because we checked in __init__,
            # but good to be defensive
            raise ValueError("LeafNode must have a value")

        if self.tag is None:
            # No tag → just return the raw text
            return self.value

        # Has a tag → build <tag props>value</tag>
        props_string = self.props_to_html() if self.props else ""
        return f"<{self.tag}{props_string}>{self.value}</{self.tag}>"

    def __repr__(self) -> str:
        # Similar to parent, but we know children=None so we skip it
        props_str = str(self.props) if self.props else "None"
        return (
            f"LeafNode(tag={self.tag!r}, "
            f"value={self.value!r}, "
            f"props={props_str})"
        )