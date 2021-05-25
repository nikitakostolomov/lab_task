import utilities.seeker as s
import pytest


@pytest.mark.parametrize(
    ["table", "headers", "expected_result"],
    [
        ([[1, 2, 3], [4, 5, 6]], [1, 2, 3], '|   1 |   2 |   3 |\n|-----|-----|-----|\n|   1 |   2 |   3 |\n|   4 |   5 |   6 |\n')
    ]
)
def test_make_table(capsys, table, headers, expected_result):
    """
    :param table: подготовленный формат таблицы
    :param headers: загаловки таблицы
    :param expected_result: таблица
    """
    s.make_table(table, headers)
    actual_result = capsys.readouterr()
    assert actual_result.out == expected_result
