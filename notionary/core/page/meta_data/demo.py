# Demo-Funktion
import asyncio
from notionary.core.page.meta_data.page_metadata_manager import NotionMetadataManager


async def run_demo():
    page_id = "1c8389d5-7bd3-814a-974e-f9e706569b16"
    
    manager = NotionMetadataManager(page_id=page_id)
    
    try:
        metadata = await manager.get_page_metadata()
        if not metadata:
            print("Konnte keine Metadaten abrufen.")
            return
            
        print("Verfügbare Eigenschaften:")
        for name, info in manager.cache.get_property_cache(page_id).items():
            prop_type = info.get("type")
            print(f"- {name} (Typ: {prop_type})")
        
        print("\nSetze Icon und Cover...")
        await manager.set_page_icon(emoji="🎧")
        await manager.set_page_cover("https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4")
        await manager.set_title("Soundcore Retoure")
        
        status_props = await manager.find_property_by_type("status")
        if status_props:
            status_name = status_props[0]
            valid_options = await manager.list_valid_status_options(status_name)
            
            print(f"\nVerfügbare Status-Optionen für '{status_name}':")
            for option in valid_options:
                print(f"- {option}")
            
            if valid_options:
                option_index = min(3, len(valid_options) - 1)
                status_to_set = valid_options[option_index]
                print(f"\nAktualisiere Status auf: {status_to_set}")
                await manager.update_property_by_name(status_name, status_to_set)
        
        url_props = await manager.find_property_by_type("url")
        if url_props:
            url_name = url_props[0]
            print(f"\nAktualisiere URL-Eigenschaft: {url_name}")
            await manager.update_property_by_name(url_name, "https://www.soundcore.com/updates")
        
        multi_select_props = await manager.find_property_by_type("multi_select")
        if multi_select_props:
            tags_name = multi_select_props[0]
            print(f"\nAktualisiere Tags-Eigenschaft: {tags_name}")
            await manager.update_property_by_name(tags_name, ["Kopfhörer", "Bestellung"])
        
        print("\nAktualisierung abgeschlossen!")
    
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(run_demo())