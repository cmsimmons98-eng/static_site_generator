from textnode import TextNode, TextType, extract_markdown_images, extract_markdown_links


def main():
    # Just a dummy example — we'll replace this soon with real parsing
    node = TextNode(
        "This is some anchor text",
        TextType.LINK,
        "https://www.boot.dev"
    )
    print(node)
    
    text = """
    This is a paragraph with ![rick roll](https://i.imgur.com/aKaOqIh.gif)
    and a [link to boot.dev](https://www.boot.dev) inside.
    """

    print("Images:", extract_markdown_images(text))
    print("Links: ", extract_markdown_links(text))


if __name__ == "__main__":
    main()