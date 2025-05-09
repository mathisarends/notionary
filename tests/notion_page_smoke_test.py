import asyncio
import os
import random
import pytest
from dotenv import load_dotenv
from typing import List

from notionary.page.notion_page import NotionPage

load_dotenv()


@pytest.mark.asyncio
class TestNotionPageSmoke:
    """Smoke tests for NotionPage class."""

    PAGE_NAME = "Smoke Test Page"
    
    # Some test data
    TEST_EMOJI = ["🔥", "🚀", "✅", "📝", "🧠"]
    TEST_COVER_URL = "https://images.unsplash.com/photo-1518655048521-f130df041f66"
    
    @classmethod
    def setup_class(cls):
        """Set up the test environment."""
        cls.token = os.getenv("NOTION_SECRET")
        if not cls.token:
            pytest.skip("NOTION_TOKEN environment variable not set")
    
    async def test_page_creation_from_name(self):
        """Test creating a NotionPage from page name."""
        page = await NotionPage.from_page_name(self.PAGE_NAME, self.token)
        assert page is not None
        assert page.id is not None
        
        # Store the page ID for other tests
        TestNotionPageSmoke.page_id = page.id
        
        print(f"✅ Found: \"{self.PAGE_NAME}\" 📝 → {await page.get_url()}")
        return page
    
    async def test_page_from_id(self):
        """Test creating a NotionPage from ID."""
        # First ensure we have a page ID
        if not hasattr(TestNotionPageSmoke, 'page_id'):
            page = await self.test_page_creation_from_name()
            TestNotionPageSmoke.page_id = page.id
            
        # Create page from ID
        page_from_id = NotionPage.from_page_id(TestNotionPageSmoke.page_id, self.token)
        assert page_from_id is not None
        assert page_from_id.id == TestNotionPageSmoke.page_id
        
        # Verify title
        title = await page_from_id.get_title()
        assert title == self.PAGE_NAME
    
    async def test_page_from_url(self):
        """Test creating a NotionPage from URL."""
        # First ensure we have a page
        if not hasattr(TestNotionPageSmoke, 'page_id'):
            page = await self.test_page_creation_from_name()
        else:
            page = NotionPage.from_page_id(TestNotionPageSmoke.page_id, self.token)
            
        # Get page URL
        url = await page.get_url()
        
        # Create a new page instance from that URL
        page_from_url = NotionPage.from_url(url, self.token)
        assert page_from_url is not None
        assert page_from_url.id == page.id
        
        # Verify title
        title = await page_from_url.get_title()
        assert title == self.PAGE_NAME
    
    async def test_get_title(self):
        """Test retrieving the page title."""
        page = await self._get_test_page()
        title = await page.get_title()
        assert title is not None
        assert isinstance(title, str)
        assert title == self.PAGE_NAME
        print(f"Page title: {title}")
    
    async def test_set_title(self):
        """Test setting the page title."""
        page = await self._get_test_page()
        original_title = await page.get_title()
        
        # Set a new title
        new_title = f"Smoke Test Page {random.randint(1000, 9999)}"
        result = await page.set_title(new_title)
        assert result is not None
        
        # Verify the title was updated
        updated_title = await page.get_title()
        assert updated_title == new_title
        
        # Reset to original title
        await page.set_title(original_title)
    
    async def test_get_url(self):
        """Test retrieving the page URL."""
        page = await self._get_test_page()
        url = await page.get_url()
        assert url is not None
        assert url.startswith("https://")
        print(f"Page URL: {url}")
    
    async def test_content_operations(self):
        """Test content operations like append, clear, and get text content."""
        page = await self._get_test_page()
        
        # Get initial content
        initial_content = await page.get_text_content()
        print(f"Initial content length: {len(initial_content)}")
        
        # Append markdown content
        test_markdown = "## Smoke Test Heading\nThis is a smoke test for the NotionPage class."
        append_result = await page.append_markdown(test_markdown)
        assert append_result is True
        
        # Get updated content and verify it's longer
        updated_content = await page.get_text_content()
        assert len(updated_content) > len(initial_content)
        print(f"Updated content length: {len(updated_content)}")
        
        # Clear the page content
        clear_result = await page.clear_page_content()
        assert clear_result is True
        
        # Verify content is cleared
        cleared_content = await page.get_text_content()
        assert len(cleared_content) < len(updated_content)
        print(f"Cleared content length: {len(cleared_content)}")
        
        # Replace with new content
        replace_result = await page.replace_content("# Fresh Content\nThis is brand new content.")
        assert replace_result is True
    
    async def test_icon_operations(self):
        """Test icon operations."""
        page = await self._get_test_page()
        
        # Get current icon
        current_icon = await page.get_icon()
        print(f"Current icon: {current_icon}")
        
        # Set emoji icon
        emoji = random.choice(self.TEST_EMOJI)
        emoji_result = await page.set_emoji_icon(emoji)
        assert emoji_result is not None
        
        # Get updated icon
        updated_icon = await page.get_icon()
        assert updated_icon == emoji
        print(f"Updated icon: {updated_icon}")
        
        # Test external icon
        external_result = await page.set_external_icon(self.TEST_COVER_URL)
        assert external_result is not None
    
    async def test_cover_operations(self):
        """Test cover operations."""
        page = await self._get_test_page()
        
        # Get current cover
        current_cover = await page.get_cover_url()
        print(f"Current cover: {current_cover}")
        
        # Set external cover
        cover_result = await page.set_cover(self.TEST_COVER_URL)
        assert cover_result is not None
        
        # Get updated cover
        updated_cover = await page.get_cover_url()
        assert updated_cover is not None
        assert self.TEST_COVER_URL in updated_cover
        print(f"Updated cover: {updated_cover}")
        
        # Set random gradient cover
        gradient_result = await page.set_random_gradient_cover()
        assert gradient_result is not None
    
    async def test_property_operations(self):
        """Test property operations."""
        page = await self._get_test_page()
        
        # Test getting property names
        properties = await page._property_manager._get_properties()
        property_names = list(properties.keys())
        print(f"Available properties: {property_names}")
        
        if not property_names:
            print("No properties available to test")
            return
            
        # Try to find a suitable property to test with
        test_property = None
        for prop_name in property_names:
            if prop_name.lower() not in ['name', 'title', 'created', 'last edited']:
                test_property = prop_name
                break
                
        if not test_property:
            test_property = property_names[0]
        
        print(f"Testing with property: {test_property}")
        
        # Test getting property value
        property_value = await page.get_property_value_by_name(test_property)
        print(f"Property value for '{test_property}': {property_value}")
        
        # Test with a property that doesn't exist
        nonexistent_value = await page.get_property_value_by_name("NonExistentProperty")
        assert nonexistent_value is None
        
        # Test getting options for a property (only works if your page is in a database)
        try:
            options = await page.get_options_for_property(test_property)
            print(f"Options for '{test_property}': {options}")
        except Exception as e:
            print(f"Could not get options: {e}")
        
        # Test setting a property value (only attempt if we can get options)
        if property_value is not None:
            try:
                set_result = await page.set_property_value_by_name(test_property, property_value)
                print(f"Set property result: {set_result}")
            except Exception as e:
                print(f"Could not set property: {e}")
    
    async def test_relation_operations(self):
        """Test relation property operations."""
        page = await self._get_test_page()
        
        # Get relation properties from the page
        # Note: This requires your test page to have relation properties
        try:
            # Try to find a relation property
            relation_property_name = None
            
            # First check if there are any relation properties
            page_properties = await page._property_manager._get_properties()
            for prop_name, prop_data in page_properties.items():
                if prop_data.get("type") == "relation":
                    relation_property_name = prop_name
                    break
            
            if relation_property_name:
                print(f"Found relation property: {relation_property_name}")
                
                # Get current relation values
                relation_values = await page.get_relation_property_values_by_name(relation_property_name)
                print(f"Current relation values: {relation_values}")
                
                # Get relation options
                relation_options = await page.get_options_for_property(relation_property_name)
                if relation_options:
                    # Take up to 2 options to relate to
                    page_titles_to_relate = relation_options[:2]
                    print(f"Will try to relate to: {page_titles_to_relate}")
                    
                    # Set relation values
                    set_result = await page.set_relation_property_values_by_name(
                        relation_property_name, page_titles_to_relate
                    )
                    print(f"Set relation result: {set_result}")
                    
                    # Get updated relation values
                    updated_values = await page.get_relation_property_values_by_name(relation_property_name)
                    print(f"Updated relation values: {updated_values}")
                else:
                    print("No relation options found to test with")
            else:
                print("No relation properties found to test with")
                
        except Exception as e:
            print(f"Error testing relation operations: {e}")
    
    async def test_get_formatting_prompt(self):
        """Test getting the formatting prompt."""
        page = await self._get_test_page()
        prompt = page.get_formatting_prompt()
        assert prompt is not None
        assert isinstance(prompt, str)
        print(f"Formatting prompt length: {len(prompt)}")
    
    async def test_get_last_edit_time(self):
        """Test getting the last edit time."""
        page = await self._get_test_page()
        last_edit_time = await page.get_last_edit_time()
        assert last_edit_time is not None
        print(f"Last edit time: {last_edit_time}")
    
    async def _get_test_page(self):
        """Helper method to get the test page."""
        if hasattr(TestNotionPageSmoke, 'page_id'):
            return NotionPage.from_page_id(TestNotionPageSmoke.page_id, self.token)
        else:
            page = await self.test_page_creation_from_name()
            TestNotionPageSmoke.page_id = page.id
            return page


def run_tests():
    """Run all the smoke tests."""
    asyncio.run(run_all_tests())


async def run_all_tests():
    """Run all tests asynchronously."""
    test_instance = TestNotionPageSmoke()
    
    # Setup
    TestNotionPageSmoke.setup_class()
    
    tests = [
        test_instance.test_page_creation_from_name,
        test_instance.test_page_from_id,
        test_instance.test_page_from_url,
        test_instance.test_get_title,
        test_instance.test_set_title,
        test_instance.test_get_url,
        test_instance.test_content_operations,
        test_instance.test_icon_operations,
        test_instance.test_cover_operations,
        test_instance.test_property_operations,
        test_instance.test_relation_operations,
        test_instance.test_get_formatting_prompt,
        test_instance.test_get_last_edit_time,
    ]
    
    success_count = 0
    
    for i, test in enumerate(tests):
        test_name = test.__name__
        try:
            print(f"\n[{i+1}/{len(tests)}] Running {test_name}...")
            await test()
            print(f"✅ {test_name} passed!")
            success_count += 1
        except Exception as e:
            print(f"\n❌ {test_name} failed: {e}")
    
    print(f"\nTest summary: {success_count}/{len(tests)} tests passed.")


if __name__ == "__main__":
    run_tests()