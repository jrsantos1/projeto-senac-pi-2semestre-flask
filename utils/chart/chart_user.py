from itertools import groupby
from this import d
import pandas as pd 
from utils.data import user
from config import App
db = App().get_db()
# engine = db.create_engine("mysql://root:root123@localhost/jm_banco")

def get_chart_extrato_data(cpf):
    engine =  db.get_engine()
    extrato_registros = user.get_extrato(cpf, 20)
    conta = user.get_conta(cpf)
    
    print("extrato")
    print(type(extrato_registros))
    
    saldo_atual = []
    data = []
    
    df = pd.read_sql_query(f"select * from extrato where conta_id = {conta.conta_id}", con=engine)
    df = df[['extrato_data', 'valor']]
    df = df.groupby("extrato_data", group_keys=True, as_index=False).sum()
    print(df)
    valor = df['valor'].to_list()
    print(valor)
    data = df['extrato_data'].to_list()
    print(data)
    
    
    
    
    # for extrato in extrato_registros:
    #     saldo_atual.append(extrato.saldo_atual)
    #     data.append(extrato.extrato_data)
    
    return valor, data


