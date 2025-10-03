from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Text, DateTime
engine = create_engine("postgresql://postgres:pass@localhost:5432/cyber")
meta = MetaData()
logs = Table("logs", meta,
    Column("id", Integer, primary_key=True),
    Column("ts", DateTime),
    Column("username", String),
    Column("ip", String),
    Column("status", String)
)
meta.create_all(engine)
