from flask import session, redirect, url_for

def verificarUsuarioLogado():
    if not(not('usuario_logado' not in session or session['usuario_logado'] == None)):
        return redirect(url_for('login'))
    else:
        pass