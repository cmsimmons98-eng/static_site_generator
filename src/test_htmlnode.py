import unittest

from htmlnode import HTMLNode
from htmlnode import LeafNode


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




if __name__ == "__main__":
    unittest.main()
