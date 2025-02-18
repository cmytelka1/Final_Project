from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, MetaData, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

db = SQLAlchemy(metadata=MetaData())

person = Table(
    "person",
    db.metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String, nullable=False),
    Column("last_name", String),
    Column("username", String),
    Column("password", String),
    Column("email", String),
    Column("role", String)
)

manuscript = Table(
    "manuscript",
    db.metadata,
    Column("ms_id", Integer, primary_key=True),
    Column("ms_name", String),
    Column("author_id", ForeignKey("person.id")),
    Column("title", String, nullable=False),
    Column("abstract", Text),
    Column("submission_date", DateTime(timezone=True), server_default=func.now()),
    Column("status", String)
)

keywords = Table(
    "keywords",
    db.metadata,
    Column("kw_id", Integer, primary_key=True),
    Column("ms_id", Integer, ForeignKey("manuscript.ms_id")),
    Column("author_id", Integer, ForeignKey("person.id")),
    Column("keyword", String)
)

decision = Table(
    "decision",
    db.metadata,
    Column("id", Integer, primary_key=True),
    Column("ms_id", Integer, ForeignKey("manuscript.ms_id")),
    Column("decision_ind", Integer),
    Column("decision_text", String)
)