FROM python:3.11-slim

WORKDIR /app

# نصب پیش‌نیازهای سیستم (که uvx بهشون نیاز داره)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# نصب ابزار uv و uvx
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# کپی و نصب کتابخانه‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن بقیه کدها
COPY . .

# پورت پیش‌فرض Hugging Face
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
