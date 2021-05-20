import gzip as gz
import os
import zipfile as zf

import click
import peewee as pw

import db_and_migration.migration.models as md


def get_attribute(
    row_slice: str, start_attribute: str, end_attribute: str
) -> str or int:
    """
    Функция для поиска конкретного атрбитуа, заключенного в теги книги fb2.
    :param row_slice: строка, в которой находятся интересующие нас атрибуты
    :param start_attribute: начанльный тег fb2
    :param end_attribute: конечный тег fb2
    :return: атрибут или пустая строка, если атрибут не найден
    """
    start_pos_attr = row_slice.find(start_attribute)
    end_pos_attr = row_slice.find(end_attribute)
    if start_pos_attr != -1 and end_pos_attr != -1:
        start_pos_attr += len(start_attribute)
        end_pos_attr = end_pos_attr
        return row_slice[start_pos_attr:end_pos_attr]
    else:
        return ""


def find_info(row: str) -> list:
    """
    Функция для поиска автора, названия и года с помощью функции get_attribute в переданной строке. Если атрибут не
    найден, вместо него будет проставлена пустая строка или 0, если этот атрибут является годом выпуска.
    :param row: строка, состоящая из нескольких строк книги
    :return: список с информацией об атрибутах
    """
    info_list = []
    title = get_attribute(row, "<book-title>", "</book-title>")

    if title:
        author_slice = get_attribute(
            row, "<author>", "</author>"
        )  # находим все, что заключено между тегами автора
        first_name = get_attribute(
            author_slice, "<first-name>", "</first-name>"
        )  # ищем имя в тегах автора
        middle_name = get_attribute(
            author_slice, "<middle-name>", "</middle-name>"
        )  # ищем отчество в тегах автора
        last_name = get_attribute(
            author_slice, "<last-name>", "</last-name>"
        )  # ищем фамилию в тегах автора
        full_name = f"{first_name} {middle_name} {last_name}"

        if full_name.isspace():
            info_list.append(None)
        else:
            info_list.append(full_name.strip().replace("  ", " "))

        info_list.append(title)

        year = get_attribute(row, "<year>", "</year>")
        info_list.append(check_attr_for_none(year, int))

        language = get_attribute(row, "<lang>", "</lang>")
        info_list.append(check_attr_for_none(language, str))

        program_used = get_attribute(row, "<program-used>", "</program-used>")
        info_list.append(check_attr_for_none(program_used, str))

        src_url = get_attribute(row, "<src-url>", "</src-url>")
        info_list.append(check_attr_for_none(src_url, str))

        version = get_attribute(row, "<version>", "</version>")
        info_list.append(check_attr_for_none(version, str))

    return info_list


def check_attr_for_none(attribute: str or int, attr_type: type) -> str or int or None:
    """
    Функция для проверки есть ли переданный атрибут, если есть то возврщает его, обернув в переданный тип, если нет,
    то вернет None.
    :param attribute: атрибут для проверки
    :param attr_type: тип, в который нужно обернуть атрибут
    :return: атрибут обернутый в указанный тип или None, если атрибут является False
    """
    if attribute:
        return attr_type(attribute)
    else:
        return None


def read_rows(book) -> str:
    """
    Получает открытую книгу и читает первые 15 строк или пока не встретит тег <title>. Прочтенные строки
    конкатинируются в одну, чтобы избежать ситуаций, когда теги находятся на разных строках (в этом случае информацию
    о авторе, книге или годе можно потерять) и передаются функции add_data_to_db для добавления информации в бд.
    :param book: открытая книга
    :return: строка, состоящая из несколькиз строк книги
    """
    book_text = ""
    count_rows = 0
    while True:
        try:
            row = book.readline().strip()
        except UnicodeDecodeError:
            row = ""
        if type(row) is bytes:
            row = row.decode("utf8")
        book_text += row + " "
        count_rows += 1
        if row.find("<title>") != -1 or count_rows == 100:
            break

    return book_text


def add_data_to_db(data: str, update: bool) -> None:
    """
    Ищет информацию с помощью функции find_info и передает ее в фукнции add_data_to_authors и add_data_to_books,
    которые добавляют информацию в базу данных.
    :param data: инофрмация в виде строки
    :param update: флаг для функций add_data_to_books и add_data_to_authors
    """
    info_list = find_info(data)
    if info_list:
        add_data_to_authors(info_list[0])
        add_data_to_books(info_list, update)


def parse_fb2(path_to_book: str, update: bool) -> None:
    """
    Функция для чтения книги в формате fb2. Читает первые 15 строк или пока не встретит тег <title>. Прочтенные строки
    конкатинируются в одну, чтобы избежать ситуаций, когда теги находятся на разных строках (в этом случае информацию
    о авторе, книге или годе можно потерять) и передаются функции add_data_to_db для добавления информации в бд.
    :param path_to_book: путь до книги
    :param update: флаг для функций add_data_to_books и add_data_to_authors
    """
    book_text = ""
    try:
        with open(path_to_book, encoding="utf8") as book:
            book_text = read_rows(book)
    except IOError:
        print(f"Произошла ошибка во время чтения файла {path_to_book}")

    add_data_to_db(book_text, update)


def parse_fb2_zip(path_to_book: str, update: bool) -> None:
    """
    Функция для чтения книги в формате fb2.zip. Читает первые 15 строк или пока не встретит тег <title>. Прочтенные
    строки конкатинируются в одну, чтобы избежать ситуаций, когда теги находятся на разных строках (в этом случае
    информацию о авторе, книге или годе можно потерять) и передаются функции add_data_to_db для добавления информации в
    бд.
    :param path_to_book: путь до книги
    :param update: флаг для функций add_data_to_books и add_data_to_authors
    """
    book_text = ""
    try:
        with zf.ZipFile(path_to_book) as zp:
            book_names = zf.ZipFile.namelist(zp)
            for book in book_names:
                if book.endswith("fb2"):
                    with zp.open(book) as bk:
                        book_text = read_rows(bk)
                add_data_to_db(book_text, update)
    except zf.BadZipFile:
        print(f"Произошла ошибка во время чтения архива zip {path_to_book}")


def parse_fb2_gz(path_to_book: str, update: bool) -> None:
    """
    Функция для чтения книги в формате fb2.gz. Читает первые 15 строк или пока не встретит тег <title>. Прочтенные
    строки конкатинируются в одну, чтобы избежать ситуаций, когда теги находятся на разных строках (в этом случае
    информацию о авторе, книге или годе можно потерять) и передаются функции add_data_to_db для добавления информации в
    бд.
    :param path_to_book: путь до книги
    :param update: флаг для функций add_data_to_books и add_data_to_authors
    """
    try:
        with gz.open(path_to_book, "rb") as book:
            book_text = read_rows(book)
    except gz.BadGzipFile:
        print(f"Произошла ошибка во время чтения архива gz {path_to_book}")

    add_data_to_db(book_text, update)


def parse_file(book_path: str, update: bool) -> None:
    """
    В зависимости от расширения книги, вызывает нужный метод для получения информации об авторе, названии и годе
    выпуска.
    :param book_path: путь до книги
    :param update: флаг для функций add_data_to_books и add_data_to_authors
    """
    if book_path.endswith("fb2"):
        parse_fb2(book_path, update)

    if book_path.endswith("fb2.zip"):
        parse_fb2_zip(book_path, update)

    if book_path.endswith("fb2.gz"):
        parse_fb2_gz(book_path, update)


def parse_files_from_directory(dir_path: str, update: bool) -> None:
    """
    Получает директорию, в которой хранятся книги. Для каждой книги вызывает метод parse_file.
    :param dir_path: путь до директории с книгами
    :param update: флаг для функций add_data_to_books и add_data_to_authors
    """
    for book_path in os.listdir(dir_path):
        parse_file(dir_path + book_path, update)


def add_data_to_authors(authors_name: str) -> None:
    """
    Добавляет в таблицу авторов информацию об авторе (его ФИО), если информации нет, то ничего не добавляем.
    :param authors_name: имя автора или пустая строка, если автора нет
    """
    with md.db:
        if authors_name:
            md.Author.get_or_create(name=authors_name)


def add_data_to_books(info_list: list, update: bool) -> None:
    """
    Добавляет в таблицу книг информацию об авторе, названии и годе выпуска. Если информации об авторе или годе нет в
    тегах книги, то на их местах в таблице будет стоять null.
    Если название книги уже есть в таблице, действуем в зависимости от флага update.
    :param info_list: список из автора, названия книги, года выпуска, языка, использованной программы, ссылки и
    версии
    :param update: флаг, если True, то обновляем информацию по уже имеющейся книге в таблице, если False, ничего
    не делаем
    """
    get_list = ["author_id", "title", "year"]
    update_list = ["language", "program_used", "src_url", "version"]
    with md.db:
        author_id = md.Author.select().where(md.Author.name == info_list[0])
        get_list_attrs = list(author_id)

        if not get_list_attrs:
            get_list_attrs = [None]
        get_list_attrs.extend(info_list[1:3])

        get_keywords = dict(zip(get_list, get_list_attrs))
        update_keywords = dict(zip(update_list, info_list[3:]))

        try:
            book_id = md.Book.get(**get_keywords).id
            if update:
                md.Book.update(**update_keywords).where(md.Book.id == book_id).execute()
        except pw.DoesNotExist:
            md.Book.insert(**get_keywords, **update_keywords).execute()


def check_directory_or_file(path: str) -> bool:
    """
    Проверяет существует ли переданная директория или файл
    :param path: путь до файла
    :return: если переданный путь до директории или файла существует, возвращает True, иначе выводит сообщение
    об ошибке в stdout
    """
    if os.path.exists(path):
        return True
    else:
        print(f"Директории {path} не существует")
        return False


@click.command()
@click.argument("dir_path")
@click.option(
    "--book_name",
    "-a",
    type=str,
    default=None,
    help="""Название книги. Если этого параметра нет, то база 
    данных будет
    заполняться информацией о всех книгах в директории, если есть, то в базу данных попадет информация только об
    одной книге.""",
)
@click.option(
    "--update",
    "-u",
    is_flag=True,
    help="""флаг. Если он есть, то информация книгах с одинаковым названием 
    будет обновлена, иначе ничего не происходит.""",
)
def digger(dir_path: str, book_name, update) -> None:
    """
    Функция для заполнения базы данных информацией о книгах в формате fb2, fb2.zip и fb2.gz.

    dir_path: путь до директории с книгами
    """
    dir_path = f"{dir_path}/"

    if book_name is not None:
        full_book_path = dir_path + book_name
        if check_directory_or_file(full_book_path):
            parse_file(full_book_path, update)

    else:
        if check_directory_or_file(dir_path):
            parse_files_from_directory(dir_path, update)


if __name__ == "__main__":
    digger()
