import click
import peewee as pw
from tabulate import tabulate

import db_and_migration.migration.models as md


def make_table(table, headers):
    """
    Функция для создания таблиц
    :param table:
    :param headers:
    :return:
    """
    print(tabulate(table, headers=headers, tablefmt="github"))


@click.command()
@click.option(
    "--author",
    "-a",
    type=str,
    help="Имя автора, если состоит из нескольких слов, то указать в кавычках",
)
@click.option(
    "--book_name",
    "-n",
    type=str,
    help="Название книги, если состоит из нескольких слов, то указать в кавычках",
)
@click.option("--year", "-y", type=int, help="Год издания книги")
@click.option(
    "--identifier",
    "-s",
    is_flag=True,
    help="Если этот флаг есть, то будут получены id книг, иначе все поля",
)
def seeker(author, book_name, year, identifier):
    """
    Функция для поиска книг по их автору, названию или году выпуска. Если опциональные параметры не указаны, то
    будет выведена вся информация.
    """
    book_where = []
    author_where = []
    with md.db:
        if author:
            author_where.append(md.Author.name == author)
        if book_name:
            book_where.append(md.Book.title == book_name)
        if year:
            book_where.append(md.Book.year == year)

        if book_where or author_where:
            query = (
                md.Book.select()
                .join(md.Author, pw.JOIN.LEFT_OUTER)
                .where(*author_where, *book_where)
            )
        else:
            query = md.Book.select().join(md.Author, pw.JOIN.LEFT_OUTER)

    table = []

    for row in query:
        if identifier:
            table.append([row.id])
        else:
            name = row.author_id.name if row.author_id is not None else None
            table.append(
                [
                    name,
                    row.title,
                    row.year,
                    row.language,
                    row.program_used,
                    row.src_url,
                    row.version,
                ]
            )

    if identifier:
        headers = ["id книги"]
        make_table(table, headers)

    else:
        headers = [
            "Имя автора",
            "Название",
            "Год",
            "Язык",
            "Использованная программа",
            "Ссылка",
            "Версия",
        ]
        make_table(table, headers)


if __name__ == "__main__":
    seeker()
