from fastapi import APIRouter, HTTPException
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

@router.get("/api/patient/{patient_id}")
async def get_patient_details(patient_id: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    try:
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
