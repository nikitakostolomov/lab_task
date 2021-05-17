import peewee as pw

db = pw.SqliteDatabase("db_and_migration/database/main.db")


class BaseModel(pw.Model):
    """
    Базовая модель, от которой наследуются другие модели.
    В каждой модели должно быть поле id, которое будет являться первичным ключом
    Все модели будут подключаться к базе данных main.db и сортироваться по первичному ключу. Это описано в метаклассе.

    id: первичный ключ

    class Meta:
        database: база данных, к которой осуществляется подключение
        order_by: поле, по которому будет сортироваться таблица
    """

    id = pw.PrimaryKeyField(unique=True)

    class Meta:
        database = db
        order_by = "id"


class Author(BaseModel):
    """
    Модель автор. Наследуется от базовой модели.
    Описывает таблицу авторов, в которой будут указаны имя автора и внешний ключ, ссылающийся на таблицу книг.
    Имя автора будет проиндексировано.

    name: имя автора, строка
    book_id: внешний ключ, ссылающийся на таблицу книг

    class Meta:
        db_table: название таблицы, которе будет использоваться в бд
    """
    name = pw.CharField(index=True)
    book_id = pw.DeferredForeignKey("Book")

    class Meta:
        db_table = "authors"


class Book(BaseModel):
    """
    Модель книга. Наследуется от базовой модели.
    Описывает таблицу книг, в которой будут указаны внешний ключ, ссылающийся на таблицу авторов, название книги,
    год выпуска книги.
    Название книги и год выпуска будут проиндексированы.

    author_id: внешний ключ, ссылающийся на таблицу авторов
    title: название книги, строка
    year: год выпуска книги, integer

    class Meta:
        db_table: название таблицы, которе будет использоваться в бд
        """
    author_id = pw.ForeignKeyField(Author)
    title = pw.CharField(index=True)
    year = pw.IntegerField(index=True)

    class Meta:
        db_table = "books"


if __name__ == "__main__":
    with db:
        db.create_tables([Author, Book])
