"""
NotionContentSchema Base Class
=============================

Base class for all Notion structured output schemas with consistent naming
"""

from pydantic import BaseModel
from notionary.blocks.markdown.markdown_document_model import MarkdownDocumentModel

class NotionContentSchema(BaseModel):
    """
    Base class for all Notion content schemas.

    Inherit from this and implement to_notion_content() to create
    schemas that work with LLM structured output.

    Example usage:

        class BlogPost(NotionContentSchema):
            title: str = Field(description="Catchy blog post title")
            introduction: str = Field(description="Engaging opening paragraph")
            main_points: List[str] = Field(description="3-5 key takeaways")
            conclusion: str = Field(description="Summary and call-to-action")

            def to_notion_content(self) -> MarkdownDocumentModel:
                from notionary.blocks.heading import HeadingMarkdownNode
                from notionary.blocks.paragraph import ParagraphMarkdownNode
                from notionary.blocks.bulleted_list import BulletedListMarkdownNode

                blocks = [
                    HeadingMarkdownNode(text=self.title, level=1),
                    ParagraphMarkdownNode(text=self.introduction),
                    HeadingMarkdownNode(text="Key Points", level=2),
                    BulletedListMarkdownNode(texts=self.main_points),
                    HeadingMarkdownNode(text="Conclusion", level=2),
                    ParagraphMarkdownNode(text=self.conclusion)
                ]
                return MarkdownDocumentModel(blocks=blocks)

        # Usage with LLM:
        llm = ChatOpenAI(model="gpt-4o")
        structured_llm = llm.with_structured_output(BlogPost)
        blog = structured_llm.invoke("Write about Python async/await")

        # Upload to Notion:
        await blog.append_to_page("My Blog")
    """

    def to_notion_content(self) -> MarkdownDocumentModel:
        """
        Convert this schema instance to Notion content.
        """
        raise NotImplementedError("Subclasses must implement to_notion_content()")

    async def append_to_page(self, page_name: str):
        """
        Upload this content directly to a Notion page.
        """
        from notionary import NotionPage

        page = await NotionPage.from_page_name(page_name)
        content = self.to_notion_content()
        await page.append_markdown(content)
