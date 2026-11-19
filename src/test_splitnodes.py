import unittest

from splitnodes import split_nodes_delimiter
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


if __name__ == "__main__":
    unittest.main()
