import typer

# from notionary.cli.databases import database_app
# from notionary.cli.pages import page_app
# from notionary.cli.data_sources import data_source_app
# from notionary.cli.file_uploads import file_upload_app
# from notionary.cli.users import user_app

app = typer.Typer(help="Notionary CLI — Notion workspace management.")
# app.add_typer(database_app, name="database")
# app.add_typer(page_app, name="page")
# app.add_typer(data_source_app, name="data-source")
# app.add_typer(file_upload_app, name="file-upload")
# app.add_typer(user_app, name="user")


def main() -> None:
    app()
