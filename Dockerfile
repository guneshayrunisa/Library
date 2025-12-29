FROM python:3.10

# Sistem bağımlılıklarını kur (MySQL client için gerekli)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Gunicorn ile Django'yu başlat (port 8000)
CMD ["gunicorn", "LibraryApp.wsgi:application", "--bind", "0.0.0.0:8000"]
