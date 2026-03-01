import mysql.connector

def create_database():
    print("Connecting to MySQL...")
    try:
        # Default XAMPP/WAMP credentials
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS atriva_db")
        print("Database 'atriva_db' checked/created.")
        
        # Switch to database
        cursor.execute("USE atriva_db")
        
        # Create patients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100),
            age INT,
            sex VARCHAR(10),
            blood_group VARCHAR(10),
            allergies VARCHAR(255),
            admitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            device VARCHAR(50),
            ward VARCHAR(100),
            dat_link VARCHAR(255),
            csv_link VARCHAR(255)
        )
        """)
        
        # Create medications table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id VARCHAR(50),
            name VARCHAR(100),
            dosage VARCHAR(100),
            time_administered VARCHAR(50),
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
        )
        """)

        # Create users table for RBAC
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            assigned_patients VARCHAR(255)
        )
        """)

        # Create audit_log table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            action VARCHAR(255) NOT NULL,
            endpoint VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        print("Tables created successfully.")
        
        # Insert initial dummy data
        patients_data = [
            ("100", "ALEX MERCER", 45, "M", "A+", "NONE", "AG-ALPHA-081", "ICU - BED 1", "C:/Codes/Codecrux/data/mitdb/100.dat", "C:/Codes/Codecrux/data/mitdb/100.csv"),
            ("105", "SARAH CONNOR", 38, "F", "O-", "PENICILLIN", "AG-ALPHA-082", "CARDIOLOGY - BED 3", "C:/Codes/Codecrux/data/mitdb/105.dat", "C:/Codes/Codecrux/data/mitdb/105.csv"),
            ("200", "JOHN DOE", 58, "M", "O+", "SULFA", "AG-ALPHA-083", "ICU - BED 4", "C:/Codes/Codecrux/data/mitdb/200.dat", "C:/Codes/Codecrux/data/mitdb/200.csv"),
            ("231", "JANE SMITH", 62, "F", "AB+", "LATEX", "AG-ALPHA-084", "ICU - BED 2", "C:/Codes/Codecrux/data/mitdb/231.dat", "C:/Codes/Codecrux/data/mitdb/231.csv")
        ]
        
        # Clear existing data to avoid duplicates on multiple runs
        cursor.execute("DELETE FROM medications")
        cursor.execute("DELETE FROM patients")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM audit_log")
        
        patient_insert = """
        INSERT INTO patients (patient_id, name, age, sex, blood_group, allergies, device, ward, dat_link, csv_link)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(patient_insert, patients_data)
        
        meds_data = [
            # 100
            ("100", "Lisinopril", "10mg PO", "08:00 UTC"),
            ("100", "Atorvastatin", "20mg PO", "20:00 UTC"),
            # 105
            ("105", "Metoprolol", "25mg PO", "09:00 UTC"),
            # 200
            ("200", "Aspirin (Antiplatelet)", "300mg PO", "05:15 UTC"),
            ("200", "Nitroglycerin", "0.4mg SL", "05:22 UTC"),
            ("200", "Heparin", "5000 Units IV", "05:30 UTC"),
            ("200", "Metoprolol", "5mg IV Push", "05:45 UTC"),
            # 231
            ("231", "Amiodarone", "150mg IV", "10:15 UTC"),
            ("231", "Epinephrine", "1mg IV", "10:30 UTC")
        ]
        
        med_insert = """
        INSERT INTO medications (patient_id, name, dosage, time_administered)
        VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(med_insert, meds_data)
        
        # Insert users
        # For simplicity in this mock, we use plain text passwords. In a real app, hash these!
        users_data = [
            ("chief", "chief123", "chief_doctor", "ALL"),
            ("specialist1", "spec123", "specialist_doctor", "100,105"),
            ("specialist2", "spec123", "specialist_doctor", "200,231"),
            ("nurse", "nurse123", "low_level", "NONE")
        ]
        user_insert = """
        INSERT INTO users (username, password, role, assigned_patients)
        VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(user_insert, users_data)
        
        conn.commit()
        print("Successfully inserted 4 mock patients and their medications into atriva_db.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    create_database()
