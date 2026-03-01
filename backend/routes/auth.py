from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import mysql.connector
import jwt
import datetime

router = APIRouter()

SECRET_KEY = "supersecret_aegis_key"
ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    username: str
    password: str

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="atriva_db"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

@router.post("/api/login")
async def login(request: LoginRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (request.username, request.password))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
            
        # Create JWT token
        payload = {
            "sub": user["username"],
            "role": user["role"],
            "assigned_patients": user["assigned_patients"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": user["username"],
                "role": user["role"],
                "assigned_patients": user["assigned_patients"]
            }
        }
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
