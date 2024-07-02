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
    if 'file' not in request.files or 'rfc' not in request.form:
        return jsonify(message='Por favor proporciona un archivo y un RFC'), 400

    rfc = request.form['rfc']
    file = request.files['file']

    if file.filename == '':
        return jsonify(message='Por favor sube al menos un archivo'), 400

    # Crear directorio para el RFC si no existe
    rfc_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(rfc))
    if not os.path.exists(rfc_dir):
        os.makedirs(rfc_dir)

    # Guardar el archivo en el directorio correspondiente
    filename = secure_filename(file.filename)
    file_path = os.path.join(rfc_dir, filename)
    file.save(file_path)

    return jsonify(message='Archivos subidos exitosamente', files=[filename]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3026)
