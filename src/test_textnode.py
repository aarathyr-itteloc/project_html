import unittest

from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
            node = TextNode("Boot.dev", TextType.LINK, "https://www.boot.dev")
            node2 = TextNode("Boot.dev", TextType.LINK, "https://www.boot.dev")
            self.assertEqual(node, node2)

    def test_url_default_is_none(self):
        node = TextNode("This is a text node", TextType.TEXT)
        self.assertIsNone(node.url)

    def test_not_eq_different_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is another text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_text_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_url(self):
        node = TextNode("Boot.dev", TextType.LINK, "https://www.boot.dev")
        node2 = TextNode("Boot.dev", TextType.LINK, "https://www.example.com")
        self.assertNotEqual(node, node2)

    def test_not_eq_url_none_vs_set(self):
        node = TextNode("Boot.dev", TextType.LINK)
        node2 = TextNode("Boot.dev", TextType.LINK, "https://www.boot.dev")
        self.assertNotEqual(node, node2)

class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertIsNone(html_node.tag)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        html_node = text_node_to_html_node(TextNode("bold", TextType.BOLD))
        self.assertEqual(html_node.to_html(), "<b>bold</b>")

    def test_italic(self):
        html_node = text_node_to_html_node(TextNode("it", TextType.ITALIC))
        self.assertEqual(html_node.to_html(), "<i>it</i>")

    def test_code(self):
        html_node = text_node_to_html_node(TextNode("x = 1", TextType.CODE))
        self.assertEqual(html_node.to_html(), "<code>x = 1</code>")

    def test_link(self):
        node = TextNode("Click", TextType.LINK, "https://boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.props, {"href": "https://boot.dev"})
        self.assertEqual(html_node.to_html(), '<a href="https://boot.dev">Click</a>')

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://x.com/a.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://x.com/a.png", "alt": "Alt text"},
        )

    def test_link_without_url_raises(self):
        with self.assertRaises(ValueError):
            text_node_to_html_node(TextNode("Click", TextType.LINK))

    def test_unknown_type_raises(self):
        node = TextNode("x", "not-a-type")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

if __name__ == "__main__":
    unittest.main()
