from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mssql import dialect
from sqlalchemy.orm import sessionmaker
from core.config import POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT,DATABASE_URL
from psycopg2.extras import Json
metadata = MetaData()

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

print(engine)
