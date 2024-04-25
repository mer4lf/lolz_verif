import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import Column, MetaData, select, BigInteger, String
from sqlalchemy import or_, func, distinct
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

Base = declarative_base()

meta = MetaData()


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)


class Books(Base):
    __tablename__ = 'books'
    id = Column(BigInteger, primary_key=True, autoincrement="auto")
    user_id = Column(BigInteger)
    title = Column(String)
    author = Column(String)
    genres = Column(String)
    description = Column(String)


# ----------------------При первом запуске раскомментировать вот этот код, после срау закомментировать------------------------------------
# connection = psycopg2.connect(user="postgres", password="1111")
# connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#
# # Создаем курсор для выполнения операций с базой данных
# cursor = connection.cursor()
# sql_create_database = cursor.execute('create database lolz_books')
# # Создаем базу данных
# engine = create_engine("postgresql+psycopg2://postgres:1111@localhost/lolz_books")
# # Закрываем соединение
# cursor.close()
# connection.close()
#
# meta.create_all(engine)


class DataBase:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(self.database_url, echo=True)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_users_books(self, user_id):
        async with self.async_session() as session:
            async with session.begin():
                query = select(Books).filter(Books.user_id == user_id)
                result = await session.execute(query)
                books = result.scalars().all()
                return books

    async def set_user(self, user_id: int):
        async with self.async_session() as session:
            async with session.begin():
                user = User(id=user_id)
                session.add(user)
                await session.commit()
                return user.id

    async def user_exists(self, user_id: int):
        async with self.async_session() as session:
            async with session.begin():
                query = select(User).filter(User.id == user_id)
                result = await session.execute(query)
                user = result.scalars().first()
                if user:
                    return True
                else:
                    return False

    async def create_new_book(self, user_id, book_info):
        async with self.async_session() as session:
            async with session.begin():
                ad = Books(user_id=user_id, title=book_info['title'],
                           genres=book_info['genres'], author=book_info['author'],
                           description=book_info['description'])
                session.add(ad)
                await session.commit()

    async def get_book(self, book_id: int):
        async with self.async_session() as session:
            async with session.begin():
                query = select(Books).filter(Books.id == book_id)
                result = await session.execute(query)
                book = result.scalars().first()
                return book

    async def delete_book(self, ad_id):
        async with self.async_session() as session:
            async with session.begin():
                query = select(Books).filter(Books.id == ad_id)
                result = await session.execute(query)
                ad = result.scalars().first()
                await session.delete(ad)
                await session.commit()

    async def get_all_books(self):
        async with self.async_session() as session:
            async with session.begin():
                query = select(Books)
                result = await session.execute(query)
                ads = result.scalars().all()
                return ads

    async def search_books(self, keyword):
        async with self.async_session() as session:
            async with session.begin():
                keyword = f"{keyword.strip()}"  # Обеспечиваем, что ключевое слово окружено пробелами
                # Создаем SQL запрос к таблице книг
                query = select(Books).where(
                    or_(
                        func.lower(Books.title).like(f'%{keyword.lower()}%'),  # Поиск по названию
                        func.lower(Books.author).like(f'%{keyword.lower()}%')  # Поиск по автору
                    )
                )

                # Выполнение запроса и возврат результатов
                result = await session.execute(query)
                books = result.scalars().all()

                # Фильтрация результатов для удостоверения, что ключевое слово стоит отдельно
                filtered_books = [
                    book for book in books
                    if
                    keyword.strip().lower() in book.title.lower().split(
                        " ") or keyword.strip().lower() in book.author.lower().split(" ")
                ]

                return filtered_books

    async def search_books_genre(self, keyword):
        async with self.async_session() as session:
            async with session.begin():
                genre = f"{keyword.strip()}"

                query = select(Books).where(
                    func.lower(Books.genres).like(f'%{genre.lower()}%')
                )

                # Выполнение запроса и возврат результатов
                result = await session.execute(query)
                books = result.scalars().all()
                return books

    async def get_genres(self):
        async with self.async_session() as session:
            async with session.begin():
                query = select(Books)

                # Выполнение запроса и возврат результатов
                result = await session.execute(query)
                genres = result.scalars().all()
                ret = [i.genres for i in genres]
                return ret
