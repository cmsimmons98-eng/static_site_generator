import unittest

from textnode import TextNode, TextType,text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes

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

class TestSplitNodesDelimiter(unittest.TestCase):
    
    def test_basic_bold(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_basic_italic(self):
        node = TextNode("Normal *italic* normal", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        expected = [
            TextNode("Normal ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" normal", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_code_inline(self):
        node = TextNode("Here is `print('hi')` code", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("print('hi')", TextType.CODE),
            TextNode(" code", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_no_delimiter(self):
        node = TextNode("Just plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        # Should return the original node unchanged
        self.assertEqual(new_nodes, [node])

    def test_unbalanced_delimiter(self):
        node = TextNode("This is **bold but not closed", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_multiple_delimiters_same_type(self):
        node = TextNode("One **two** three **four** end", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("One ", TextType.TEXT),
            TextNode("two", TextType.BOLD),
            TextNode(" three ", TextType.TEXT),
            TextNode("four", TextType.BOLD),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_non_text_node_unchanged(self):
        bold_node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([bold_node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [bold_node])

class TestMarkdownExtractors(unittest.TestCase):

    def test_extract_images_basic(self):
        text = "Here's a photo ![cute cat](cat.jpg) and another ![sunset](sunset.png)"
        result = extract_markdown_images(text)
        expected = [
            ("cute cat", "cat.jpg"),
            ("sunset", "sunset.png"),
        ]
        self.assertEqual(result, expected)

    def test_extract_images_with_empty_alt(self):
        text = "Image with no alt ![](empty.jpg)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("", "empty.jpg")])

    def test_extract_images_none(self):
        text = "No images here [just a link](https://example.com)"
        self.assertEqual(extract_markdown_images(text), [])

    def test_extract_links_basic(self):
        text = "Check [boot.dev](https://www.boot.dev) and [YouTube](https://youtube.com)"
        result = extract_markdown_links(text)
        expected = [
            ("boot.dev", "https://www.boot.dev"),
            ("YouTube", "https://youtube.com"),
        ]
        self.assertEqual(result, expected)

    def test_extract_links_does_not_catch_images(self):
        text = "This ![image](img.jpg) should not appear as link"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_extract_links_with_special_chars(self):
        text = "Read [my article!](https://example.com/article?lang=en&ref=bootdev)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("my article!", "https://example.com/article?lang=en&ref=bootdev")])

    def test_mixed_content(self):
        text = "See ![rickroll](rick.gif) and visit [boot.dev](https://boot.dev) now!"
        self.assertEqual(
            extract_markdown_images(text),
            [("rickroll", "rick.gif")]
        )
        self.assertEqual(
            extract_markdown_links(text),
            [("boot.dev", "https://boot.dev")]
        )

class TestSplitNodesImageAndLink(unittest.TestCase):

    # ── split_nodes_image tests ─────────────────────────────────────

    def test_split_images_basic_one_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) inside",
            TextType.TEXT
        )
        result = split_nodes_image([node])
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" inside", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_images_multiple(self):
        node = TextNode(
            "![cat](cat.jpg) before ![dog](dog.png) after",
            TextType.TEXT
        )
        result = split_nodes_image([node])
        expected = [
            TextNode("cat", TextType.IMAGE, "cat.jpg"),
            TextNode(" before ", TextType.TEXT),
            TextNode("dog", TextType.IMAGE, "dog.png"),
            TextNode(" after", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_images_at_start(self):
        node = TextNode(
            "![logo](logo.png) this is the beginning",
            TextType.TEXT
        )
        result = split_nodes_image([node])
        expected = [
            TextNode("logo", TextType.IMAGE, "logo.png"),
            TextNode(" this is the beginning", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_images_at_end(self):
        node = TextNode(
            "Text ends with image ![sunset](sunset.jpg)",
            TextType.TEXT
        )
        result = split_nodes_image([node])
        expected = [
            TextNode("Text ends with image ", TextType.TEXT),
            TextNode("sunset", TextType.IMAGE, "sunset.jpg"),
        ]
        self.assertEqual(result, expected)

    def test_split_images_no_images(self):
        node = TextNode("Just normal text [link](url.com)", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [node]  # unchanged
        self.assertEqual(result, expected)

    def test_split_images_already_image_node(self):
        node = TextNode("already image", TextType.IMAGE, "img.jpg")
        result = split_nodes_image([node])
        self.assertEqual(result, [node])  # should not touch it

    def test_split_images_empty_alt(self):
        node = TextNode("Empty alt ![](empty.png)", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [
            TextNode("Empty alt ", TextType.TEXT),
            TextNode("", TextType.IMAGE, "empty.png"),
        ]
        self.assertEqual(result, expected)

    # ── split_nodes_link tests ──────────────────────────────────────

    def test_split_links_basic(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        result = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertEqual(result, expected)

    def test_split_links_with_images_ignored(self):
        node = TextNode(
            "See ![rick roll](rick.gif) and visit [boot.dev](https://boot.dev)",
            TextType.TEXT
        )
        result = split_nodes_link([node])
        expected = [
            TextNode("See ![rick roll](rick.gif) and visit ", TextType.TEXT),
            TextNode("boot.dev", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(result, expected)

    def test_split_links_multiple(self):
        node = TextNode(
            "[Google](https://google.com) is not [DuckDuckGo](https://duckduckgo.com)",
            TextType.TEXT
        )
        result = split_nodes_link([node])
        expected = [
            TextNode("Google", TextType.LINK, "https://google.com"),
            TextNode(" is not ", TextType.TEXT),
            TextNode("DuckDuckGo", TextType.LINK, "https://duckduckgo.com"),
        ]
        self.assertEqual(result, expected)

    def test_split_links_no_links(self):
        node = TextNode("Plain text with ![image](img.jpg)", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_split_links_already_link_node(self):
        node = TextNode("already link", TextType.LINK, "https://example.com")
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_split_links_complex_url(self):
        node = TextNode(
            "Read [docs](https://example.com/docs?sort=desc&lang=en#section)",
            TextType.TEXT
        )
        result = split_nodes_link([node])
        expected = [
            TextNode("Read ", TextType.TEXT),
            TextNode("docs", TextType.LINK, "https://example.com/docs?sort=desc&lang=en#section"),
        ]
        self.assertEqual(result, expected)

    # Bonus: mixed content – apply both splitters
    def test_mixed_images_and_links(self):
        node = TextNode(
            "Click ![cat](cat.jpg) here [boot.dev](https://boot.dev) now!",
            TextType.TEXT
        )
        # First images, then links (common order)
        after_images = split_nodes_image([node])
        after_both = split_nodes_link(after_images)

        expected = [
            TextNode("Click ", TextType.TEXT),
            TextNode("cat", TextType.IMAGE, "cat.jpg"),
            TextNode(" here ", TextType.TEXT),
            TextNode("boot.dev", TextType.LINK, "https://boot.dev"),
            TextNode(" now!", TextType.TEXT),
        ]
        self.assertEqual(after_both, expected)

class TestTextToTextNodes(unittest.TestCase):

    def test_full_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
    
        nodes = text_to_textnodes(text)
    
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        
        self.assertEqual(nodes, expected)

    def test_only_plain_text(self):
        text = "Just some normal text without anything special."
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes, [TextNode(text, TextType.TEXT)])

    def test_only_bold_and_code(self):
        text = "Hello **world** this is `code` here"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Hello ", TextType.TEXT),
            TextNode("world", TextType.BOLD),
            TextNode(" this is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_image_at_beginning(self):
        text = "![cat](cat.jpg) is very cute"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("cat", TextType.IMAGE, "cat.jpg"),
            TextNode(" is very cute", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_multiple_images_and_links(self):  # or whatever the test name is
        text = "See ![sun](sun.jpg) and [Google](https://google.com) or ![moon](moon.jpg)"
        
        nodes = text_to_textnodes(text)
        
        expected = [
            TextNode("See ", TextType.TEXT),
            TextNode("sun", TextType.IMAGE, "sun.jpg"),
            TextNode(" and ", TextType.TEXT),
            TextNode("Google", TextType.LINK, "https://google.com"),
            TextNode(" or ", TextType.TEXT),
            TextNode("moon", TextType.IMAGE, "moon.jpg"),
        ]
        
        self.assertEqual(nodes, expected)


if __name__ == "__main__":
    unittest.main()
