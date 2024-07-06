from flask import Flask, request, jsonify, send_file, g
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import sqlite3
import uuid
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://historiallaboral.com"}})

# Directorio donde se guardarán los archivos subidos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurarse de que el directorio de carga exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configuración de la base de datos SQLite
DATABASE = 'token_store.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                token TEXT PRIMARY KEY,
                nss TEXT NOT NULL,
                expires INTEGER NOT NULL
            )
        ''')
        db.commit()

@app.before_first_request
def initialize():
    init_db()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files or 'nss' not in request.form:
        return jsonify(message='Por favor proporciona archivos y un NSS'), 400

    nss = request.form['nss']
    files = request.files.getlist('files')

    if not files or any(file.filename == '' for file in files):
        return jsonify(message='Por favor sube al menos un archivo'), 400

    # Crear directorio para el NSS si no existe
    nss_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(nss))
    if not os.path.exists(nss_dir):
        os.makedirs(nss_dir)

    uploaded_files = []

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(nss_dir, filename)

        # Verificar si el archivo ya existe y agregar sufijo numérico si es necesario
        if os.path.exists(file_path):
            base, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(file_path):
                new_filename = f"{base}_v{counter}{extension}"
                file_path = os.path.join(nss_dir, new_filename)
                counter += 1
            filename = new_filename

        file.save(file_path)
        uploaded_files.append(filename)

    return jsonify(message='Archivos subidos exitosamente', files=uploaded_files), 200

@app.route('/upload-signature', methods=['POST'])
def upload_signature():
    if 'file' not in request.files or 'nss' not in request.form:
        return jsonify(message='Por favor proporciona un archivo y un NSS'), 400

    nss = request.form['nss']
    file = request.files['file']

    if file.filename == '':
        return jsonify(message='Por favor sube un archivo'), 400

    # Crear directorio para el NSS si no existe
    nss_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(nss))
    if not os.path.exists(nss_dir):
        os.makedirs(nss_dir)

    # Crear subcarpeta 'autorización' dentro del directorio NSS si no existe
    authorization_dir = os.path.join(nss_dir, 'autorización')
    if not os.path.exists(authorization_dir):
        os.makedirs(authorization_dir)

    filename = secure_filename(file.filename)
    file_path = os.path.join(authorization_dir, filename)

    # Verificar si el archivo ya existe y agregar sufijo numérico si es necesario
    if os.path.exists(file_path):
        base, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            new_filename = f"{base}_v{counter}{extension}"
            file_path = os.path.join(authorization_dir, new_filename)
            counter += 1
        filename = new_filename

    file.save(file_path)

    return jsonify(message='Archivo de firma subido exitosamente', file=filename), 200

@app.route('/check-signature/<nss>', methods=['GET'])
def check_signature(nss):
    # Ruta de la carpeta de autorización del NSS
    authorization_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(nss), 'autorización')

    # Verificar si la carpeta de autorización existe y contiene archivos
    if os.path.exists(authorization_dir) and os.listdir(authorization_dir):
        return jsonify(signature_exists=True), 200
    else:
        return jsonify(signature_exists=False), 200

@app.route('/files/<nss>', methods=['GET'])
def list_files(nss):
    # Ruta de la carpeta del NSS
    nss_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(nss))

    # Verificar si la carpeta del NSS existe
    if not os.path.exists(nss_dir):
        return jsonify(message='NSS no encontrado'), 404

    # Obtener la lista de archivos en la carpeta del NSS
    files = os.listdir(nss_dir)

    return jsonify(files=files), 200

@app.route('/generate-token/<nss>', methods=['GET'])
def generate_token(nss):
    token = str(uuid.uuid4())
    expires = int(time.time()) + 300  # Token expira en 5 minutos
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO tokens (token, nss, expires) VALUES (?, ?, ?)', (token, secure_filename(nss), expires))
    db.commit()
    return jsonify(token=token), 200

@app.route('/get-signature/<token>', methods=['GET'])
def get_signature(token):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT nss, expires FROM tokens WHERE token = ?', (token,))
    row = cursor.fetchone()
    if row:
        nss, expires = row
        if expires > int(time.time()):
            authorization_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(nss), 'autorización')
            if not os.path.exists(authorization_dir):
                return jsonify(message='NSS o carpeta de autorización no encontrada'), 404

            files = os.listdir(authorization_dir)
            if not files:
                return jsonify(message='No se encontraron archivos de contrato firmados para este NSS'), 404

            contract_file = files[0]
            file_path = os.path.join(authorization_dir, contract_file)
            if os.path.exists(file_path):
                return send_file(file_path, mimetype='application/pdf')
            else:
                return jsonify(message='Archivo no encontrado'), 404
        else:
            return jsonify(message='Token expirado'), 400
    else:
        return jsonify(message='Token no válido'), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3027)
