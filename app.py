from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://historiallaboral.com"}})

# Directorio donde se guardarán los archivos subidos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurarse de que el directorio de carga exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3027)
