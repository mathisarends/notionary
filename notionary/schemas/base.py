"""
NotionContentSchema Base Class
=============================

Base class for all Notion structured output schemas with injected MarkdownBuilder
"""

from pydantic import BaseModel

from notionary.blocks.markdown.markdown_builder import MarkdownBuilder


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

            def to_notion_content(self, builder: MarkdownBuilder) -> str:
                return (builder
                    .h1(self.title)
                    .paragraph(self.introduction)
                    .h2("Key Points")
                    .bulleted_list(self.main_points)
                    .h2("Conclusion")
                    .paragraph(self.conclusion)
                    .build()
                )

        # Usage with LLM:
        llm = ChatOpenAI(model="gpt-4o")
        structured_llm = llm.with_structured_output(BlogPost)
        blog = structured_llm.invoke("Write about Python async/await")

        # Upload to Notion:
        await blog.append_to_page("My Blog")
    """

    def to_notion_content(self, builder: MarkdownBuilder) -> str:
        """
        Build Notion content using the provided MarkdownBuilder.

        Args:
            builder: Empty MarkdownBuilder instance to build content with

        Returns:
            str: The final markdown string (user should call build() on the builder)
        """
        raise NotImplementedError("Subclasses must implement to_notion_content()")

    async def append_to_page(self, title: str):
        """
        Upload this content directly to a Notion page.

        Args:
            page_name: Name of the target Notion page
        """
        from notionary import NotionPage

        # Create fresh builder and let subclass build content
        builder = MarkdownBuilder()
        markdown = self.to_notion_content(builder)

        page = await NotionPage.from_title(title)
        await page.append_markdown(markdown)
