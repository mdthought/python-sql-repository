from abc import ABC, abstractmethod
from sqlite3 import Connection
from typing import Sequence

from .base_model import BaseModel


class BaseRepository[T: BaseModel](ABC):
    def __init__(self, connection: Connection):
        super().__init__()

        self._connection = connection
        self._cursor = connection.cursor()

    @property
    @abstractmethod
    def table_name(self) -> str:
        pass

    @property
    @abstractmethod
    def pk(self) -> Sequence[str]:
        pass

    @property
    @abstractmethod
    def model(self) -> type[T]:
        pass

    @property
    def _model_field_names(self) -> Sequence[str]:
        return self.model.model_fields.keys()

    async def get_by_pk(self, *values) -> T | None:
        where_clause = " AND ".join(
            f"{name} = ?" for name in self.pk
        )

        result = self._cursor.execute(f'''
            SELECT id, name
            FROM {self.table_name}
            WHERE {where_clause};
        ''', values).fetchone()

        if result is None:
            return None

        model_dict = {
            name: value
            for name, value
            in zip(self._model_field_names, result)
        }

        return self.model.model_validate(model_dict)

    async def save(self, value: T) -> None:
        values = tuple(getattr(value, name) for name in self._model_field_names)

        self._cursor.execute(f'''
            INSERT INTO {self.table_name} ({', '.join(self._model_field_names)})
            VALUES ({', '.join(['?'] * len(self._model_field_names))})
        ''', values)

        self._connection.commit()
