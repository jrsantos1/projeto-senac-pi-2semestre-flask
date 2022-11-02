from flask import session
from models.tables import *

def get_cliente_logado(cpf)-> Cliente : 
    cliente = Cliente.query.filter_by(cpf=cpf).first()
    return cliente

def get_conta_cliente_logado(cpf) -> Conta:
    cliente = Cliente.query.filter_by(cpf=cpf).first()
    conta = Conta.query.filter_by(cliente_id=cliente.cliente_id).first()
    return conta;

def get_conta_extrato(cpf, size) -> Extrato :
    cliente = Cliente.query.filter_by(cpf=cpf).first()
    conta = Conta.query.filter_by(cliente_id=cliente.cliente_id).first()
    extrato = Extrato.query.filter_by(conta_id=conta.conta_id).limit(size)
    return extrato