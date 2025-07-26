from notionary.blocks.mappings.markdown_node import MarkdownNode
from notionary.blocks.mappings.heading_markdown_block import HeadingMarkdownBlock
from notionary.blocks.mappings.image_markdown_block import ImageMarkdownBlock
from notionary.blocks.mappings.paragraph_markdown_block import ParagraphMarkdownBlock

class ClassToMarkdownMapper(MarkdownNode):
    def __init__(self):
        self.children: list[MarkdownNode] = []

    def add(self, node: MarkdownNode):
        self.children.append(node)

    def to_markdown(self) -> str:
        # Zusammenfügen aller Child-Markdowns mit zwei Zeilenumbrüchen
        return "\n\n".join(child.to_markdown() for child in self.children if child is not None)


if __name__ == "__main__":
    doc = ClassToMarkdownMapper()
    doc.add(HeadingMarkdownBlock(level=1, text="Mein Titel"))
    doc.add(ParagraphMarkdownBlock("Das ist ein Absatz."))
    doc.add(ImageMarkdownBlock(url="https://example.com/image.png", caption="Ein Bild"))

    markdown_str = doc.to_markdown()
    print(markdown_str)
    
    