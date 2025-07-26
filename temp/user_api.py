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
                    print(
                        f"   Max Upload Size: {limits.get('max_file_upload_size_in_bytes', 'N/A')} bytes"
                    )
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


async def test_user_list_operations():
    """
    Test der neuen User-Listen Funktionen
    """
    print("\n" + "👥 Teste User-Listen Operationen")
    print("=" * 50)

    try:
        from notionary import NotionUserManager

        user_manager = NotionUserManager()

        # 1. Teste list_users (paginiert)
        print("1️⃣ Teste list_users (paginiert)...")
        users_response = await user_manager.list_users(page_size=10)

        if users_response:
            print("✅ User-Liste erfolgreich abgerufen!")
            print(f"   Anzahl Users: {len(users_response.results)}")
            print(f"   Hat mehr Seiten: {users_response.has_more}")
            print(f"   Next Cursor: {users_response.next_cursor}")

            # Zeige erste paar User
            for i, user in enumerate(users_response.results[:3]):
                print(f"   User {i+1}: {user.name} ({user.type})")
        else:
            print("❌ User-Liste konnte nicht abgerufen werden")

        # 2. Teste get_all_users
        print("\n2️⃣ Teste get_all_users...")
        all_users = await user_manager.get_all_users()

        if all_users:
            print("✅ Alle User erfolgreich abgerufen!")
            print(f"   Gesamtanzahl: {len(all_users)}")

            # User-Typen zählen
            person_count = len([u for u in all_users if u.is_person])
            bot_count = len([u for u in all_users if u.is_bot])
            print(f"   Personen: {person_count}")
            print(f"   Bots: {bot_count}")

            # Zeige erste paar User
            print("   Erste User:")
            for user in all_users[:5]:
                user_type = "👤" if user.is_person else "🤖"
                print(f"   {user_type} {user.name} ({user.user_type})")
        else:
            print("❌ Keine User gefunden oder Fehler")

        # 3. Teste get_users_by_type
        print("\n3️⃣ Teste get_users_by_type...")
        person_users = await user_manager.get_users_by_type("person")
        bot_users = await user_manager.get_users_by_type("bot")

        print(f"✅ Personen gefunden: {len(person_users)}")
        print(f"✅ Bots gefunden: {len(bot_users)}")

        # 4. Teste find_users_by_name
        if all_users and len(all_users) > 0:
            print("\n4️⃣ Teste find_users_by_name...")

            # Suche nach dem ersten User-Namen (teilweise)
            first_user_name = all_users[0].name
            if first_user_name and len(first_user_name) > 2:
                search_term = first_user_name[:3]  # Erste 3 Zeichen
                found_users = await user_manager.find_users_by_name(search_term)

                print(
                    f"✅ Suche nach '{search_term}': {len(found_users)} User gefunden"
                )
                for user in found_users[:3]:
                    print(f"   📍 {user.name}")
            else:
                print("⚠️  Kann keine Namenssuche durchführen (kein passender Name)")

        # 5. Teste erweiterte Workspace-Info
        print("\n5️⃣ Teste erweiterte Workspace-Info...")
        workspace_info = await user_manager.get_workspace_info()

        if workspace_info:
            print("✅ Erweiterte Workspace-Info:")
            for key, value in workspace_info.items():
                if key.startswith("total_") or key.endswith("_users"):
                    print(f"   📊 {key}: {value}")

    except Exception as e:
        print(f"❌ Fehler bei User-Listen Operationen: {e}")
        import traceback

        traceback.print_exc()


async def test_pagination_example():
    """
    Beispiel für manuelle Pagination
    """
    print("\n" + "📄 Teste manuelle Pagination")
    print("=" * 50)

    try:
        from notionary import NotionUserManager

        user_manager = NotionUserManager()

        print("Durchlaufe alle Seiten manuell...")
        page = 1
        cursor = None
        total_users = 0

        while True:
            print(f"   Seite {page}...")
            response = await user_manager.list_users(page_size=5, start_cursor=cursor)

            if not response or not response.results:
                break

            total_users += len(response.results)
            print(f"   📄 Seite {page}: {len(response.results)} Users")

            # Wenn keine weiteren Seiten
            if not response.has_more:
                break

            cursor = response.next_cursor
            page += 1

            # Safety break
            if page > 10:
                print("   ⚠️  Abbruch nach 10 Seiten (Safety)")
                break

        print(f"✅ Pagination abgeschlossen: {total_users} Users insgesamt")

    except Exception as e:
        print(f"❌ Fehler bei Pagination: {e}")


if __name__ == "__main__":
    print("🎯 Notion User API - Erweiterte Tests")
    print("   Nutzt alle verfügbaren API-Endpoints inkl. User-Listen\n")

    # Haupttest
    asyncio.run(simple_user_test())

    # Erweiterte Tests
    asyncio.run(test_individual_user_operations())

    # Neue User-Listen Tests
    asyncio.run(test_user_list_operations())

    # Pagination Beispiel
    asyncio.run(test_pagination_example())

    print(f"\n{'='*60}")
    print("📋 ZUSAMMENFASSUNG:")
    print("✅ Verfügbare User-Funktionen:")
    print("   - Bot-User Info abrufen (/users/me)")
    print("   - Einzelne User per ID abrufen (/users/{id})")
    print("   - 🆕 ALLE Workspace-User auflisten (/users)")
    print("   - 🆕 Paginierte User-Listen")
    print("   - 🆕 User-Filterung nach Typ (person/bot)")
    print("   - 🆕 User-Suche nach Namen (client-side)")
    print("   - Workspace-Informationen über Bot-User")
    print("   - User-Daten aktualisieren")
    print("")
    print("❌ Einschränkungen:")
    print("   - Guests sind NICHT in der User-Liste enthalten")
    print("   - Namenssuche ist nur client-side möglich")
    print("   - Bulk-User-Operationen nicht unterstützt")
    print("   - Benötigt 'user information capabilities'")
    print("")
    print("💡 NEUE MÖGLICHKEITEN:")
    print("   - User-Discovery ohne externe IDs")
    print("   - Vollständige Workspace-User-Übersicht")
    print("   - Automatische Pagination-Behandlung")
    print("   - Smart User-Filtering und -Suche")
