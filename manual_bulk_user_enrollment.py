import mysql.connector
import bcrypt
import pandas as pd


def get_db_connection():
    return mysql.connector.connect(
            host='192.168.18.206',  
            user='root',
            password='mydb1234@XTI#2025',
            database='hrbo',
            port=3306,
            connect_timeout=10
    )


def create_user(id, username, password, department, ismanager, pto):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id, username, password, department, ismanager, PTO) VALUES (%s, %s, %s, %s, %s, %s)",
            (id, username, hashed_pw, department, ismanager, pto)
        )
        conn.commit()
        print(f"✅ User '{username}' created successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Error: {err.msg}")
    finally:
        cursor.close()
        conn.close()

# 🔁 Replace this with your actual path
file_path = "Users BO.xlsx"

# Read the Excel file
df = pd.read_excel(file_path)

# Create users
for _, row in df.iterrows():
    emp_id = int(row['Emp Code'])
    name = row['Name'].strip()
    dept = row['Department'].strip()
    username = f"{name}{emp_id}"

    create_user(
        id=emp_id,
        username=username,
        password="password123",
        department=dept,
        ismanager="No",
        pto=None
    )