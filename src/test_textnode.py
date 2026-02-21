import unittest

from textnode import TextNode, TextType
from textnode import text_node_to_html_node

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    
    def test_eq_different_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is DIFFERENT text", TextType.BOLD)
        self.assertNotEqual(node, node2)
    
    def test_eq_different_type(self):
                node = TextNode("Same text", TextType.BOLD)
                node2 = TextNode("Same text", TextType.ITALIC)
                self.assertNotEqual(node, node2)

    def test_eq_with_url_and_without(self):
            node_with_url = TextNode("Click me", TextType.LINK, "https://boot.dev")
            node_without_url = TextNode("Click me", TextType.LINK)  # url defaults to None
            node_with_different_url = TextNode("Click me", TextType.LINK, "https://example.com")

            self.assertNotEqual(node_with_url, node_without_url)
            self.assertNotEqual(node_with_url, node_with_different_url)

            # Just to be extra sure — same everything including url
            node_same = TextNode("Click me", TextType.LINK, "https://boot.dev")
            self.assertEqual(node_with_url, node_same)

    # ── TextNode → HTMLNode conversion tests ──────────────────────

    def test_text_node_to_html_text(self):
        text_node = TextNode("plain text here", TextType.TEXT)
        html_node = text_node_to_html_node(text_node)
        self.assertIsNone(html_node.tag)
        self.assertEqual(html_node.value, "plain text here")
        self.assertIsNone(html_node.children)
        self.assertIsNone(html_node.props)

    def test_text_node_to_html_bold(self):
        text_node = TextNode("bold words", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "bold words")

    def test_text_node_to_html_link(self):
        text_node = TextNode("boot.dev", TextType.LINK, "https://www.boot.dev")
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "boot.dev")
        self.assertEqual(html_node.props, {"href": "https://www.boot.dev"})

    def test_text_node_to_html_image(self):
        text_node = TextNode("a cute cat", TextType.IMAGE, "cat.jpg")
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "cat.jpg", "alt": "a cute cat"})

    def test_text_node_to_html_invalid_type(self):
        # Simulate unknown type (you can monkey-patch or just test the error path)
        invalid_node = TextNode("oops", TextType.TEXT)  # we'll change type manually
        invalid_node.text_type = "INVALID"  # hack for test — don't do this in real code
        with self.assertRaises(ValueError):
            text_node_to_html_node(invalid_node)

if __name__ == "__main__":
    unittest.main()
