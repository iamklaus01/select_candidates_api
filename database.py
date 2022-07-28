import databases
import sqlalchemy

DATABASE_URL = "postgresql://klaus:sc_api_2022@localhost/selectd"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(DATABASE_URL)
