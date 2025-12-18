from sqlalchemy.orm import declarative_base
from core.db import metadata

# class Base(DeclarativeBase):
#     metadata = metadata

Base = declarative_base(metadata=metadata)