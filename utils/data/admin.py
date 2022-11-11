import pandas as pd

from config import App
db = App().get_db()
# from models.tables import *


def get_usuarios() -> dict:
    engine =  db.get_engine()
    query = '''
    select 
    c.nome, 
    c.data_nascimento, 
    c.sexo ,c.telefone, 
    a.conta, a.saldo, 
    a.tipo from cliente c 
    inner join conta a
    on c.cliente_id = a.cliente_id;
    ''' 
    df = pd.read_sql_query(query, con=engine)
    df = df.to_dict(orient='records')
    return df

def get_movimentacoes():
    engine =  db.get_engine()
    
    df = pd.read_sql_query('select * from extrato', con=engine)
    df = df[['extrato_data', 'valor']]
    df = df.groupby(by='extrato_data', as_index=False, group_keys=True).sum()
    
    data = df['extrato_data'].to_list()
    valor = df['valor'].to_list()
    
    
    return data, valor
    
def get_transacoes():
    query = 'select * from cliente'
    df = pd.read_sql_query(query, con=engine)
    df = df.to_dict()
    return df

