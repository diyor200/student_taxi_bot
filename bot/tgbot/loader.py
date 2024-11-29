from .config import load_config
from .misc.db_api.postgres import Database



db = Database()
config = load_config(".env")
