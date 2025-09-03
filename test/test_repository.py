import sqlite3
from unittest.async_case import IsolatedAsyncioTestCase

from repository.base_model import BaseModel
from repository.base_repository import BaseRepository

connection = sqlite3.connect('test.sqlite3')
cursor = connection.cursor()


class Dummy(BaseModel):
    id: int
    name: str


class DummyRepository(BaseRepository[Dummy]):
    @property
    def table_name(self) -> str:
        return "dummy"

    @property
    def model(self):
        return Dummy

    @property
    def pk(self):
        return "id",


class TestRepository(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dummy (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );
        ''')
        connection.commit()

    async def asyncSetUp(self):
        cursor.execute('''
            DELETE FROM dummy WHERE TRUE;
        ''')

        cursor.execute('''
            INSERT INTO dummy (id, name) VALUES
            (1, 'Alice'),
            (2, 'Bob'),
            (3, 'Charlie');
        ''')

        connection.commit()

    async def test_get_by_pk(self):
        dummy_repository = DummyRepository(connection)
        v = await dummy_repository.get_by_pk(1)

        self.assertIsInstance(v, Dummy)

    async def test_save(self):
        dummy_repository = DummyRepository(connection)

        dummy = Dummy(id=4, name='David')
        await dummy_repository.save(dummy)
        v = await dummy_repository.get_by_pk(4)

        self.assertEqual(v, dummy)
