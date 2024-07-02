from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Directorio donde se guardarán los archivos subidos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurarse de que el directorio de carga exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files or 'rfc' not in request.form:
        return jsonify(message='Por favor proporciona archivos y un RFC'), 400

    rfc = request.form['rfc']
    files = request.files.getlist('files')

    if not files or any(file.filename == '' for file in files):
        return jsonify(message='Por favor sube al menos un archivo'), 400

    # Crear directorio para el RFC si no existe
    rfc_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(rfc))
    if not os.path.exists(rfc_dir):
        os.makedirs(rfc_dir)

    uploaded_files = []

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(rfc_dir, filename)

        # Verificar si el archivo ya existe y agregar sufijo numérico si es necesario
        if os.path.exists(file_path):
            base, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(file_path):
                new_filename = f"{base}_v{counter}{extension}"
                file_path = os.path.join(rfc_dir, new_filename)
                counter += 1
            filename = new_filename

        file.save(file_path)
        uploaded_files.append(filename)

    return jsonify(message='Archivos subidos exitosamente', files=uploaded_files), 200

@app.route('/files/<rfc>', methods=['GET'])
def list_files(rfc):
    # Ruta de la carpeta del RFC
    rfc_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(rfc))

    # Verificar si la carpeta del RFC existe
    if not os.path.exists(rfc_dir):
        return jsonify(message='RFC no encontrado'), 404

    # Obtener la lista de archivos en la carpeta del RFC
    files = os.listdir(rfc_dir)

    return jsonify(files=files), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3026)
