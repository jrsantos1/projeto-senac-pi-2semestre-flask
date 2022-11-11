from flask import session, redirect, url_for

def verificarUsuarioLogado():
    if ('usuario_logado' not in session or session['usuario_logado'] == None):
        return redirect(url_for('login'))
    else:
        pass
def verifica_admin_logado():
    if ('admin_logado' not in session or session['admin_logado'] == None):
        return False
    else:
        return True