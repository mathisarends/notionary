import asyncio
import os
import pytest
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

from notionary.database.notion_database import NotionDatabase
from notionary.page.notion_page import NotionPage

# Load environment variables (ensure NOTION_TOKEN is set)
load_dotenv()


@pytest.mark.asyncio
class TestNotionDatabaseSmoke:
    """Smoke tests for NotionDatabase class."""

    DATABASE_NAME = "Wissen & Notizen"

    @classmethod
    def setup_class(cls):
        """Set up the test environment."""
        cls.token = os.getenv("NOTION_SECRET")
        if not cls.token:
            pytest.skip("NOTION_TOKEN environment variable not set")

    async def test_database_creation_from_name(self):
        """Test creating a NotionDatabase from database name."""
        database = await NotionDatabase.from_database_name(
            self.DATABASE_NAME, self.token
        )
        assert database is not None
        assert database.database_id is not None

        # Store the database ID for other tests
        TestNotionDatabaseSmoke.database_id = database.database_id

        print(
            f'✅ Found: "{self.DATABASE_NAME}" 📊 → Database ID: {database.database_id}'
        )
        return database

    async def test_database_from_id(self):
        """Test creating a NotionDatabase from ID."""
        # First ensure we have a database ID
        if not hasattr(TestNotionDatabaseSmoke, "database_id"):
            database = await self.test_database_creation_from_name()
            TestNotionDatabaseSmoke.database_id = database.database_id

        # Create database from ID
        database_from_id = await await NotionDatabase.from_database_id(
            TestNotionDatabaseSmoke.database_id, self.token
        )
        assert database_from_id is not None
        assert database_from_id.database_id == TestNotionDatabaseSmoke.database_id

    async def test_create_blank_page(self):
        """Test creating a blank page in the database."""
        database = await self._get_test_database()

        # Create a blank page
        new_page = await database.create_blank_page()
        assert new_page is not None
        assert new_page.id is not None

        # Store the page ID for later tests
        TestNotionDatabaseSmoke.test_page_id = new_page.id

        print(f"✅ Created blank page with ID: {new_page.id}")

        # Verify the page exists
        page_title = await new_page.get_title()
        print(f"New page title: {page_title}")

        return new_page

    async def test_get_pages(self):
        """Test retrieving pages from the database."""
        database = await self._get_test_database()

        # Get a small number of pages to test
        limit = 5
        pages = await database.get_pages(limit=limit)

        # Verify we got pages
        assert pages is not None
        print(f"Retrieved {len(pages)} pages from database")

        # Print titles of retrieved pages
        for i, page in enumerate(pages[:3]):  # Show max 3 pages
            title = await page.get_title()
            print(f"  Page {i+1}: {title} (ID: {page.id})")

        if len(pages) > 3:
            print(f"  ... and {len(pages) - 3} more pages")

    async def test_iter_pages(self):
        """Test iterating through pages in the database."""
        database = await self._get_test_database()

        # Count pages using iterator
        count = 0
        async for page in database.iter_pages(page_size=10):
            count += 1
            if count <= 3:  # Show max 3 pages
                title = await page.get_title()
                print(f"  Iterated page {count}: {title} (ID: {page.id})")

            # Limit to 10 pages for testing
            if count >= 10:
                break

        print(f"Iterated through {count} pages")
        assert count > 0, "Should find at least one page in the database"

    async def test_filter_pages(self):
        """Test filtering pages in the database."""
        database = await self._get_test_database()

        # Create a simple filter condition - this is just an example
        # You may need to adjust to match properties in your test database
        filter_condition = {"property": "Name", "title": {"is_not_empty": True}}

        # Get filtered pages
        filtered_pages = await database.get_pages(
            limit=5, filter_conditions=filter_condition
        )

        print(f"Retrieved {len(filtered_pages)} filtered pages")
        assert len(filtered_pages) > 0, "Filter should return at least one page"

        # Print titles of filtered pages
        for i, page in enumerate(filtered_pages[:3]):  # Show max 3 pages
            title = await page.get_title()
            print(f"  Filtered page {i+1}: {title}")

    async def test_sort_pages(self):
        """Test sorting pages in the database."""
        database = await self._get_test_database()

        # Create a sort instruction - this is just an example
        # You may need to adjust to match properties in your test database
        sorts = [{"property": "Name", "direction": "ascending"}]

        # Get sorted pages
        sorted_pages = await database.get_pages(limit=5, sorts=sorts)

        print(f"Retrieved {len(sorted_pages)} sorted pages")
        assert len(sorted_pages) > 0, "Sort should return at least one page"

        # Print titles of sorted pages
        for i, page in enumerate(sorted_pages[:3]):  # Show max 3 pages
            title = await page.get_title()
            print(f"  Sorted page {i+1}: {title}")

    async def test_archive_page(self):
        """Test archiving a page."""
        # Skip if we haven't created a test page
        if not hasattr(TestNotionDatabaseSmoke, "test_page_id"):
            test_page = await self.test_create_blank_page()
            TestNotionDatabaseSmoke.test_page_id = test_page.id

        database = await self._get_test_database()

        # Archive the test page
        result = await database.archive_page(TestNotionDatabaseSmoke.test_page_id)
        assert result is True, "Archive operation should succeed"
        print(
            f"✅ Successfully archived page with ID: {TestNotionDatabaseSmoke.test_page_id}"
        )

    async def test_get_last_edited_time(self):
        """Test getting the last edited time of the database."""
        database = await self._get_test_database()

        last_edited_time = await database.get_last_edited_time()
        assert last_edited_time is not None
        print(f"Database last edited time: {last_edited_time}")

    async def _get_test_database(self):
        """Helper method to get the test database."""
        if hasattr(TestNotionDatabaseSmoke, "database_id"):
            return await await NotionDatabase.from_database_id(
                TestNotionDatabaseSmoke.database_id, self.token
            )
        else:
            database = await self.test_database_creation_from_name()
            TestNotionDatabaseSmoke.database_id = database.database_id
            return database


def run_tests():
    """Run all the smoke tests."""
    asyncio.run(run_all_tests())


async def run_all_tests():
    """Run all tests asynchronously."""
    test_instance = TestNotionDatabaseSmoke()

    # Setup
    TestNotionDatabaseSmoke.setup_class()

    tests = [
        test_instance.test_database_creation_from_name,
        test_instance.test_database_from_id,
        test_instance.test_create_blank_page,
        test_instance.test_get_pages,
        test_instance.test_iter_pages,
        test_instance.test_filter_pages,
        test_instance.test_sort_pages,
        test_instance.test_get_last_edited_time,
        test_instance.test_archive_page,  # Run this last since it archives a page
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
            import traceback

            traceback.print_exc()

    print(f"\nTest summary: {success_count}/{len(tests)} tests passed.")

    # Close the database connection at the end
    if hasattr(TestNotionDatabaseSmoke, "database_id"):
        database = await await NotionDatabase.from_database_id(
            TestNotionDatabaseSmoke.database_id, test_instance.token
        )
        await database.close()
        print("Database connection closed.")


if __name__ == "__main__":
    run_tests()
