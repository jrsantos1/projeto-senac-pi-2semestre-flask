from models.tables import *
from config import App
import pandas as pd
db = App().get_db()
engine =  db.get_engine()

def get_usuarios() -> dict:
    query = 'select * from cliente'
    df = pd.read_sql_query(query, con=engine)
    df = df.to_dict()
    return df
    
def get_transacoes():
    query = 'select * from cliente'
    df = pd.read_sql_query(query, con=engine)
    df = df.to_dict()
    return df

