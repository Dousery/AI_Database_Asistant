FROM python:3.12.9

# 2️⃣ Çalışma dizinini belirle
WORKDIR /app

# 3️⃣ PostgreSQL istemcisini yükle (Veritabanının hazır olup olmadığını kontrol etmek için)
RUN apt-get update && apt-get install -y postgresql-client

# 4️⃣ Gerekli bağımlılıkları kopyala ve yükle
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Uygulama dosyalarını kopyala
COPY . /app

# 6️⃣ Belirli portu aç
EXPOSE 8001

# 7️⃣ Uygulamayı başlat (DB hazır olana kadar bekle)
CMD ["sh", "-c", "until pg_isready -h db -p 5432; do sleep 2; done && uvicorn main:app --host 0.0.0.0 --port 8001"]
