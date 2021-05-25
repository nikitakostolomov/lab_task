import pytest
import utilities.digger as d


@pytest.mark.parametrize(
    ["row_slice", "start_attribute", "end_attribute", "expected_result"],
    [
        ("abc<author>Лол Кеков</author>", "<author>", "</author>", "Лол Кеков"),
        (
                "abc<author><first_name>Лол</first_name><last_name>Кеков</last_name></author>", "<first_name>",
                "</first_name>",
                "Лол"),
        ("abc<book_title>Книга</book_title>", "<book_title>", "</book_title>", "Книга"),
        ("abc<book_title>Книга</book_title>", "<author>", "</author>", "")
    ],
)
def test_get_attribute(row_slice, start_attribute, end_attribute, expected_result):
    """
    :param row_slice: строка, в которой находятся интересующие нас атрибуты
    :param start_attribute: начанльный тег fb2
    :param end_attribute: конечный тег fb2
    :param expected_result: атрибут или пустая строка, если атрибут не найден
    """
    actual_result = d.get_attribute(row_slice, start_attribute, end_attribute)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    ["attribute", "attr_type", "expected_result"],
    [
        ("Лол Кеков", str, "Лол Кеков"),
        ("1337", int, 1337),
        ("", str, None)
    ]
)
def test_check_attr_for_none(attribute, attr_type, expected_result):
    """
    :param attribute: атрибут для проверки
    :param attr_type: тип, в который нужно обернуть атрибут
    :param expected_result: атрибут обернутый в указанный тип или None, если атрибут является False
    """
    actual_result = d.check_attr_for_none(attribute, attr_type)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    ["row", "expected_result"],
    [
        ("""<book-title>...Сказал он, смеясь</book-title><author>
      <first-name>Саймон</first-name>
      <last-name>Грин</last-name>
    </author><year>2013</year>""", ["Саймон Грин", "...Сказал он, смеясь", 2013, None, None, None, None]),
        ("<first-name>Саймон</first-name>", [])

    ]
)
def test_find_info(row, expected_result):
    """
    :param row: строка, состоящая из нескольких строк книги
    :param expected_result: список с информацией об атрибутах, если название книги не найдено, вернется пустой список.
    Если атрибут не найден, вместо него будет проставлено значение None.
    """
    actual_result = d.find_info(row)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    ["path_to_book", "expected_result"],
    [
        ("tests/TestBooks/TestBook1.txt", """<author><first-name>Александр</first-name><last-name>Бакулин</last-name><id>e05b60e0-31fc-43dd-be60-a18f3f3a5256</id></author><book-title>Гравитация и эфир</book-title><title>"""),
        ("tests/TestBooks/TestBook2.txt", "")

    ]
)
def test_read_rows(path_to_book, expected_result):
    """
    :param path_to_book: путь до книги, чтобы ее открыть и передать в функцию
    :param expected_result: строка, состоящая из нескольких строк книги
    """
    with open(path_to_book, encoding="utf8") as f:
        actual_result = d.read_rows(f)
    assert actual_result == expected_result




