import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
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

class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_no_images(self):
        node = TextNode("Just plain text", TextType.TEXT)
        self.assertListEqual([node], split_nodes_image([node]))

    def test_empty_list(self):
        self.assertListEqual([], split_nodes_image([]))

    def test_single_image_in_middle(self):
        node = TextNode("before ![img](https://a.com/i.png) after", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("before ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://a.com/i.png"),
                TextNode(" after", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )

    def test_image_at_start(self):
        node = TextNode("![img](https://a.com/i.png) after", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("img", TextType.IMAGE, "https://a.com/i.png"),
                TextNode(" after", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )

    def test_image_at_end(self):
        node = TextNode("before ![img](https://a.com/i.png)", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("before ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://a.com/i.png"),
            ],
            split_nodes_image([node]),
        )

    def test_only_image(self):
        node = TextNode("![img](https://a.com/i.png)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("img", TextType.IMAGE, "https://a.com/i.png")],
            split_nodes_image([node]),
        )

    def test_adjacent_images(self):
        node = TextNode(
            "![one](https://a.com/1.png)![two](https://a.com/2.png)", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("one", TextType.IMAGE, "https://a.com/1.png"),
                TextNode("two", TextType.IMAGE, "https://a.com/2.png"),
            ],
            split_nodes_image([node]),
        )

    def test_empty_alt_text(self):
        node = TextNode("a ![](https://a.com/i.png) b", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("a ", TextType.TEXT),
                TextNode("", TextType.IMAGE, "https://a.com/i.png"),
                TextNode(" b", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )

    def test_non_text_nodes_untouched(self):
        bold = TextNode("![not an image](https://a.com/i.png)", TextType.BOLD)
        self.assertListEqual([bold], split_nodes_image([bold]))

    def test_multiple_nodes(self):
        nodes = [
            TextNode("a ![x](https://a.com/x.png)", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("![y](https://a.com/y.png) b", TextType.TEXT),
        ]
        self.assertListEqual(
            [
                TextNode("a ", TextType.TEXT),
                TextNode("x", TextType.IMAGE, "https://a.com/x.png"),
                TextNode("bold", TextType.BOLD),
                TextNode("y", TextType.IMAGE, "https://a.com/y.png"),
                TextNode(" b", TextType.TEXT),
            ],
            split_nodes_image(nodes),
        )

    def test_links_are_left_alone(self):
        node = TextNode(
            "a [link](https://a.com) and ![img](https://a.com/i.png)", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("a [link](https://a.com) and ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://a.com/i.png"),
            ],
            split_nodes_image([node]),
        )

    def test_same_image_twice(self):
        node = TextNode(
            "![i](https://a.com/i.png) mid ![i](https://a.com/i.png)", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("i", TextType.IMAGE, "https://a.com/i.png"),
                TextNode(" mid ", TextType.TEXT),
                TextNode("i", TextType.IMAGE, "https://a.com/i.png"),
            ],
            split_nodes_image([node]),
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev) with text that follows",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("another link", TextType.LINK, "https://blog.boot.dev"),
                TextNode(" with text that follows", TextType.TEXT),
            ],
            split_nodes_link([node]),
        )

    def test_no_links(self):
        node = TextNode("Just plain text", TextType.TEXT)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_empty_list(self):
        self.assertListEqual([], split_nodes_link([]))

    def test_link_at_start(self):
        node = TextNode("[link](https://a.com) after", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("link", TextType.LINK, "https://a.com"),
                TextNode(" after", TextType.TEXT),
            ],
            split_nodes_link([node]),
        )

    def test_link_at_end(self):
        node = TextNode("before [link](https://a.com)", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("before ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://a.com"),
            ],
            split_nodes_link([node]),
        )

    def test_only_link(self):
        node = TextNode("[link](https://a.com)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("link", TextType.LINK, "https://a.com")],
            split_nodes_link([node]),
        )

    def test_adjacent_links(self):
        node = TextNode("[one](https://a.com)[two](https://b.com)", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("one", TextType.LINK, "https://a.com"),
                TextNode("two", TextType.LINK, "https://b.com"),
            ],
            split_nodes_link([node]),
        )

    def test_non_text_nodes_untouched(self):
        code = TextNode("[link](https://a.com)", TextType.CODE)
        self.assertListEqual([code], split_nodes_link([code]))

    def test_multiple_nodes(self):
        nodes = [
            TextNode("a [x](https://a.com)", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("[y](https://b.com) b", TextType.TEXT),
        ]
        self.assertListEqual(
            [
                TextNode("a ", TextType.TEXT),
                TextNode("x", TextType.LINK, "https://a.com"),
                TextNode("bold", TextType.BOLD),
                TextNode("y", TextType.LINK, "https://b.com"),
                TextNode(" b", TextType.TEXT),
            ],
            split_nodes_link(nodes),
        )

    def test_images_are_left_alone(self):
        node = TextNode(
            "![img](https://a.com/i.png) and [link](https://b.com)", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("![img](https://a.com/i.png) and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://b.com"),
            ],
            split_nodes_link([node]),
        )

    def test_only_image_no_links(self):
        node = TextNode("![img](https://a.com/i.png)", TextType.TEXT)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_same_link_twice(self):
        node = TextNode("[a](https://a.com) mid [a](https://a.com)", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("a", TextType.LINK, "https://a.com"),
                TextNode(" mid ", TextType.TEXT),
                TextNode("a", TextType.LINK, "https://a.com"),
            ],
            split_nodes_link([node]),
        )


class TestSplitImageThenLink(unittest.TestCase):
    def test_chain_both_splitters(self):
        node = TextNode(
            "Intro ![img](https://a.com/i.png) middle [link](https://b.com) end",
            TextType.TEXT,
        )
        result = split_nodes_link(split_nodes_image([node]))
        self.assertListEqual(
            [
                TextNode("Intro ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://a.com/i.png"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://b.com"),
                TextNode(" end", TextType.TEXT),
            ],
            result,
        )

class TestTextToTextNodes(unittest.TestCase):
    def test_full_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertListEqual(
            [
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
            ],
            text_to_textnodes(text),
        )

    def test_plain_text(self):
        self.assertListEqual(
            [TextNode("Just plain text", TextType.TEXT)],
            text_to_textnodes("Just plain text"),
        )

    def test_only_bold(self):
        self.assertListEqual(
            [TextNode("bold", TextType.BOLD)],
            text_to_textnodes("**bold**"),
        )

    def test_only_italic(self):
        self.assertListEqual(
            [TextNode("italic", TextType.ITALIC)],
            text_to_textnodes("_italic_"),
        )

    def test_only_code(self):
        self.assertListEqual(
            [TextNode("code", TextType.CODE)],
            text_to_textnodes("`code`"),
        )

    def test_only_image(self):
        self.assertListEqual(
            [TextNode("img", TextType.IMAGE, "https://a.com/i.png")],
            text_to_textnodes("![img](https://a.com/i.png)"),
        )

    def test_only_link(self):
        self.assertListEqual(
            [TextNode("link", TextType.LINK, "https://a.com")],
            text_to_textnodes("[link](https://a.com)"),
        )

    def test_multiple_bold(self):
        self.assertListEqual(
            [
                TextNode("a", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("b", TextType.BOLD),
            ],
            text_to_textnodes("**a** and **b**"),
        )

    def test_bold_and_italic_adjacent(self):
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" then ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            text_to_textnodes("**bold** then _italic_"),
        )

    def test_underscore_in_url_and_code(self):
        text = "See [my link](https://a.com/my_file_name.html) and `snake_case_var` here"
        self.assertListEqual(
            [
                TextNode("See ", TextType.TEXT),
                TextNode("my link", TextType.LINK, "https://a.com/my_file_name.html"),
                TextNode(" and ", TextType.TEXT),
                TextNode("snake_case_var", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ],
            text_to_textnodes(text),
        )

    def test_underscore_in_image_url(self):
        self.assertListEqual(
            [
                TextNode("pic", TextType.IMAGE, "https://a.com/my_image_file.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            text_to_textnodes("![pic](https://a.com/my_image_file.png) and _italic_"),
        )

    def test_underscore_in_link_text(self):
        self.assertListEqual(
            [TextNode("my_link_text", TextType.LINK, "https://a.com")],
            text_to_textnodes("[my_link_text](https://a.com)"),
        )

    def test_delimiters_inside_code_stay_literal(self):
        self.assertListEqual(
            [
                TextNode("use ", TextType.TEXT),
                TextNode("**not bold** and _not italic_", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ],
            text_to_textnodes("use `**not bold** and _not italic_` here"),
        )

    def test_underscore_inside_bold(self):
        self.assertListEqual(
            [TextNode("snake_case", TextType.BOLD)],
            text_to_textnodes("**snake_case**"),
        )

    def test_adjacent_image_and_link(self):
        self.assertListEqual(
            [
                TextNode("img", TextType.IMAGE, "https://a.com/i.png"),
                TextNode("link", TextType.LINK, "https://b.com"),
            ],
            text_to_textnodes("![img](https://a.com/i.png)[link](https://b.com)"),
        )

    def test_image_not_mistaken_for_link(self):
        self.assertListEqual(
            [
                TextNode("a ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://a.com/i.png"),
                TextNode(" b ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://b.com"),
            ],
            text_to_textnodes("a ![img](https://a.com/i.png) b [link](https://b.com)"),
        )

    def test_every_type_twice(self):
        text = (
            "**b1** _i1_ `c1` ![a1](https://a.com/1.png) [l1](https://a.com/1) "
            "**b2** _i2_ `c2` ![a2](https://a.com/2.png) [l2](https://a.com/2)"
        )
        self.assertListEqual(
            [
                TextNode("b1", TextType.BOLD),
                TextNode(" ", TextType.TEXT),
                TextNode("i1", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("c1", TextType.CODE),
                TextNode(" ", TextType.TEXT),
                TextNode("a1", TextType.IMAGE, "https://a.com/1.png"),
                TextNode(" ", TextType.TEXT),
                TextNode("l1", TextType.LINK, "https://a.com/1"),
                TextNode(" ", TextType.TEXT),
                TextNode("b2", TextType.BOLD),
                TextNode(" ", TextType.TEXT),
                TextNode("i2", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("c2", TextType.CODE),
                TextNode(" ", TextType.TEXT),
                TextNode("a2", TextType.IMAGE, "https://a.com/2.png"),
                TextNode(" ", TextType.TEXT),
                TextNode("l2", TextType.LINK, "https://a.com/2"),
            ],
            text_to_textnodes(text),
        )

    def test_unclosed_bold_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("This is **broken")

    def test_unclosed_code_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("This is `broken")

    def test_unclosed_italic_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("This is _broken")

if __name__ == "__main__":
    unittest.main()
