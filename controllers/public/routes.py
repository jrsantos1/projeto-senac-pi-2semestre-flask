from models.tables import *
import string
from flask import session, redirect, url_for, render_template, request, flash, send_from_directory
from config import App
import plotly
import plotly.express as px
import json
import pandas as pd
from utils.auth.auth import *

aplicativo = App()
app = aplicativo.get_app()

# Página inicial
@app.route("/")
def home():

    y = [1,2,3,6]
    x = ['jhonatan','lucas','fernando','marques', ]
    
    df = pd.DataFrame(dict(
    x = [1, 3, 2, 4],
    y = [1, 2, 3, 4]
    ))
    fig = px.line(df, y=y,  x=x, title="Unsorted Input") 
    
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    clientes = Cliente.query.order_by(Cliente.cliente_id)
    for cliente in clientes:
        print(cliente.nome)
    return render_template("home.html", titulo="Lista", clientes=clientes, graphJSON=graphJSON)

@app.route("/sobre", methods=['GET', 'POST'])
def sobre():
    return render_template("sobre.html", titulo="sobre")

@app.route("/abrir_conta")
def abrir_conta():
    return render_template("user/abrir_conta.html", titulo="criar template")

@app.route("/login")
def login():
    if 'usuario_logado' in session:
        if not (session['usuario_logado'] == None):
            return redirect(url_for('index_user'))
        
    return render_template("user/login.html", titulo="login")

# rotas de autenticação

@app.route('/admin/login')
def login_admin():
    if 'admin_logado' in session:
        if not (session['admin_logado'] == None):
            return redirect(url_for('admin_home'))
        
    return render_template('admin/admin_login.html')
    

@app.route('/admin/autenticar', methods=['Post'])
def autenticar_admin():
    usuario: string = request.form['usuario']
    senha: string = request.form['senha']
    
    usuario_adm = Usuario_Admin.query.filter_by(admin_usuario=request.form['usuario']).first()
    
    if usuario_adm: 
        if senha == usuario_adm.admin_senha:
            if 'usuario_logado' in session:
                session['usuario_logado'] = None
            
            session['admin_logado'] = usuario
            
            return redirect(url_for('admin_home'))

    return redirect(url_for('login_admin'))
            
@app.route('/admin')
def admin_home():
    logado = verifica_admin_logado()
    if logado:
        return render_template('/admin/admin_home.html')
    else: 
        return redirect(url_for('login_admin'))    
    
@app.route("/autenticar", methods=['POST'])
def autenticar():
    #recebendo dados enviados pelo formulário 
    cpf: string = request.form['cpf']
    senha: string = request.form['senha']
    # verificando se há usuário no banco de dados com consulta
    usuario = Usuario.query.filter_by(cpf=request.form['cpf']).first()
    if usuario:
        if senha == usuario.senha:
            session['usuario_logado'] = usuario.cpf
            cliente = Cliente.query.filter_by(cpf=cpf).first()
            return redirect(url_for('index_user'))
        else:
            flash('falha no login')
            return redirect(url_for('login'))
    flash('falha no login')
    return redirect(url_for('login'))

@app.route('/adicionar_foto/<nome_arquivo>')
def adicionar_foto(nome_arquivo):
     return send_from_directory('uploads', nome_arquivo)