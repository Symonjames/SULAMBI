from ..database import connection
from .SessionModel import SessionModel
from .Model import Model

class AccountModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "accounts"
    self.primaryKey = "id"
    self.filteredColumns = ["password"]
    self.columns = ["username", "password", "accountType", "membershipId", "active"]

  def create(self, username: str, password: str, accountType: str, membershipId: int=None, active: bool=True):
    return super().create((username, password, accountType, membershipId, active))

  def updatePassword(self, id: int, password: str):
    return super().updateSpecific(id, ["password"], (password,))

  def authenticate(self, username: str, password: str):
    param = connection.get_param_placeholder()
    conn, cursor = connection.cursorInstance()
    
    try:
      is_postgresql = connection.get_db_type() == 'postgresql'
      
      # Build column list - parseResponse maps by position, not column names
      # For PostgreSQL, use lowercase column names (PostgreSQL lowercases unquoted identifiers)
      # For SQLite, column names are case-insensitive
      all_columns = [self.primaryKey] + self.columns
      
      if is_postgresql:
        # PostgreSQL columns are lowercase, so use lowercase in SELECT
        # parseResponse will still create camelCase keys based on self.columns order
        columns_lower = [col.lower() for col in all_columns]
        column_list = ','.join(columns_lower)
        cursor.execute(f"SELECT {column_list} FROM {self.table} WHERE username={param} AND password={param} AND active={param}", (username, password, True))
      else:
        # SQLite is case-insensitive for identifiers
        column_list = ','.join(all_columns)
        cursor.execute(f"SELECT {column_list} FROM {self.table} WHERE username={param} AND password={param} AND active={param}", (username, password, True))
      
      parsed = self.parseResponse(cursor.fetchone())

      if (parsed == None):
        conn.close()
        return None

      # clears current user's current token
      SessionDb = SessionModel()

      # provide users their newly created token
      # parsed dictionary uses the keys from self.columns (camelCase)
      session = SessionDb.create(parsed["id"], parsed["accountType"])
      conn.close()
      return session
    except Exception as e:
      conn.close()
      print(f"Error in authenticate: {e}")
      import traceback
      traceback.print_exc()
      raise

  def deactivate(self, id: int):
    matchedAccount = super().get(id)
    if (matchedAccount == None):
      return None

    super().updateSpecific(id, ["active"], (False,))
    return matchedAccount

  def activate(self, id: int):
    matchedAccount = super().get(id)
    if (matchedAccount == None):
      return None

    super().updateSpecific(id, ["active"], (True,))
    return matchedAccount