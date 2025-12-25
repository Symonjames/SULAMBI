from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")  # For PostgreSQL (production)

# Track which database type is being used
_db_type = None

def cursorInstance():
  global _db_type
  # Use PostgreSQL if DATABASE_URL is provided (production)
  if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    try:
      import psycopg2
      from urllib.parse import urlparse
      
      result = urlparse(DATABASE_URL)
      connect = psycopg2.connect(
        database=result.path[1:],  # Remove leading '/'
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port or 5432
      )
      _db_type = 'postgresql'
      return connect, connect.cursor()
    except ImportError:
      print("Warning: psycopg2 not installed. Install with: pip install psycopg2-binary")
      print("Falling back to SQLite...")
    except Exception as e:
      print(f"Error connecting to PostgreSQL: {e}")
      print("Falling back to SQLite...")
  
  # Fallback to SQLite (local development)
  db_path = DB_PATH or os.getenv("DB_PATH") or "app/database/database.db"
  
  connect = sqlite3.connect(db_path, timeout=30.0)
  connect.execute("PRAGMA journal_mode=WAL")
  connect.execute("PRAGMA synchronous=NORMAL")
  connect.execute("PRAGMA cache_size=1000")
  connect.execute("PRAGMA temp_store=MEMORY")
  _db_type = 'sqlite'
  return connect, connect.cursor()

def get_db_type():
  """Return the database type: 'postgresql' or 'sqlite'"""
  global _db_type
  if _db_type is None:
    # Check which database would be used
    if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
      try:
        import psycopg2
        _db_type = 'postgresql'
      except:
        _db_type = 'sqlite'
    else:
      _db_type = 'sqlite'
  return _db_type

def get_param_placeholder():
  """Return the correct parameter placeholder for the database type"""
  return '%s' if get_db_type() == 'postgresql' else '?'

