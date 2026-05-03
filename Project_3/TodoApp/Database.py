from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.ext.declarative import declarative_base

# Database connection with sqlite -----------  start -----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./todoApp.db"
engine  = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# Database connection with sqlite -----------  end -----------

# Database connection with postgress SQL -----------  start -----------
# pip install psycopg2-binary
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Admin%40123@localhost/TodoApplicationDatabase"
# engine  = create_engine(SQLALCHEMY_DATABASE_URL)
# Database connection with postgress SQL -----------  end -----------


# Database connection with MySQL -----------  start -----------
# pip install pymysql 
#  Admin%40123 == Admin@123
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Admin%40123@127.0.0.1:3306/TodoApplicationDatabase"
# engine  = create_engine(SQLALCHEMY_DATABASE_URL)
# Database connection with MySQL -----------  end -----------


SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


Base = declarative_base()
