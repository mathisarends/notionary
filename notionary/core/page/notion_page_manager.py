import asyncio
from typing import Any, Dict, List, Optional, Union
from notionary.core.converters.registry.block_element_registry import (
    BlockElementRegistry,
)
from notionary.core.converters.registry.block_element_registry_builder import (
    BlockElementRegistryBuilder,
)
from notionary.core.notion_client import NotionClient
from notionary.core.page.metadata.metadata_editor import MetadataEditor
from notionary.core.page.metadata.notion_icon_manager import NotionPageIconManager
from notionary.core.page.metadata.notion_page_cover_manager import NotionPageCoverManager
from notionary.core.page.properites.database_property_service import DatabasePropertyService
from notionary.core.page.relations.notion_page_relation_manager import NotionRelationManager
from notionary.core.page.content.page_content_manager import PageContentManager
from notionary.core.page.properites.page_property_manager import PagePropertyManager
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.page_id_utils import extract_and_validate_page_id
from notionary.core.page.relations.page_database_relation import PageDatabaseRelation

class NotionPageManager(LoggingMixin):
    """
    High-Level Facade for managing content and metadata of a Notion page.
    """

    def __init__(
        self,
        page_id: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self._page_id = extract_and_validate_page_id(page_id=page_id, url=url)

        self.url = url
        self._title = title
        self._client = NotionClient(token=token)
        self._page_data = None

        self._block_element_registry = (
            BlockElementRegistryBuilder.create_standard_registry()
        )

        self._page_content_manager = PageContentManager(
            page_id=self._page_id,
            client=self._client,
            block_registry=self._block_element_registry,
        )
        self._metadata = MetadataEditor(self._page_id, self._client)
        self._page_cover_manager = NotionPageCoverManager(page_id=self._page_id, client=self._client)
        self._page_icon_manager = NotionPageIconManager(page_id=self._page_id, client=self._client)
        
        self._db_relation = PageDatabaseRelation(page_id=self._page_id, client=self._client)
        self._db_property_service = None
        
        self._relation_manager = NotionRelationManager(page_id=self._page_id, client=self._client)
        
        self._property_manager = PagePropertyManager(
            self._page_id, 
            self._client,
            self._metadata,
            self._db_relation
        )

    async def _get_db_property_service(self) -> Optional[DatabasePropertyService]:
        """
        Gets the database property service, initializing it if necessary.
        This is a more intuitive way to work with the instance variable.
        
        Returns:
            Optional[DatabasePropertyService]: The database property service or None if not applicable
        """
        if self._db_property_service is not None:
            return self._db_property_service
            
        database_id = await self._db_relation.get_parent_database_id()
        if not database_id:
            return None
        
        self._db_property_service = DatabasePropertyService(database_id, self._client)
        await self._db_property_service.load_schema()
        return self._db_property_service

    @property
    def page_id(self) -> Optional[str]:
        """Get the ID of the page."""
        return self._page_id

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def block_registry(self) -> BlockElementRegistry:
        return self._block_element_registry

    @block_registry.setter
    def block_registry(self, block_registry: BlockElementRegistry) -> None:
        """Set the block element registry for the page content manager."""
        self._block_element_registry = block_registry
        self._page_content_manager = PageContentManager(
            page_id=self._page_id, client=self._client, block_registry=block_registry
        )

    async def append_markdown(self, markdown: str) -> str:
        return await self._page_content_manager.append_markdown(markdown)

    async def clear(self) -> str:
        return await self._page_content_manager.clear()

    async def replace_content(self, markdown: str) -> str:
        await self._page_content_manager.clear()
        return await self._page_content_manager.append_markdown(markdown)

    async def get_text(self) -> str:
        return await self._page_content_manager.get_text()
    
    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_title(title)

    async def set_page_icon(
        self, emoji: Optional[str] = None, external_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        return await self._page_icon_manager.set_icon(emoji, external_url)
    
    async def _get_page_data(self, force_refresh=False) -> Dict[str, Any]:
        """ Gets the page data and caches it for future use.
        """
        if self._page_data is None or force_refresh:
            self._page_data = await self._client.get_page(self._page_id)
        return self._page_data
    
    async def get_icon(self) -> Optional[str]:
        """Retrieves the page icon - either emoji or external URL.
        """
        return await self._page_icon_manager.get_icon()

    async def get_cover_url(self) -> str:
        return await self._page_cover_manager.get_cover_url()

    async def set_page_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        return await self._page_cover_manager.set_cover(external_url)
    
    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        return await self._page_cover_manager.set_random_gradient_cover()
    
    async def get_properties(self) -> Dict[str, Any]:
        """Retrieves all properties of the page."""
        return await self._property_manager.get_properties()

    async def get_property_value(self, property_name: str) -> Any:
        """Get the value of a specific property."""
        return await self._property_manager.get_property_value(
            property_name, 
            self._relation_manager.get_relation_values
        )
    
    async def set_property_by_name(self, property_name: str, value: Any) -> Optional[Dict[str, Any]]:
        """ Sets the value of a specific property by its name.
        """ 
        return await self._property_manager.set_property_by_name(
            property_name=property_name, 
            value=value,
        )
        
    async def is_database_page(self) -> bool:
        """ Checks if this page belongs to a database.
        """
        return await self._db_relation.is_database_page()
        
    async def get_parent_database_id(self) -> Optional[str]:
        """ Gets the ID of the database this page belongs to, if any
        """
        return await self._db_relation.get_parent_database_id()

    async def get_available_options_for_property(self, property_name: str) -> List[str]:
        """ Gets the available option names for a property (select, multi_select, status).
        """
        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_option_names(property_name)
        return []

    async def get_property_type(self, property_name: str) -> Optional[str]:
        """ Gets the type of a specific property.
        """
        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_property_type(property_name)
        return None

    async def get_database_metadata(self, include_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """ Gets complete metadata about the database this page belongs to.
        """
        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_database_metadata(include_types)
        return {"properties": {}}

    async def get_relation_options(self, property_name: str, limit: int = 100) -> List[Dict[str, Any]]:
            """ Returns available options for a relation property.
            """
            return await self._relation_manager.get_relation_options(property_name, limit)

    async def add_relations_by_name(self, relation_property_name: str, page_titles: Union[str, List[str]]) -> Optional[Dict[str, Any]]:
        """ Adds one or more relations.
        """
        return await self._relation_manager.add_relation_by_name(property_name=relation_property_name, page_titles=page_titles)

    async def get_relation_values(self, property_name: str) -> List[str]:
        """
        Returns the current relation values for a property.
        """
        return await self._relation_manager.get_relation_values(property_name)

    async def get_relation_property_ids(self) -> List[str]:
        """ Returns a list of all relation property names.
        """
        return await self._relation_manager.get_relation_property_ids()

    async def get_all_relations(self) -> Dict[str, List[str]]:
        """ Returns all relation properties and their values.
        """
        return await self._relation_manager.get_all_relations()
        
    async def get_status(self) -> Optional[str]:
        """ Determines the status of the page (e.g., 'Draft', 'Completed', etc.)
        """
        return await self.get_property_value("Status")
    
    
    
async def append_markdown_demo():
    url = "https://www.notion.so/Jarvis-Clipboard-1a3389d57bd380d7a507e67d1b25822c"
    page_manager = NotionPageManager(url=url)
    
    example_output = """!> [📚] AI Summary: Explore the fascinating connection between the nervous system and muscle movement. Discover the differences between training for hypertrophy and strength, alongside effective resistance protocols. Learn how to assess recovery with tools like heart rate variability and grip strength. Dive into the impact of key nutrients such as creatine and electrolytes on muscle performance. This discussion offers actionable strategies to enhance movement, preserve strength with age, and boost energy levels.

+++ 🎧 Audio Summary
    $[AI-generated audio summary](https://storage.googleapis.com/audio_summaries/ep_ai_summary_127d02ec-ca12-4312-a5ed-cb14b185480c.mp3)

<!-- spacer -->

## ⬆️ Key Insights
- The interplay between the nervous system and muscle fibers is critical for effective muscle contraction and movement coordination.
- Adequate nutrition, particularly protein and electrolytes, coupled with proper recovery practices, is essential for optimizing muscle growth and performance.
- Regular strength training helps offset age-related muscle decline and improves overall posture and functional movement.
- Simple tools like grip strength measurements and heart rate variability can provide valuable insights into recovery status and training readiness.

<!-- spacer -->
---

### 💪 1. Understanding Muscle Strength
- Muscles naturally weaken with age; strength training helps offset this decline and improve posture and movement.
- The *Henneman size principle* explains how our bodies efficiently recruit muscle fibers based on the weight of an object, prioritizing energy conservation.
- Neural adaptations are the primary driver of strength gains in the initial weeks of training, before hypertrophy becomes significant.
+++ Transcript
    <embed:Listen to this highlight>(https://snipd.com/snip/a1b2c3d4)
    ... "When we talk about strength training, we're primarily focusing on the neurological adaptations that occur first. What's fascinating is that during the first 4-6 weeks of a strength program, most of your strength gains come from improved neural efficiency, not muscle size. Your brain is literally learning to recruit more muscle fibers simultaneously, creating greater force output with the same muscle mass."


### 🧠 2. The Nervous System's Role
- The central nervous system coordinates which motor units are activated and in what sequence when performing movements.
- *Motor unit recruitment* follows a specific pattern that prioritizes smaller, more precise units before larger, more powerful ones.
- Fatigue can significantly impact nervous system efficiency, reducing both strength output and movement quality.
+++ Transcript
    <embed:Listen to this highlight>(https://snipd.com/snip/e5f6g7h8)
    ... "The beauty of how our nervous system works is that it's incredibly adaptive. When you're learning a new movement, your brain is creating new neural pathways. With practice, these pathways become more efficient—similar to how a path through grass becomes more defined the more it's walked on. This is why technique practice is so crucial; you're literally building the neural infrastructure for efficient movement."


### 🔬 3. Assessing Recovery Through Simple Tests
- *Heart rate variability* (HRV) is a key indicator of recovery, but can be difficult to measure accurately without specialized equipment.
- Morning grip strength is a simple, readily available test to assess whole-system recovery and inform training decisions.
- Sleep quality has a direct correlation with both HRV and grip strength measurements.
+++ Transcript
    <embed:Listen to this highlight>(https://snipd.com/snip/i9j0k1l2)
    ... "One of the simplest recovery tools you have access to is grip strength. First thing in the morning, try squeezing a hand dynamometer or even just observe how your grip feels. If it's significantly weaker than your baseline, that's often an indicator your nervous system is still fatigued. This simple test has been shown to correlate with overall systemic recovery and can help you decide whether to push hard in training or take a lighter approach that day."


### 🥗 4. Nutrition for Muscle Performance
- *Creatine monohydrate* remains one of the most well-researched and effective supplements for improving strength and power output.
- Adequate *electrolyte balance* is critical for optimal muscle contraction and preventing cramping during exercise.
- Protein timing and distribution throughout the day may be as important as total daily intake for maximizing muscle protein synthesis.
+++ Transcript
    <embed:Listen to this highlight>(https://snipd.com/snip/m3n4o5p6)
    ... "The research on creatine is remarkably consistent. A dose of 3-5 grams daily increases phosphocreatine stores in your muscles, enhancing your capacity for high-intensity, short-duration activities. What's often overlooked is how it can benefit cognitive function as well. Your brain uses a significant amount of ATP, and creatine supports that energy production. This is why some studies show improvements in cognitive tasks, particularly under sleep-deprived conditions, when supplementing with creatine."
"""
    
    await page_manager.append_markdown(markdown=example_output)

if __name__ == "__main__":
    asyncio.run(append_markdown_demo())
    print("\nDemonstration completed.")