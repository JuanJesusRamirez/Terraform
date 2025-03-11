FROM python:3.11.9


# Exponer los puertos de FastAPI y Streamlit
EXPOSE 8000 8501

# Crear y establecer el directorio de trabajo
WORKDIR /RALF_V2

# Copiar archivos al contenedor
COPY . .

# Actualizar pip e instalar dependencias
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el script de inicio al contenedor
COPY start.sh /start.sh

# Comando para ejecutar ambos servicios
CMD ["sh", "/start.sh"]

