import email
from models.tables import *
from flask import session, redirect, url_for, render_template, request, flash
from config import App
from utils.auth import auth
from utils.email import config_email as e_mail
import win32com.client as wincl
from jinja2 import FileSystemLoader, Environment
import pythoncom 


aplicativo = App()
app = aplicativo.get_app()

# rota inicial usuário
@app.route("/user")
def index_user():
    if not(not('usuario_logado' not in session or session['usuario_logado'] == None)):
        return redirect(url_for('login'))
    else:
        cpf = session['usuario_logado']
        cliente = Cliente.query.filter_by(cpf=cpf).first()
        conta = Conta.query.filter_by(cliente_id=cliente.cliente_id).first()
        return render_template('user/home.html', cliente = cliente, conta = conta)

# rota para realizar logout
@app.route("/user/logout")
def user_logout():
    if 'usuario_logado' in session:
        session['usuario_logado'] = None
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

# rota para criar novo usuário
@app.route("/novo_usuario", methods=['POST'])
def novo_usuario():
    
    cpf =  request.form['cpf']
    cliente = Cliente.query.filter_by(cpf=cpf).first()
    usuario = Usuario.query.filter_by(cpf=cpf).first()
    
    # recebendo dados de endereço
    
    cep = request.form['cep']
    bairro = request.form['bairro']
    uf = request.form['uf']
    cidade = request.form['cidade']
    bairro = request.form['bairro']
    rua = request.form['rua']
    numero = request.form['numero']
    complemento = request.form['complemento']
    
    endereco = Endereco_Cliente(
        cep=cep,
        uf = uf,
        cidade = cidade,
        bairro = bairro,
        rua = rua,
        numero = numero,
        complemento = complemento)
    
    try:
        db.session.add(endereco)
        db.session.commit()
    except:
        print("ocorreu um erro durante o cadastro do endereço")
    
    if cliente or usuario:
        print('cliente existe')
        flash('usuário já existe')
        redirect(url_for('login'))
            
    else:
        
        # criando novo cliente
        print('criando cliente')
        
        nome = request.form['nome']
        nascimento = request.form['nascimento']
        telefone = request.form['telefone']
        
        cliente = Cliente(cpf=cpf, nome=nome, data_nascimento=nascimento, telefone=telefone, endereco_cliente_id=endereco.endereco_cliente_id)
        db.session.add(cliente)
        db.session.commit()
        
        # salvando foto
        arquivo = request.files ['arquivo']
        image_path = aplicativo.get_path().join('/uploads')
        arquivo.save(f'{image_path}/{cliente.cliente_id}.jpg')
        
        # criando novo usuário
        
        email =  request.form['email']
        senha = request.form['senha']
            
        usuario = Usuario(email=email, senha=senha, cpf=cpf)
        db.session.add(usuario)
        db.session.commit()
        
        #criando nova conta 
        
        conta_numero = request.form['conta']
        saldo = 0
        tipo = request.form['tipo']
        
        conta = Conta(conta=conta_numero, saldo=saldo, tipo=tipo, cliente_id=cliente.cliente_id)
        db.session.add(conta)
        db.session.commit()
        
        # derrubando sessão
        
        session['usuario_logado'] = None
        
        flash('Seu cadastro foi criado com sucesso')
        return redirect(url_for('login'))
    
    return redirect(url_for('login'))

# rota para direcionar tela de transação
@app.route('/user/transacao')
def transacao():
    return render_template('user/transacao.html')

# rota para realizar transferência
@app.route("/user/transferir", methods=['POST'])
def transferir():
    
    auth.verificarUsuarioLogado()
    
    conta_destino = request.form['conta_destino']
    valor = request.form['valor']
    conta = Conta.query.filter_by(conta_id=conta_destino).first()
    print(conta)
    cliente_logado = Cliente.query.filter_by(cpf=session['usuario_logado']).first()
    conta_logado = Conta.query.filter_by(cliente_id=cliente_logado.cliente_id).first()
    
    user_cliente_logado = Usuario.query.filter_by(cpf=cliente_logado.cpf).first()
    
    cliente_destinatario = Cliente.query.filter_by(cliente_id=conta.cliente_id).first()
    print(cliente_destinatario.cliente_id)
    user_cliente_destinatario = Usuario.query.filter_by(cpf=cliente_destinatario.cpf).first() 
    print(user_cliente_destinatario.cpf)


    if not(conta) or conta == None: 
        flash('Conta de destino não existe')
        return redirect(url_for('transacao'))
    
    if conta_logado.saldo < float(valor):
         flash('saldo insuficiente')
         return redirect(url_for('transacao'))
    
    data = request.form['data']
    tipo = request.form['tipo']
    
    # salando transacao
    
    transacao = Transacao(
        conta_origem_id=conta_logado.conta_id, 
        conta_destino_id=conta.conta_id, 
        transacao_data=data, 
        valor=valor, 
        operacao_id=tipo)
    
    db.session.add(transacao)
    db.session.commit()
    
    # alterando saldos 
    
    novo_valor = float(valor)
    conta_logado.saldo -= novo_valor 
    conta.saldo += novo_valor    
    db.session.add(conta_logado)
    db.session.add(conta)
    db.session.commit()
    
    # gerando extrato
    saldo_extrado_saida = novo_valor - (novo_valor * 2) 
    extrato_saida = Extrato(conta_id=conta_logado.conta_id, extrato_data=data, fluxo='Saída', valor=saldo_extrado_saida)
    extrato_entrada = Extrato(conta_id=conta.conta_id, extrato_data=data, fluxo='Entrada', valor=valor)
        
    db.session.add(extrato_saida)
    db.session.add(extrato_entrada)
    
    db.session.commit()
    
    # enviar e-mail 
    
    dados_email = {
        'valor': valor,
        'destinatario':conta_destino,
        'data': data
    }
    
    print(dados_email['destinatario'])
    
    template = e_mail.carregar_template(dados_email, 'email/email_transferencia_realizada.html')
    print(user_cliente_logado)
    e_mail.enviar(destinatario=user_cliente_logado.email, template=template)
    
    dados_email = {
        'nome' : 'teste',
        'valor': valor,
        'remetente':user_cliente_logado.cpf,
        'data': data
    }
    
    template_transferencia_recebida = e_mail.carregar_template(dados_email,'email/email_transferencia_recebida.html' )
    e_mail.enviar(destinatario=user_cliente_destinatario.email, template=template_transferencia_recebida)
    
    return redirect(url_for('index_user'))
        
    