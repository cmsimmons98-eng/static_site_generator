import unittest

from htmlnode import HTMLNode
from htmlnode import LeafNode
from htmlnode import ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_basic(self):
        node = HTMLNode(
            props={"href": "https://www.google.com", "target": "_blank"}
        )
        result = node.props_to_html()
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(result, expected)

    def test_props_to_html_empty_or_none(self):
        node1 = HTMLNode()  # all None
        node2 = HTMLNode(props={})  # empty dict
        
        self.assertEqual(node1.props_to_html(), "")
        self.assertEqual(node2.props_to_html(), "")

    def test_props_to_html_single_prop(self):
        node = HTMLNode(props={"class": "highlight"})
        result = node.props_to_html()
        expected = ' class="highlight"'
        self.assertEqual(result, expected)

    def test_repr_shows_useful_info(self):
        child = HTMLNode(value="some text")
        node = HTMLNode(
            tag="div",
            children=[child, child],
            props={"id": "main", "class": "container"}
        )
        
        repr_str = repr(node)
        self.assertIn("tag='div'", repr_str)
        self.assertIn("children_count=2", repr_str)
        self.assertIn("props={'id': 'main', 'class': 'container'}", repr_str)

    # ── LeafNode tests ─────────────────────────────────────────────

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode(
            tag="a",
            value="Click me!",
            props={"href": "https://www.boot.dev", "target": "_blank"}
        )
        expected = '<a href="https://www.boot.dev" target="_blank">Click me!</a>'
        self.assertEqual(node.to_html(), expected)

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(tag=None, value="Just some raw text")
        self.assertEqual(node.to_html(), "Just some raw text")

    def test_leaf_to_html_bold(self):
        node = LeafNode("b", "this should be bold")
        self.assertEqual(node.to_html(), "<b>this should be bold</b>")

    def test_leaf_to_html_code(self):
        node = LeafNode("code", "print('hello')")
        self.assertEqual(node.to_html(), "<code>print('hello')</code>")

    def test_leaf_raises_without_value(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None)  # should fail immediately in __init__

    # ── ParentNode tests ───────────────────────────────────────────

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild = LeafNode("b", "grandchild")
        child = ParentNode("span", [grandchild])
        parent = ParentNode("div", [child])
        expected = "<div><span><b>grandchild</b></span></div>"
        self.assertEqual(parent.to_html(), expected)

    def test_to_html_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, " normal text "),
                LeafNode("i", "italic text"),
                LeafNode(None, " more normal text"),
            ]
        )
        expected = "<p><b>Bold text</b> normal text <i>italic text</i> more normal text</p>"
        self.assertEqual(node.to_html(), expected)

    def test_to_html_nested_parents(self):
        inner = ParentNode("ul", [
            LeafNode("li", "Item 1"),
            LeafNode("li", "Item 2"),
        ])
        outer = ParentNode("div", [
            LeafNode("h1", "Title"),
            inner,
            LeafNode("p", "Footer text")
        ])
        expected = (
            "<div><h1>Title</h1>"
            "<ul><li>Item 1</li><li>Item 2</li></ul>"
            "<p>Footer text</p></div>"
        )
        self.assertEqual(outer.to_html(), expected)

    def test_parent_raises_no_tag(self):
        with self.assertRaises(ValueError):
            ParentNode(None, [LeafNode("span", "hi")])

    def test_parent_raises_no_children(self):
        with self.assertRaises(ValueError):
            ParentNode("div", None)  # None is not allowed (empty list [] would be ok)


if __name__ == "__main__":
    unittest.main()
