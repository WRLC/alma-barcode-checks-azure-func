"""
Object Relational Mapping (ORM) models for the application.
"""
import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

dotenv.load_dotenv()  # Load environment variables from .env file

engine = create_engine(os.getenv("SQLALCHEMY_DB_URL"))  # type:ignore[arg-type] # Create a new SQLite database
session_factory = sessionmaker(bind=engine)  # Create a session factory

Base = declarative_base()  # Create a base class for ORM models
