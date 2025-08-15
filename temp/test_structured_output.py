from notionary.blocks.heading.heading_markdown_node import HeadingMarkdownBlockParams
from notionary.blocks.paragraph.paragraph_markdown_node import ParagraphMarkdownBlockParams
from notionary.blocks.bulleted_list.bulleted_list_markdown_node import BulletedListMarkdownBlockParams
from notionary.markdown.markdown_document_model import (
    MarkdownDocumentModel, 
    HeadingBlock, 
    ParagraphBlock, 
    BulletedListBlock
)


def create_minimal_test() -> MarkdownDocumentModel:
    """Super-minimaler Proof of Concept."""
    return MarkdownDocumentModel(blocks=[
        HeadingBlock(params=HeadingMarkdownBlockParams(
            text="Hello World", 
            level=1
        )),
        
        ParagraphBlock(params=ParagraphMarkdownBlockParams(
            text="This is a simple test."
        )),
        
        BulletedListBlock(params=BulletedListMarkdownBlockParams(
            texts=["Item 1", "Item 2", "Item 3"]
        ))
    ])


if __name__ == "__main__":
    # Test
    doc = create_minimal_test()
    markdown = doc.to_markdown()
    
    print("Generated Markdown:")
    print("=" * 30)
    print(markdown)
    print("=" * 30)