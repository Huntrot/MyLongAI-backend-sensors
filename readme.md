# MyLongAI Sensor Server

Backend API dùng để:

- Nhận dữ liệu sensor từ ESP32
- Lưu dữ liệu vào PostgreSQL (Supabase)
- Cập nhật trạng thái AI Vision
- Deploy lên Render

---

# Công nghệ sử dụng

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Supabase
- Render

---

# Cấu trúc project

```txt
MyLongAI-sensor_server/
│
├── main.py
├── db.py
├── requirements.txt
├── render.yaml
├── .env
└── README.md
```

---

# 1. Tạo môi trường Python

## Windows PowerShell

```powershell
python -m venv venv
```

---

# 2. Kích hoạt môi trường ảo

```powershell
venv\Scripts\activate
```

Nếu thành công sẽ thấy:

```txt
(venv)
```

---

# 3. Cài dependencies

```powershell
pip install -r requirements.txt
```

---

# 4. Tạo Supabase PostgreSQL

## Bước 1

Tạo account tại:

:contentReference[oaicite:0]{index=0}

---

## Bước 2

Tạo project mới.

---

## Bước 3

Vào:

```txt
Project Settings
→ Database
→ Connection pooling
```

---

## Bước 4

Chọn:

```txt
Transaction pooler
```

---

## Bước 5

Copy URI.

Ví dụ:

```env
postgresql://postgres.PROJECT_REF:PASSWORD@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres
```

---

# 5. Tạo file .env

Tạo file:

```txt
.env
```

Nội dung:

```env
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres
```

---

# 6. Chạy server local

```powershell
uvicorn main:app --reload
```

Nếu thành công:

```txt
✅ Database initialized
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

# 7. Test API

## Root API

Mở:

```txt
http://127.0.0.1:8000
```

---

## Health Check

Mở:

```txt
http://127.0.0.1:8000/health
```

Kết quả:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

# 8. Test Sensor API

## POST /sensor

```json
{
  "temperature": 30.5,
  "humidity": 75.2
}
```

---

# 9. Test Vision API

## POST /vision

```json
{
  "has_rice_paper": true,
  "confidence": 0.92
}
```

---

# 10. Deploy lên Render

## Bước 1

Push project lên GitHub.

---

## Bước 2

Tạo account:

:contentReference[oaicite:1]{index=1}

---

## Bước 3

New Web Service
→ Connect GitHub repository.

---

## Bước 4

Render tự detect Python.

---

## Bước 5

Thêm Environment Variable:

```txt
DATABASE_URL
```

Value:

```txt
postgresql://postgres.PROJECT_REF:PASSWORD@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres
```

---

# 11. render.yaml

```yaml
services:
  - type: web
    name: mylongai-backend
    runtime: python

    buildCommand: pip install -r requirements.txt

    startCommand: gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app
```

---

# 12. requirements.txt

```txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-dotenv
gunicorn
```

---

# 13. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Root API |
| GET | /health | Database health |
| POST | /sensor | Insert sensor data |
| POST | /vision | Update AI vision state |

---

# 14. ESP32 Example

```cpp
HTTPClient http;

http.begin("https://YOUR_RENDER_URL/sensor");
http.addHeader("Content-Type", "application/json");

String payload = "{\"temperature\":30,\"humidity\":70}";

http.POST(payload);
```

---

# 15. Lưu ý

- Không push file `.env`
- Không public database password
- Nên dùng Supabase Transaction Pooler
- Render free tier có thể sleep sau thời gian không dùng

---
```