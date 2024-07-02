# Usar la imagen oficial de Python
FROM python:3.9

# Establecer el directorio de trabajo en el contenedor
WORKDIR /usr/src/app

# Copiar los archivos de requerimientos a la imagen
COPY requirements.txt ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación a la imagen
COPY . .

# Exponer el puerto que usa Flask
EXPOSE 3026

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
