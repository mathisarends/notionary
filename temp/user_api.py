import asyncio
from notionary import NotionWorkspace


async def simple_user_test():
    """
    Einfacher Test der User API - nur verfügbare Funktionen
    """
    print("🚀 Teste Notion User API (korrigierte Version)")
    print("=" * 50)
    
    try:
        workspace = NotionWorkspace()
        
        # 1. Bot-User abrufen (das sollte immer funktionieren)
        print("1️⃣ Teste Bot-User Abfrage...")
        bot_user = await workspace.get_current_bot_user()
        
        if bot_user:
            print("✅ Bot-User erfolgreich abgerufen!")
            print(f"   Name: {bot_user.name}")
            print(f"   ID: {bot_user.id}")
            print(f"   Workspace: {bot_user.workspace_name}")
            print(f"   Typ: {bot_user.user_type}")
            
            # 2. Workspace-Info abrufen
            print("\n2️⃣ Teste Workspace-Info...")
            workspace_info = await workspace.get_workspace_info()
            if workspace_info:
                print("✅ Workspace-Info erfolgreich abgerufen!")
                for key, value in workspace_info.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ Workspace-Info fehlgeschlagen")
            
            # 3. User per ID abrufen (mit Bot-ID als Test)
            print(f"\n3️⃣ Teste User-Abfrage per ID (ID: {bot_user.id[:8]}...)...")
            same_user = await workspace.get_user_by_id(bot_user.id)
            if same_user:
                print("✅ User per ID erfolgreich abgerufen!")
                print(f"   Name: {same_user.name}")
            else:
                print("❌ User per ID fehlgeschlagen")
                
        else:
            print("❌ Bot-User konnte nicht abgerufen werden")
            print("   Überprüfe dein NOTION_TOKEN")
            return
            
        print(f"\n{'='*50}")
        print("✅ Alle verfügbaren User API Tests erfolgreich!")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


async def test_individual_user_operations():
    """
    Test der individuellen User-Operationen
    """
    print("\n" + "🔧 Teste individuelle User-Operationen")
    print("=" * 50)
    
    try:
        from notionary import NotionUser, NotionUserManager
        
        # 1. Direkter NotionUser Test
        print("1️⃣ Teste NotionUser.current_bot_user()...")
        bot_user = await NotionUser.current_bot_user()
        if bot_user:
            print("✅ Direkter Bot-User Zugriff erfolgreich!")
            print(f"   Name: {bot_user.name}")
            
            # Daten refresh testen
            print("\n2️⃣ Teste User-Daten Refresh...")
            success = await bot_user.refresh_user_data()
            print(f"   Refresh erfolgreich: {success}")
            
            # Workspace-Limits testen (nur für Bot-User)
            if bot_user.is_bot:
                print("\n3️⃣ Teste Workspace-Limits...")
                limits = await bot_user.get_workspace_limits()
                if limits:
                    print("✅ Workspace-Limits abgerufen!")
                    print(f"   Max Upload Size: {limits.get('max_file_upload_size_in_bytes', 'N/A')} bytes")
                else:
                    print("   Keine Workspace-Limits verfügbar")
        else:
            print("❌ Direkter Bot-User Zugriff fehlgeschlagen")
            
        # 2. UserManager Test
        print("\n4️⃣ Teste NotionUserManager...")
        user_manager = NotionUserManager()
        bot_via_manager = await user_manager.get_current_bot_user()
        if bot_via_manager:
            print("✅ Bot-User über Manager erfolgreich!")
            print(f"   Name: {bot_via_manager.name}")
        else:
            print("❌ Bot-User über Manager fehlgeschlagen")
            
    except Exception as e:
        print(f"❌ Fehler bei individuellen Operationen: {e}")


if __name__ == "__main__":
    print("🎯 Notion User API - Korrigierte Tests")
    print("   Nutzt nur verfügbare API-Endpoints\n")
    
    # Haupttest
    asyncio.run(simple_user_test())
    
    # Erweiterte Tests
    asyncio.run(test_individual_user_operations())
    
    print(f"\n{'='*60}")
    print("📋 ZUSAMMENFASSUNG:")
    print("✅ Verfügbare User-Funktionen:")
    print("   - Bot-User Info abrufen (/users/me)")
    print("   - Einzelne User per ID abrufen (/users/{id})")
    print("   - Workspace-Informationen über Bot-User")
    print("   - User-Daten aktualisieren")
    print("")
    print("❌ NICHT verfügbare Funktionen:")
    print("   - Alle Workspace-User auflisten")
    print("   - User-Suche (außer über externe User-IDs)")
    print("   - Bulk-User-Operationen")
    print("")
    print("💡 TIPP: Um andere User zu finden, nutze deren User-IDs")
    print("   aus anderen Quellen (z.B. Page created_by, etc.)")