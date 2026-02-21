from textnode import TextNode, TextType


def main():
    # Just a dummy example — we'll replace this soon with real parsing
    node = TextNode(
        "This is some anchor text",
        TextType.LINK,
        "https://www.boot.dev"
    )
    print(node)


if __name__ == "__main__":
    main()