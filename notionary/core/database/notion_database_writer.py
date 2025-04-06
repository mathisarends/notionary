from typing import Any, Dict, List, Optional, Union
from notionary.core.database.notion_database_manager import NotionDatabaseManager
from notionary.core.notion_client import NotionClient
from notionary.core.page.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin


class NotionRelationHandler(LoggingMixin):
    """
    Handler for managing relations in Notion databases.
    Provides a unified interface for working with relations.
    """
    def __init__(self, client: NotionClient, db_manager: NotionDatabaseManager):
        self._client = client
        self._db_manager = db_manager
        self._formatter = NotionPropertyFormatter()
    
    async def find_relation_by_title(self, database_id: str, relation_prop_name: str, title: str) -> Optional[str]:
        """
        Finds a relation ID based on the title of the entry in the target database.
        """
        target_db_id = await self._db_manager.get_relation_database_id(database_id, relation_prop_name)
        if not target_db_id:
            self.logger.error("No target database found for relation '%s' in database %s", relation_prop_name, database_id)
            return None
            
        options = await self._db_manager.get_relation_options(database_id, relation_prop_name)
        
        for option in options:
            if option["title"].lower() == title.lower():
                self.logger.debug("Relation entry '%s' found: %s", title, option['id'])
                return option["id"]
                
        self.logger.warning("Relation entry '%s' not found", title)
        return None
    
    async def _get_title_properties(self, database_id: str, title: str) -> Optional[Dict[str, Any]]:
        """
        Determines the title property for a database and formats the value.
        """
        properties = await self._db_manager.get_database_properties(database_id)
        
        title_prop_name = None
        for name, prop_info in properties.items():
            if prop_info.get("type") == "title":
                title_prop_name = name
                break
                
        if not title_prop_name:
            self.logger.error("No title property found in database %s", database_id)
            return None
            
        formatted_title = self._formatter.format_value("title", title)
        if not formatted_title:
            self.logger.error("Could not format title '%s'", title)
            return None
            
        return {title_prop_name: formatted_title}


class DatabaseWritter(LoggingMixin):
    """
    Enhanced class for creating and updating pages in Notion databases.
    Supports both simple properties and relations.
    """
    
    def __init__(self, client: NotionClient, db_manager: NotionDatabaseManager = None):
        self._client = client
        self._formatter = NotionPropertyFormatter()
        self._db_manager = db_manager or NotionDatabaseManager(client)
        self._relation_handler = NotionRelationHandler(client, self._db_manager)
    
    async def create_page(self, database_id: str, properties: Dict[str, Any], 
                         relations: Dict[str, Union[str, List[str]]] = None) -> Optional[Dict[str, Any]]:
        """
        Creates a new page in a database with support for relations.
        """
        formatted_props = await self._format_properties(database_id, properties)
        if not formatted_props:
            return None
            
        if relations:
            relation_props = await self._process_relations(database_id, relations)
            if relation_props:
                formatted_props.update(relation_props)
            
        data = {
            "parent": {"database_id": database_id},
            "properties": formatted_props
        }
            
        result = await self._client.post("pages", data)
        if not result:
            self.logger.error("Error creating page in database %s", database_id)
            return None
            
        self.logger.info("Page successfully created in database %s", database_id)
        return result
    
    async def update_page(self, page_id: str, properties: Dict[str, Any] = None,
                         relations: Dict[str, Union[str, List[str]]] = None) -> Optional[Dict[str, Any]]:
        """
        Updates a page with support for relations.
        """
        page_data = await self._client.get(f"pages/{page_id}")
        if not page_data or "parent" not in page_data or "database_id" not in page_data["parent"]:
            self.logger.error("Could not determine database ID for page %s", page_id)
            return None
            
        database_id = page_data["parent"]["database_id"]
        
        if not properties and not relations:
            self.logger.warning("No properties or relations specified for update")
            return page_data
            
        update_props = {}
        
        if properties:
            formatted_props = await self._format_properties(database_id, properties)
            if formatted_props:
                update_props.update(formatted_props)
                
        if relations:
            relation_props = await self._process_relations(database_id, relations)
            if relation_props:
                update_props.update(relation_props)
                
        if not update_props:
            self.logger.warning("No valid properties to update for page %s", page_id)
            return None
            
        data = {
            "properties": update_props
        }
        
        result = await self._client.patch(f"pages/{page_id}", data)
        if not result:
            self.logger.error("Error updating page %s", page_id)
            return None
            
        self.logger.info("Page %s successfully updated", page_id)
        return result
    
    async def delete_page(self, page_id: str) -> bool:
        """
        Deletes a page (archives it in Notion).
        """
        data = {
            "archived": True
        }
        
        result = await self._client.patch(f"pages/{page_id}", data)
        if not result:
            self.logger.error("Error deleting page %s", page_id)
            return False
            
        self.logger.info("Page %s successfully deleted (archived)", page_id)
        return True
    
    async def _format_properties(self, database_id: str, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Formats properties according to their types in the database.
        """
        db_schema = await self._client.get(f"databases/{database_id}")
        if not db_schema or "properties" not in db_schema:
            self.logger.error("Could not load database schema for %s", database_id)
            return None
        
        formatted_props = {}
        
        for prop_name, value in properties.items():
            if prop_name not in db_schema["properties"]:
                self.logger.warning("Property '%s' does not exist in database %s", prop_name, database_id)
                continue
                
            prop_type = db_schema["properties"][prop_name]["type"]
            
            formatted_value = self._formatter.format_value(prop_type, value)
            if formatted_value:
                formatted_props[prop_name] = formatted_value
            else:
                self.logger.warning("Could not format value for property '%s' of type '%s'", prop_name, prop_type)
        
        return formatted_props
    
    async def _process_relations(self, database_id: str, relations: Dict[str, Union[str, List[str]]]) -> Dict[str, Any]:
        """
        Processes relation properties and converts titles to IDs.
        """
        formatted_relations = {}
        db_properties = await self._db_manager.get_database_properties(database_id)
        
        for prop_name, titles in relations.items():
            if prop_name not in db_properties:
                self.logger.warning("Property '%s' does not exist in database %s", prop_name, database_id)
                continue
                
            prop_info = db_properties[prop_name]
            if prop_info.get("type") != "relation":
                self.logger.warning("Property '%s' is not a relation (type: %s)", prop_name, prop_info.get("type"))
                continue
                
            title_list = [titles] if isinstance(titles, str) else titles
            
            relation_ids = []
            for title in title_list:
                relation_id = await self._relation_handler.find_relation_by_title(
                    database_id, prop_name, title
                )
                
                if relation_id:
                    relation_ids.append(relation_id)
                else:
                    self.logger.warning("Could not find relation ID for '%s' in '%s'", title, prop_name)
            
            if relation_ids:
                formatted_relations[prop_name] = {
                    "relation": [{"id": rel_id} for rel_id in relation_ids]
                }
        
        return formatted_relations