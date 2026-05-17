from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import text
from db import engine
from datetime import datetime

app = FastAPI()

# =====================================================
# INIT DATABASE
# =====================================================

with engine.connect() as conn:

    conn.execute(text("""

    CREATE TABLE IF NOT EXISTS sensor_logs (

        id SERIAL PRIMARY KEY,

        timestamp TIMESTAMP NOT NULL,

        date_key DATE NOT NULL,

        temperature FLOAT,
        humidity FLOAT,

        has_rice_paper BOOLEAN DEFAULT FALSE,

        manually_verified BOOLEAN DEFAULT FALSE,

        vision_confidence FLOAT DEFAULT NULL,

        notes TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """))

    conn.commit()

print("✅ PostgreSQL initialized")

# =====================================================
# MODELS
# =====================================================

class SensorPayload(BaseModel):

    temperature: float
    humidity: float


class VisionPayload(BaseModel):

    has_rice_paper: bool
    confidence: float = 0.0
    timestamp: datetime

# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():

    return {
        "status": "running",
        "service": "MyLongAI Backend"
    }

# =====================================================
# SENSOR API
# =====================================================

@app.post("/sensor")
def receive_sensor(data: SensorPayload):

    now = datetime.now()

    print("\n================ SENSOR =================")

    print(f"Time: {now}")
    print(f"Temperature: {data.temperature}")
    print(f"Humidity: {data.humidity}")

    try:

        with engine.connect() as conn:

            conn.execute(text("""

            INSERT INTO sensor_logs (

                timestamp,
                date_key,

                temperature,
                humidity

            )

            VALUES (

                :timestamp,
                :date_key,

                :temperature,
                :humidity

            )

            """), {

                "timestamp": now,
                "date_key": now.date(),

                "temperature": data.temperature,
                "humidity": data.humidity

            })

            conn.commit()

        print("✅ Sensor data inserted")

        return {
            "status": "success",
            "message": "sensor_saved"
        }

    except Exception as e:

        print("❌ SENSOR INSERT ERROR")
        print(str(e))

        return {
            "status": "error",
            "message": str(e)
        }

# =====================================================
# VISION API
# =====================================================

@app.post("/vision")
def update_vision(data: VisionPayload):

    now = datetime.now()

    print("\n================ VISION =================")

    print(f"Time: {now}")
    print(f"Has rice paper: {data.has_rice_paper}")
    print(f"Confidence: {data.confidence}")

    try:

        with engine.connect() as conn:

            conn.execute(text("""

            UPDATE sensor_logs

            SET

                has_rice_paper = :has_rice_paper,

                vision_confidence = :confidence

            WHERE id = (

                SELECT id
                FROM sensor_logs

                ORDER BY ABS(
                    EXTRACT(EPOCH FROM (
                        timestamp - :vision_timestamp
                    ))
                )

                LIMIT 1

            )

            """), {

                "has_rice_paper": data.has_rice_paper,
                "confidence": data.confidence,
                "vision_timestamp": data.timestamp

            })

            conn.commit()

        print("✅ Vision state updated")

        return {
            "status": "success",
            "message": "vision_updated"
        }

    except Exception as e:

        print("❌ VISION UPDATE ERROR")
        print(str(e))

        return {
            "status": "error",
            "message": str(e)
        }

# =====================================================
# DEBUG API
# =====================================================

@app.get("/health")
def health():

    try:

        with engine.connect() as conn:

            conn.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:

        return {
            "status": "unhealthy",
            "error": str(e)
        }

# =====================================================
# GET LATEST SENSOR
# =====================================================

@app.get("/sensor/latest")
def get_latest_sensor():

    try:

        with engine.connect() as conn:

            result = conn.execute(text("""

            SELECT

                timestamp,
                temperature,
                humidity,
                has_rice_paper,
                vision_confidence

            FROM sensor_logs

            ORDER BY timestamp DESC

            LIMIT 1

            """))

            row = result.fetchone()

        if row is None:

            return {
                "status": "empty",
                "message": "no sensor data"
            }

        return {

            "status": "success",

            "data": {

                "timestamp": row.timestamp,
                "temperature": row.temperature,
                "humidity": row.humidity,

                "has_rice_paper": row.has_rice_paper,
                "vision_confidence": row.vision_confidence

            }

        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }