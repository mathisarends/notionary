from notionary import NotionPage
from typing import Union

from pydantic import BaseModel, Field
from langchain_core.tools import tool


class CreatePageToolArguments(BaseModel):
    """Arguments for creating a new Notion page"""

    page_name: str = Field(..., description="The name of the page to create")


@tool("create_page", args_schema=CreatePageToolArguments)
async def create_page(page_name: str) -> Union[NotionPage, str]:
    """Create a new page in Notion with the given name."""
    try:
        return await NotionPage.from_page_name(name=page_name)
    except Exception as e:
        return f"Error creating page: {str(e)}"


class ReadPageToolArguments(BaseModel):
    """Arguments for reading a Notion page"""

    page: NotionPage = Field(..., description="The Notion page to read")


@tool("read_page", args_schema=ReadPageToolArguments)
async def read_page(page: NotionPage) -> str:
    """Read the content of a Notion page."""
    try:
        return await page.get_text_content()
    except Exception as e:
        return f"Error reading page: {str(e)}"
