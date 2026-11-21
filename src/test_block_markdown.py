import unittest

from block_markdown import BlockType, block_to_block_type, markdown_to_blocks


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        self.assertEqual(
            markdown_to_blocks(md),
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\n"  # noqa: ISC004
                "This is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_extra_blank_lines(self):
        self.assertEqual(markdown_to_blocks("a\n\n\n\nb\n\n"), ["a", "b"])

    def test_markdown_to_blocks_empty(self):
        self.assertEqual(markdown_to_blocks(""), [])


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph(self):
        self.assertEqual(block_to_block_type("Solo un paragrafo"), BlockType.PARAGRAPH)

    def test_multiline_paragraph(self):
        block = "prima riga\nseconda riga"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_headings_all_levels(self):
        for n in range(1, 7):
            block = "#" * n + " Titolo"
            self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_seven_hashes_is_paragraph(self):
        self.assertEqual(block_to_block_type("####### Titolo"), BlockType.PARAGRAPH)

    def test_heading_without_space_is_paragraph(self):
        self.assertEqual(block_to_block_type("#Titolo"), BlockType.PARAGRAPH)

    def test_code(self):
        block = "```\nprint('ciao')\nx = 1\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_empty(self):
        self.assertEqual(block_to_block_type("```\n```"), BlockType.CODE)

    def test_code_not_closed_is_paragraph(self):
        self.assertEqual(block_to_block_type("```\ncodice"), BlockType.PARAGRAPH)

    def test_code_single_line_is_paragraph(self):
        self.assertEqual(block_to_block_type("```codice```"), BlockType.PARAGRAPH)

    def test_quote(self):
        block = "> prima riga\n> seconda riga"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_without_space(self):
        block = ">prima\n>seconda"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_missing_marker_is_paragraph(self):
        block = "> prima riga\nseconda riga"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list(self):
        block = "- uno\n- due\n- tre"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_single_item(self):
        self.assertEqual(block_to_block_type("- uno"), BlockType.UNORDERED_LIST)

    def test_unordered_list_without_space_is_paragraph(self):
        self.assertEqual(block_to_block_type("-uno\n-due"), BlockType.PARAGRAPH)

    def test_unordered_list_mixed_is_paragraph(self):
        block = "- uno\ndue\n- tre"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list(self):
        block = "1. uno\n2. due\n3. tre"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_single_item(self):
        self.assertEqual(block_to_block_type("1. uno"), BlockType.ORDERED_LIST)

    def test_ordered_list_not_starting_at_one_is_paragraph(self):
        block = "2. due\n3. tre"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_skipped_number_is_paragraph(self):
        block = "1. uno\n3. tre"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_ten_items(self):
        block = "\n".join(f"{i}. voce" for i in range(1, 11))
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_without_space_is_paragraph(self):
        self.assertEqual(block_to_block_type("1.uno"), BlockType.PARAGRAPH)

if __name__ == "__main__":
    unittest.main()
