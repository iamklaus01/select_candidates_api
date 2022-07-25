import sqlalchemy
import enum
from sqlalchemy import Column, ForeignKey, String, Integer, Enum, UniqueConstraint
from .database import metadata, engine

# Enum class
class Role(enum.Enum):
    admin = "ADMIN"
    common = "COMMON"

class ValueType(enum.Enum):
    integer = "INTEGER"
    multiple = "ENUM"

class Metric(enum.Enum):
    moreThan = "=>"
    lessThan = "<="
    equalTo = "="
   

users = sqlalchemy.Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(64)),
    Column("email", String, nullable=False, unique = True),
    Column("password", String(256)),
    Column("role", Enum(Role), default=Role.common),
)

candidates_files = sqlalchemy.Table(
    "candidatesFiles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("extension", String(5)),
    Column("path", String, nullable=False),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
)

selection_files = sqlalchemy.Table(
    "selectionFiles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("path", String, nullable=False),
    Column("candidatesFile_id", Integer, ForeignKey("candidatesFiles.id", ondelete="CASCADE")),
)

solver_stats = sqlalchemy.Table(
    "solverStats",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("status", String),
    Column("solutions", Integer),
    Column("selectionFile_id", Integer, ForeignKey("selectionFiles.id", ondelete="CASCADE")),
)

features = sqlalchemy.Table(
    "features",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("label", String, nullable=False),
    Column("valueType", Enum(ValueType), nullable=False),
    Column("candidatesFile_id", Integer, ForeignKey("candidatesFiles.id", ondelete="CASCADE")),
)

integer_constraints = sqlalchemy.Table(
    "iconstraints",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("min_value", Integer, nullable=False),
    Column("max_value", Integer, nullable=False),
    Column("feature_id", Integer, ForeignKey("features.id", ondelete="CASCADE")),
)

enum_constraints = sqlalchemy.Table(
    "econstraints",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("value", Enum(ValueType), nullable=False),
    Column("number", Integer, nullable=False),
    Column("metric", Enum(Metric), nullable=False),
    Column("feature_id", Integer, ForeignKey("features.id", ondelete="CASCADE")),
)

metadata.create_all(engine)