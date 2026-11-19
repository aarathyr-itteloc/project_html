import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_multiple_props(self):
        node = HTMLNode(
            "a",
            "Link",
            None,
            {"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"',
        )

    def test_props_to_html_single_prop(self):
        node = HTMLNode("a", "Link", None, {"href": "https://www.boot.dev"})
        self.assertEqual(node.props_to_html(), ' href="https://www.boot.dev"')

    def test_props_to_html_none(self):
        node = HTMLNode("p", "Testo")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_empty_dict(self):
        node = HTMLNode("p", "Testo", None, {})
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_preserves_order(self):
        node = HTMLNode("img", "", None, {"src": "a.png", "alt": "Foto", "width": "100"})
        self.assertEqual(
            node.props_to_html(),
            ' src="a.png" alt="Foto" width="100"',
        )

    def test_constructor_defaults(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_repr(self):
        node = HTMLNode("p", "Ciao", None, {"class": "intro"})
        self.assertEqual(
            repr(node),
            "HTMLNode(tag='p', value='Ciao', children=None, props={'class': 'intro'})",
        )

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.google.com">Click me!</a>',
        )

    def test_leaf_to_html_multiple_props(self):
        node = LeafNode(
            "a",
            "Link",
            {"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.google.com" target="_blank">Link</a>',
        )

    def test_leaf_to_html_b(self):
        node = LeafNode("b", "Bold text")
        self.assertEqual(node.to_html(), "<b>Bold text</b>")

    def test_leaf_to_html_i(self):
        node = LeafNode("i", "Italic text")
        self.assertEqual(node.to_html(), "<i>Italic text</i>")

    def test_leaf_to_html_h1(self):
        node = LeafNode("h1", "Title")
        self.assertEqual(node.to_html(), "<h1>Title</h1>")

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Just raw text")
        self.assertEqual(node.to_html(), "Just raw text")

    def test_leaf_to_html_empty_props(self):
        node = LeafNode("p", "Text", {})
        self.assertEqual(node.to_html(), "<p>Text</p>")

    def test_leaf_to_html_no_value_raises(self):
        node = LeafNode("p", None)  # pyright: ignore[reportArgumentType]
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_has_no_children(self):
        node = LeafNode("p", "Hello")
        self.assertIsNone(node.children)

class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_great_grandchildren(self):
        node = ParentNode(
            "div",
            [ParentNode("section", [ParentNode("p", [LeafNode("b", "deep")])])],
        )
        self.assertEqual(
            node.to_html(),
            "<div><section><p><b>deep</b></p></section></div>",
        )

    def test_to_html_many_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold"),
                LeafNode(None, " normal "),
                LeafNode("i", "italic"),
                LeafNode(None, " end"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold</b> normal <i>italic</i> end</p>",
        )

    def test_to_html_single_text_child(self):
        node = ParentNode("p", [LeafNode(None, "solo testo")])
        self.assertEqual(node.to_html(), "<p>solo testo</p>")

    def test_to_html_with_props(self):
        node = ParentNode(
            "a",
            [LeafNode(None, "Link")],
            {"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.google.com" target="_blank">Link</a>',
        )

    def test_to_html_children_with_props(self):
        node = ParentNode(
            "div",
            [
                LeafNode("a", "Link", {"href": "https://boot.dev"}),
                LeafNode("img", "", {"src": "a.png", "alt": "Foto"}),
            ],
        )
        self.assertEqual(
            node.to_html(),
            '<div><a href="https://boot.dev">Link</a>'
            '<img src="a.png" alt="Foto"></img></div>',
        )

    def test_to_html_props_on_parent_and_nested_parent(self):
        inner = ParentNode("span", [LeafNode(None, "x")], {"class": "inner"})
        outer = ParentNode("div", [inner], {"id": "outer"})
        self.assertEqual(
            outer.to_html(),
            '<div id="outer"><span class="inner">x</span></div>',
        )

    def test_to_html_siblings_that_are_parents(self):
        node = ParentNode(
            "ul",
            [
                ParentNode("li", [LeafNode(None, "uno")]),
                ParentNode("li", [LeafNode(None, "due")]),
                ParentNode("li", [LeafNode("b", "tre")]),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<ul><li>uno</li><li>due</li><li><b>tre</b></li></ul>",
        )

    def test_to_html_mixed_leaf_and_parent_children(self):
        node = ParentNode(
            "div",
            [
                LeafNode("h1", "Titolo"),
                ParentNode("p", [LeafNode(None, "a "), LeafNode("b", "b")]),
                LeafNode(None, "fine"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<div><h1>Titolo</h1><p>a <b>b</b></p>fine</div>",
        )

    def test_to_html_empty_children_list(self):
        node = ParentNode("div", [])
        self.assertEqual(node.to_html(), "<div></div>")

    def test_to_html_empty_props(self):
        node = ParentNode("div", [LeafNode("p", "x")], {})
        self.assertEqual(node.to_html(), "<div><p>x</p></div>")

    def test_to_html_no_tag_raises(self):
        node = ParentNode(None, [LeafNode("p", "x")])  # pyright: ignore[reportArgumentType]
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_no_children_raises(self):
        node = ParentNode("div", None)  # pyright: ignore[reportArgumentType]
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_nested_child_without_value_raises(self):
        node = ParentNode("div", [ParentNode("span", [LeafNode("b", None)])])  # pyright: ignore[reportArgumentType]
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_nested_parent_without_children_raises(self):
        node = ParentNode("div", [ParentNode("span", None)])  # pyright: ignore[reportArgumentType]
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_has_no_value(self):
        node = ParentNode("div", [LeafNode("p", "x")])
        self.assertIsNone(node.value)

    def test_to_html_does_not_modify_children(self):
        children = [LeafNode("b", "x")]
        node = ParentNode("div", children)  # pyright: ignore[reportArgumentType]
        node.to_html()
        self.assertEqual(len(children), 1)

if __name__ == "__main__":
    unittest.main()
