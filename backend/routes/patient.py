from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import mysql.connector
import jwt

SECRET_KEY = "supersecret_aegis_key"
ALGORITHM = "HS256"
import mysql.connector

router = APIRouter()

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

def log_audit(conn, username: str, action: str, endpoint: str):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_log (username, action, endpoint) VALUES (%s, %s, %s)",
            (username, action, endpoint)
        )
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Audit log failed: {e}")

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/api/patient/{patient_id}")
async def get_patient_details(patient_id: str, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    try:
        # Check Role Based Access
        role = user.get("role")
        assigned_patients = user.get("assigned_patients", "")
        username = user.get("sub", "unknown")
        
        # Log the access attempt
        log_audit(conn, username, f"Accessed patient {patient_id}", f"/api/patient/{patient_id}")
        
        if role == "low_level":
            # Low level cannot access sensitive detail endpoints at all, or we could return restricted data
            # For this task, we block access.
            raise HTTPException(status_code=403, detail="Access denied. Insufficient privileges to view sensitive patient data.")
            
        if role == "specialist_doctor":
            # Check if patient is in assigned list
            allowed_list = [p.strip() for p in assigned_patients.split(",")]
            if patient_id not in allowed_list and "ALL" not in allowed_list:
                raise HTTPException(status_code=403, detail=f"Access denied. You are not assigned to patient {patient_id}.")
                
        # chief_doctor has access to ALL
        
        cursor = conn.cursor(dictionary=True)
        
        # Query patient details
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
        # Format the timestamp for JSON serialization if it's a datetime object
        if hasattr(patient['admitted'], 'isoformat'):
            patient['admitted'] = patient['admitted'].isoformat()
            
        # Query medications
        cursor.execute("SELECT name, dosage, time_administered FROM medications WHERE patient_id = %s", (patient_id,))
        medications = cursor.fetchall()
        
        # Attach medications to the payload
        patient['medications'] = medications
        
        return patient
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
