from notionary import NotionDatabase

async def main():
    db = await NotionDatabase.from_database_name("Snipd Database")
    
    pages = await db.get_all_pages()
    
    
    print(f"Total pages in database: {len(pages)}")
    for i, page in enumerate(pages, 1):
        print(f"{i:3d}. {page.title} (ID: {page.id})")
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())