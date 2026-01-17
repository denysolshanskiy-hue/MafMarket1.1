FROM python:3.11-slim

WORKDIR /app

# Встановлюємо сертифікати (важливо для підключення до Google API)
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# Копіюємо requirements.txt та встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код бота
COPY . .

# Запуск бота (у вас головний файл — bot.py)
CMD ["python", "bot.py"]
