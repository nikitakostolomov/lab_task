import click

import db_and_migration.migration.models as md


@click.command()
@click.option(
    "--author",
    "-a",
    type=str,
    help="Имя автора, если состоит из нескольких слов, то в кавычках",
)
@click.option(
    "--book_name",
    "-n",
    type=str,
    help="Название книги, если состоит из нескольких слов, то в кавычках",
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
    Функция для поиска книг по их автору, названию или году выпуска
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
            query = md.Book.select().join(md.Author).where(*author_where, *book_where)
        else:
            query = md.Book.select().join(md.Author)

    for row in query:
        if identifier:
            print(row.id)
        else:
            print(row.author_id.name, row.title, row.year)


if __name__ == "__main__":
    seeker()
