import sqlalchemy as sqlalchemy
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
#from sqlalchemy import create_engine
#from sqlalchemy.orm import declarative_base, sessionmaker
#from sqlalchemy.pool import StaticPool

#aqui se pondria otro url si se usara mysql o postgres
DB_URL = "sqlite:///./dbfile.db"
engine = sqlalchemy.create_engine(DB_URL, connect_args={"check_same_thread": False})

#si quisieramos usar postgres o mysql
#DB_URL = "postgresql://dbuser: password@localost/dbname"
#DB_URL = "mysql://dbuser: password@localost/dbname"
#engine = sqlalchemy.create_engine(DB_URL)

SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()
