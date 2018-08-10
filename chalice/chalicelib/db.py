from sqlalchemy import declarative_base, create_engine
import os


db_host = os.environ['CSW_HOST']
db_port = os.environ['CSW_PORT']
db_user = os.environ['CSW_USER']
db_password = os.environ['CSW_PASSWORD']

Base = declarative_base()

engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/csw")
