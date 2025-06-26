import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import urllib.parse
from sqlalchemy.ext.declarative import declarative_base

# Load .env file
load_dotenv()

# Get database connection details
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = urllib.parse.quote_plus(os.getenv('DB_PASS'))  # Encode special chars
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Build SQLAlchemy DB URI
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Optional debug print (remove in production)
print("Connecting to DB with URI:", SQLALCHEMY_DATABASE_URI)

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ This was missing
Base = declarative_base()
