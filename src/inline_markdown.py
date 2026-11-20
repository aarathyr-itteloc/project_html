import re

from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:

    new_nodes: list[TextNode]=[]

    for node in old_nodes:

        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        chunks=node.text.split(delimiter)

        if len(chunks) == 1:
            new_nodes.append(node)
            continue

        if len(chunks) % 2 == 0:
            raise ValueError (
                f"invalid Markdown syntax: unmatched delimiter "
                f"{delimiter!r} in {node.text!r}"
            )
        for i, part in enumerate(chunks):
            if part == "":
               continue
            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes

def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes: list[TextNode] = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        images = extract_markdown_images(node.text)
        if not images:
            new_nodes.append(node)
            continue

        remaining = node.text
        for image_alt, image_link in images:
            sections = remaining.split(f"![{image_alt}]({image_link})", 1)
            if len(sections) != 2:
                raise ValueError("invalid Markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_link))
            remaining = sections[1]

        if remaining != "":
            new_nodes.append(TextNode(remaining, TextType.TEXT))

    return new_nodes




def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes: list[TextNode] = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        links = extract_markdown_links(node.text)
        if not links:
            new_nodes.append(node)
            continue

        remaining = node.text
        for link_text, link_url in links:
            sections = remaining.split(f"[{link_text}]({link_url})", 1)
            if len(sections) != 2:
                raise ValueError("invalid Markdown, link section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
            remaining = sections[1]

        if remaining != "":
            new_nodes.append(TextNode(remaining, TextType.TEXT))

    return new_nodes


def text_to_textnodes(text: str) -> list[TextNode]:
    new_nodes=[TextNode(text,TextType.TEXT)]
    new_nodes=split_nodes_delimiter(new_nodes,"`",TextType.CODE)
    new_nodes=split_nodes_link(new_nodes)
    new_nodes=split_nodes_image(new_nodes)
    new_nodes=split_nodes_delimiter(new_nodes,"**",TextType.BOLD)
    new_nodes=split_nodes_delimiter(new_nodes,"_",TextType.ITALIC)
    return new_nodes
