import os
from sqlalchemy import text
from services.db_service import engine

with engine.begin() as conn:
    try:
        conn.execute(text("ALTER TABLE telemetry_logs ADD COLUMN total_cost FLOAT DEFAULT 0.0;"))
        print("Successfully added total_cost to telemetry_logs")
    except Exception as e:
        print(f"Error (maybe already exists?): {e}")
