from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

# 1. PRIMEIRO criamos o app
app = Flask(__name__)

# 2. DEPOIS configuramos o que ele precisa
app.secret_key = 'supersecretkey'  # Agora funciona!
ADM_PASSWORD = os.getenv('ADM_PASSWORD', 'admin123')

# Configurações de Caminho
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'elenco.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração de Upload
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# --- MODELO ---
class Personagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ator = db.Column(db.String(100), nullable=False)
    foto_path = db.Column(db.String(200))
    tom_voz = db.Column(db.String(200))
    comportamento = db.Column(db.Text)
    figurino = db.Column(db.Text)

# Criar banco de dados
with app.app_context():
    db.create_all()

# --- SEGURANÇA ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADM_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Senha Incorreta!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    personagens = Personagem.query.order_by(Personagem.nome).all()
    return render_template('index.html', personagens=personagens)

@app.route('/adicionar', methods=['POST'])
@login_required
def adicionar():
    foto = request.files.get('foto')
    nome_arquivo = None
    if foto and foto.filename != '':
        nome_arquivo = secure_filename(foto.filename)
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo))

    novo = Personagem(
        nome=request.form.get('nome'),
        ator=request.form.get('ator'),
        foto_path=nome_arquivo,
        tom_voz=request.form.get('tom_voz'),
        comportamento=request.form.get('comportamento'),
        figurino=request.form.get('figurino')
    )
    db.session.add(novo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['POST'])
@login_required
def editar(id):
    personagem = Personagem.query.get_or_404(id)
    personagem.nome = request.form.get('nome')
    personagem.ator = request.form.get('ator')
    personagem.tom_voz = request.form.get('tom_voz')
    personagem.comportamento = request.form.get('comportamento')
    personagem.figurino = request.form.get('figurino')

    foto = request.files.get('foto')
    if foto and foto.filename != '':
        nome_arquivo = secure_filename(foto.filename)
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo))
        personagem.foto_path = nome_arquivo

    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
