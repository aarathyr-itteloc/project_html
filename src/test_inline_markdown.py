import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "`", TextType.CODE),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "**", TextType.BOLD),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_italic(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "_", TextType.ITALIC),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_multiple_delimited_sections(self):
        node = TextNode("`a` and `b` and `c`", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "`", TextType.CODE),
            [
                TextNode("a", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("b", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("c", TextType.CODE),
            ],
        )

    def test_delimiter_at_start(self):
        node = TextNode("**bold** at the start", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "**", TextType.BOLD),
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" at the start", TextType.TEXT),
            ],
        )

    def test_delimiter_at_end(self):
        node = TextNode("at the end `code`", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "`", TextType.CODE),
            [
                TextNode("at the end ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
        )

    def test_whole_text_delimited(self):
        node = TextNode("`only code`", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "`", TextType.CODE),
            [TextNode("only code", TextType.CODE)],
        )

    def test_no_delimiter(self):
        node = TextNode("plain text", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "`", TextType.CODE),
            [TextNode("plain text", TextType.TEXT)],
        )

    def test_empty_list(self):
        self.assertEqual(split_nodes_delimiter([], "`", TextType.CODE), [])

    def test_non_text_nodes_unchanged(self):
        nodes = [
            TextNode("already **bold**", TextType.BOLD),
            TextNode("code", TextType.CODE),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(split_nodes_delimiter(nodes, "**", TextType.BOLD), nodes)

    def test_multiple_input_nodes(self):
        nodes = [
            TextNode("one `a` two", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("three `b`", TextType.TEXT),
        ]
        self.assertEqual(
            split_nodes_delimiter(nodes, "`", TextType.CODE),
            [
                TextNode("one ", TextType.TEXT),
                TextNode("a", TextType.CODE),
                TextNode(" two", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode("three ", TextType.TEXT),
                TextNode("b", TextType.CODE),
            ],
        )

    def test_unmatched_delimiter_raises(self):
        node = TextNode("This is `broken text", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_unmatched_bold_raises(self):
        node = TextNode("This is **broken text", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_three_delimiters_raises(self):
        node = TextNode("`a` and `b", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_chained_delimiters(self):
        node = TextNode("A **bold**, an _italic_ and `code`", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            nodes,
            [
                TextNode("A ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(", an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
        )

    def test_does_not_modify_input(self):
        node = TextNode("a `b` c", TextType.TEXT)
        original = [node]
        split_nodes_delimiter(original, "`", TextType.CODE)
        self.assertEqual(original, [TextNode("a `b` c", TextType.TEXT)])

class TestExtractMarkdown(unittest.TestCase):
    # --- immagini ---
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = (
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) "
            "and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            extract_markdown_images(text),
        )

    def test_extract_image_empty_alt(self):
        self.assertListEqual(
            [("", "https://i.imgur.com/zjjcJKZ.png")],
            extract_markdown_images("![](https://i.imgur.com/zjjcJKZ.png)"),
        )

    def test_extract_images_no_match(self):
        self.assertListEqual([], extract_markdown_images("just plain text"))

    def test_images_ignore_links(self):
        text = "a [link](https://www.boot.dev) and no images"
        self.assertListEqual([], extract_markdown_images(text))

    # --- link ---
    def test_extract_markdown_links(self):
        text = (
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            extract_markdown_links(text),
        )

    def test_links_ignore_images(self):
        text = "![image](https://i.imgur.com/zjjcJKZ.png) and [link](https://www.boot.dev)"
        self.assertListEqual(
            [("link", "https://www.boot.dev")], extract_markdown_links(text)
        )

    def test_extract_links_no_match(self):
        self.assertListEqual([], extract_markdown_links("just plain text"))

    def test_mixed_images_and_links(self):
        text = "[a](https://a.com) ![b](https://b.com/b.png) [c](https://c.com)"
        self.assertListEqual(
            [("b", "https://b.com/b.png")], extract_markdown_images(text)
        )
        self.assertListEqual(
            [("a", "https://a.com"), ("c", "https://c.com")],
            extract_markdown_links(text),
        )

if __name__ == "__main__":
    unittest.main()
