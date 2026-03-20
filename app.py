from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurações de Caminho
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'elenco.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração de Upload
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB por foto

# Garante que a pasta de fotos exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

class Personagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ator = db.Column(db.String(100), nullable=False)
    foto_path = db.Column(db.String(200)) # Nome do arquivo salvo
    tom_voz = db.Column(db.String(200))
    comportamento = db.Column(db.Text)
    figurino = db.Column(db.Text)

with app.app_context():
    # db.drop_all() # Use apenas se der erro de "column not found" de novo
    db.create_all()

@app.route('/')
def index():
    personagens = Personagem.query.order_by(Personagem.nome).all()
    return render_template('index.html', personagens=personagens)

@app.route('/adicionar', methods=['POST'])
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
def editar(id):
    personagem = Personagem.query.get_or_404(id)
    
    # Atualiza os textos
    personagem.nome = request.form.get('nome')
    personagem.ator = request.form.get('ator')
    personagem.tom_voz = request.form.get('tom_voz')
    personagem.comportamento = request.form.get('comportamento')
    personagem.figurino = request.form.get('figurino')

    # Lógica da Foto
    foto = request.files.get('foto')
    if foto and foto.filename != '':
        nome_arquivo = secure_filename(foto.filename)
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo))
        personagem.foto_path = nome_arquivo # Atualiza o caminho no banco

    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)