import asyncio
import os
import pytest
from dotenv import load_dotenv

from notionary.page.notion_page import NotionPage

# Load environment variables (ensure NOTION_TOKEN is set)
load_dotenv()


@pytest.mark.asyncio
class TestNotionPageSmoke:
    """Smoke tests for NotionPage class focusing on from_page_name functionality."""

    # The name of an existing page to test with
    TEST_PAGE_NAME = "Smoke Test Page"
    
    @classmethod
    def setup_class(cls):
        """Set up the test environment."""
        cls.token = os.getenv("NOTION_SECRET")
        if not cls.token:
            pytest.skip("NOTION_SECRET environment variable not set")
    
    async def test_from_page_name(self):
        """Test creating a NotionPage by finding a page with a matching name."""
        # Create page from name
        page = await NotionPage.from_page_name(self.TEST_PAGE_NAME, self.token)
        
        # Verify page was created
        assert page is not None
        assert page.id is not None
        print(f"Page created with ID: {page.id}")
        
        # Get and verify title
        title = await page.get_title()
        assert title is not None
        # The title might not be exactly the same as the search name due to fuzzy matching
        print(f"Page title: {title}")
        
        # Get URL
        url = await page.get_url()
        assert url is not None
        assert url.startswith("https://")
        print(f"Page URL: {url}")
        
        return page
    
    async def test_content_operations_with_named_page(self):
        """Test content operations on a page found by name."""
        page = await self.test_from_page_name()
        
        # Get initial content
        initial_content = await page.get_text_content()
        print(f"Initial content length: {len(initial_content)}")
        
        # Append markdown content
        test_markdown = "## Smoke Test for Page Found by Name\nThis is a smoke test for the NotionPage.from_page_name method."
        append_result = await page.append_markdown(test_markdown)
        assert append_result is True
        
        # Get updated content and verify it's longer
        updated_content = await page.get_text_content()
        assert len(updated_content) > len(initial_content)
        print(f"Updated content length: {len(updated_content)}")
    
    async def test_metadata_operations_with_named_page(self):
        """Test metadata operations on a page found by name."""
        page = await self.test_from_page_name()
        
        # Test icon operations
        current_icon = await page.get_icon()
        print(f"Current icon: {current_icon}")
        
        # Set emoji icon
        emoji_result = await page.set_emoji_icon("📝")
        assert emoji_result is not None
        
        # Get updated icon
        updated_icon = await page.get_icon()
        assert updated_icon == "📝"
        print(f"Updated icon: {updated_icon}")
        
        # Test cover operations
        current_cover = await page.get_cover_url()
        print(f"Current cover: {current_cover}")
        
        # Set random gradient cover
        gradient_result = await page.set_random_gradient_cover()
        assert gradient_result is not None
    
    async def test_property_operations_with_named_page(self):
        """Test property operations on a page found by name."""
        page = await self.test_from_page_name()
        
        # Get all properties and print them
        # We'll test a specific property if it exists
        # For example, if you have a "Status" property:
        property_value = await page.get_property_value("Status")
        print(f"Status property value: {property_value}")
        
        # Test with a property that doesn't exist
        nonexistent_value = await page.get_property_value("NonExistentProperty")
        assert nonexistent_value is None
        
    async def test_fuzzy_name_matching(self):
        """Test that fuzzy name matching works with slightly misspelled names."""
        # Intentionally use a slightly misspelled version of the page name
        # For example, if the page is named "Meeting Notes", try "Meeting Note"
        misspelled_name = self.TEST_PAGE_NAME[:-1]  # Remove last character
        
        # Create page from misspelled name
        page = await NotionPage.from_page_name(misspelled_name, self.token)
        
        # Verify page was created
        assert page is not None
        
        # Get and verify title
        title = await page.get_title()
        print(f"Original name: {self.TEST_PAGE_NAME}")
        print(f"Misspelled search: {misspelled_name}")
        print(f"Found page title: {title}")
        
        # The title should be similar to the original TEST_PAGE_NAME
        # This is a fuzzy match test, so we're checking the title contains most of the original name
        assert any(part in title.lower() for part in self.TEST_PAGE_NAME.lower().split())


def run_tests():
    """Run all the smoke tests."""
    asyncio.run(run_all_tests())


async def run_all_tests():
    """Run all tests asynchronously."""
    test_instance = TestNotionPageSmoke()
    
    # Setup
    TestNotionPageSmoke.setup_class()
    
    try:
        print("Testing page creation from page name...")
        await test_instance.test_from_page_name()
        
        print("\nTesting content operations with named page...")
        await test_instance.test_content_operations_with_named_page()
        
        print("\nTesting metadata operations with named page...")
        await test_instance.test_metadata_operations_with_named_page()
        
        print("\nTesting property operations with named page...")
        await test_instance.test_property_operations_with_named_page()
        
        print("\nTesting fuzzy name matching...")
        await test_instance.test_fuzzy_name_matching()
        
        print("\nAll smoke tests passed successfully! ✅")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    run_tests()