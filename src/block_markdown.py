from enum import Enum


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = markdown.split("\n\n")
    result: list[str] = []
    for block in blocks:
        block = block.strip()
        if block == "":
            continue
        result.append(block)
    return result

def block_to_block_type(block: str) -> BlockType:
    lines = block.split("\n")

    # Heading: 1-6 '#' followed by a space
    if block.startswith(
        ("# ", "## ", "### ", "#### ", "##### ", "###### ")
    ):
        return BlockType.HEADING

    # Code: starts with ``` + newline, ends with ```
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1] == "```":
        return BlockType.CODE

    # Quote: every line starts with '>'
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    # Unordered list: every line starts with '- '
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    # Ordered list: lines start with '1. ', '2. ', '3. ', ...
    if all(line.startswith(f"{i}. ") for i, line in enumerate(lines, start=1)):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH
