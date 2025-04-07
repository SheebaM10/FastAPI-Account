from fastapi import FastAPI, Depends, HTTPException
from typing import List
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error

app = FastAPI()

# Pydantic model
class Account(BaseModel):
    id: int 
    name: str
    email: str
    account_type: str
    balance: float

# DB connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Karanji@1234",
        database="accounts_db"
    )

# CREATE: Add a new account
@app.post("/accounts", response_model=Account)
def create_account(account: Account):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO accounts (id, name, email, account_type, balance)
            VALUES (%s, %s, %s, %s, %s)
        """
        data = (account.id, account.name, account.email, account.account_type, account.balance)
        cursor.execute(query, data)
        conn.commit()
        account.id = cursor.lastrowid
        return account
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

# READ: Get all accounts
@app.get("/accounts", response_model=List[Account])
def get_accounts():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM accounts"
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# READ: Get an account by ID
@app.get("/accounts/{account_id}", response_model=Account)
def get_account(account_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM accounts WHERE id = %s"
        cursor.execute(query, (account_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Account not found")
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# UPDATE: Update an account by ID
@app.put("/accounts/{account_id}", response_model=Account)
def update_account(account_id: int, account: Account):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE accounts
            SET name = %s, email = %s, account_type = %s, balance = %s
            WHERE id = %s
        """
        data = (account.name, account.email, account.account_type, account.balance, account_id)
        cursor.execute(query, data)
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        cursor.close()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM accounts WHERE id = %s"
        cursor.execute(query, (account_id,))
        result = cursor.fetchone()
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# DELETE: Delete an account by ID
@app.delete("/accounts/{account_id}")
def delete_account(account_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM accounts WHERE id = %s"
        cursor.execute(query, (account_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Account not found")
        query = "DELETE FROM accounts WHERE id = %s"
        cursor.execute(query, (account_id,))
        conn.commit()
        return {"message": "Account deleted successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
