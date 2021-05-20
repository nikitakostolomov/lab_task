import click

import db_and_migration.migration.models as md


@click.command()
def migration():
    """
    Функция для создания таблиц.
    """
    with md.db as db:
        db.create_tables([md.Author, md.Book])


if __name__ == "__main__":
    migration()
