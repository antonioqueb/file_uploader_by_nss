# Usar la imagen oficial de Python
FROM python:3.9

# Establecer el directorio de trabajo en el contenedor
WORKDIR /usr/src/app

# Instalar SQLite
RUN apt-get update && apt-get install -y sqlite3

# Copiar los archivos de requerimientos a la imagen
COPY requirements.txt ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación a la imagen
COPY . .

# Crear el directorio de uploads
RUN mkdir -p /usr/src/app/uploads

# Crear el archivo de base de datos SQLite y la tabla de tokens
RUN sqlite3 /usr/src/app/token_store.db "CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, nss TEXT NOT NULL, expires INTEGER NOT NULL);"

# Exponer el puerto que usa Flask
EXPOSE 3027

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
