import click

import db_and_migration.migration.models as md


@click.command()
@click.option("--number", "-n", help="id книги, которую требуется удалить")
@click.option(
    "--delete_all",
    "-a",
    is_flag=True,
    help="Если этот флаг указан, удаляет все записи из таблицы авторов и книг",
)
def wiper(number, delete_all):
    """
    Функция для удаления записей из таблиц. Если id автора у указанной книги еще встречается где либо в таблице, то
    этот автор не будет удален, иначе также удаляется автор из таблицы авторов по его id.
    """
    if delete_all:
        md.Author.delete().execute()
        md.Book.delete().execute()

    if number:
        query = md.Book.select(md.Book.author_id).where(md.Book.id == number)
        author_id = 0

        for row in query:
            author_id = row.author_id

        md.Book.delete().where(md.Book.id == number).execute()
        rest_authors = md.Book.select().where(md.Book.author_id == author_id)

        if len(rest_authors) == 0:
            md.Author.delete().where(md.Author.id == author_id).execute()


if __name__ == "__main__":
    wiper()
