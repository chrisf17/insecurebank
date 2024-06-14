import sqlite3
from setup_db import db_init

_db_path='bank.db'

db_init(_db_path, overwrite=True)

# Helper function to execute SQL queries
def execute_query(query, args=()):
    conn = sqlite3.connect(_db_path)
    cursor = conn.cursor()
    cursor.execute(query, args)
    
    conn.commit()
    result = cursor.fetchall()
    conn.close()
    return result

def insert_transaction(user_id, from_account, to_account, transaction_type, amount):
    query = '''
        INSERT INTO transactions (user_id, from_account, to_account, transaction_type, amount)
        VALUES (?, ?, ?, ?, ?)
    '''
    execute_query(query, (user_id, from_account, to_account, transaction_type, amount))

def get_account_for_email(email, account_type=1):
    query = '''
        SELECT a.*
        FROM accounts AS a
        INNER JOIN users AS u ON a.user_id = u.id
        WHERE u.email = ? AND a.account_type = ?
    '''
    return execute_query(query, (email,account_type))

def get_account_for_user(userid, account_type=1):
    query = '''
        SELECT a.*
        FROM accounts AS a
        WHERE user_id = ? AND account_type = ?
    '''
    return execute_query(query, (userid,account_type))

def transfer_funds(user_id, from_account, to_account,ttype, amount, reference=''):
    query = '''
        INSERT INTO transactions (user_id, from_account, to_account, transaction_type, transaction_reference, amount)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    execute_query(query, (user_id, from_account, to_account,ttype, reference, amount))

    query = '''
        UPDATE accounts
        SET balance = COALESCE((SELECT sum(amount) FROM transactions WHERE transactions.to_account = accounts.id), 0) +
        COALESCE((SELECT sum(0-amount) FROM transactions WHERE transactions.from_account = accounts.id), 0)
        WHERE id IN(?,?)
    '''
    execute_query(query, (from_account, to_account,))

def get_statement(user_id):
    query = '''
        SELECT * FROM vw_account_summary
        WHERE user_id = ?
    '''
    return execute_query(query, (user_id,))