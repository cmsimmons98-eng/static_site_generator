import unittest

from textnode import TextNode, TextType


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


if __name__ == "__main__":
    unittest.main()
