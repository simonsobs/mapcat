"""
A custom SQLAlchemy type to (de)serialize pydantic models to JSONB.

See: https://github.com/fastapi/sqlmodel/pull/1324 - this can be removed at some point.
"""

from sqlalchemy.types import JSON, TypeDecorator


class JSONEncodedPydantic(TypeDecorator):
    impl = JSON
    cache_ok = True

    def __init__(self, pydantic_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pydantic_class = pydantic_class

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.model_dump(mode="json")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.pydantic_class(**value)
