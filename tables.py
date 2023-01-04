import sqlalchemy
import enum
from sqlalchemy import Column, ForeignKey, String, Integer, Float, Enum, DateTime, Boolean, Text
from database import metadata, engine


# Enum class
class Role(enum.Enum):
    admin = "ADMIN"
    common = "COMMON"

class ValueType(enum.Enum):
    number = "NUMBER"
    multiple = "ENUM"

class OptimizeType(enum.Enum):
    minimize = "MINIMIZE"
    maximize = "MAXIMIZE"


class Metric(enum.Enum):
    moreThan = ">="
    lessThan = "<="
    equalTo = "=="
   

users = sqlalchemy.Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(64)),
    Column("email", String, nullable=False, unique = True),
    Column("password", String(256)),
    Column("role", Enum(Role), default=Role.common),
    Column("verified", Boolean, nullable=False, default='False'),
    Column("verification_code", String, nullable=True, unique=True),
    Column("active", Boolean, default=True),
    Column("created_at", DateTime),
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
    Column("encodedFile", Text, nullable=False),
    Column("status", String),
    Column("nbre_sol", Integer),
    Column("satisfaction", Integer, nullable=True),
    Column("features", Text, nullable=False),
    Column("candidatesFile_id", Integer, ForeignKey("candidatesFiles.id", ondelete="CASCADE")),
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
    Column("coefficient", Float, nullable=True),
    Column("optimize", Enum(OptimizeType), nullable=True),
    Column("feature_id", Integer, ForeignKey("features.id", ondelete="CASCADE")),
)

enum_constraints = sqlalchemy.Table(
    "econstraints",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("value", String, nullable=False),
    Column("number", Integer, nullable=False),
    Column("metric", Enum(Metric), nullable=False),
    Column("weight", Integer, nullable=True),
    Column("optimize", Enum(OptimizeType), nullable=True),
    Column("feature_id", Integer, ForeignKey("features.id", ondelete="CASCADE")),
)

metadata.create_all(engine)