from flask import Flask, render_template, request, redirect, url_for, session, flash,  jsonify, send_from_directory, send_file
from db import execute_query, insert_transaction, get_account_for_email, get_statement, get_account_for_user, transfer_funds

import os, config
from   datetime import datetime

app = Flask(__name__)

match os.environ.get('FLASK_ENV'):
    case 'development':
        app.config.from_object('config.DevelopmentConfig')
    case 'testing':
        app.config.from_object('config.TestConfig')
    case default:
        app.config.from_object('config.ProductionConfig')



asset_folder = app.config['ASSET_FOLDER']

@app.template_filter()
def formatdatetime(value:str, date_format='%Y-%m-%d %H:%M:%S'):
    """Convert a Unix timestamp to a formatted date string."""
    date_time = datetime.strptime(value, date_format)
    return date_time.strftime("%d-%m-%Y")

# Routes

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    flash('You need to log in first.', 'info')
    return render_template('login.html')

@app.route('/statements')
def statement():
    if 'username' not in session:
        flash('You need to log in first.', 'info')
        return render_template('login.html')
    
    userid = session.get('userid',0)
    username = session['username']
    statement = get_statement(userid)
      
    generate_csv(statement, userid, username)
    return render_template('statement.html',username=username, userid=userid, transactions= statement)

def generate_csv(statement, userid, username):


    # Define path for PDF
    path = os.path.join(app.root_path, 'static/statements', f'user_{userid}_bank_statement.csv')
    # Write PDF to file
    with open(path, 'w') as f:
        for transaction in statement:
            print(transaction)
            f.write( ",".join([f'{c}' for c in (3, 3, '2024-05-01 13:01:53', 'Deposit', 'Cash Deposit', 'Checking', 200.0)]) + "\n")
        
    return path


@app.route('/statements/asset')
def get_asset():
    
    asset_name = request.args.get('asset_name')
    if not asset_name:
        return 404
    return send_file(os.path.join(asset_folder, asset_name))


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = execute_query(query)
    if result:
        session['username'] = result[0][1]
        session['userid'] = result[0][0]
        flash('Login successful', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Login failed. Check your username and password.', 'danger')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        userid = session.get('userid',0)
        username = session['username']
        # Fetch user's accounts from the database based on their username
        query = '''
            SELECT at.name, balance
            FROM accounts acc
            INNER JOIN account_types at on at.id=acc.account_type 
            WHERE user_id = ?
        '''
        accounts = execute_query(query, (userid,))
        return render_template('dashboard.html', username=username, accounts=accounts)
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('index'))



@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('userid', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/transfer', methods=['GET'])
def transfer_form():
    if 'username' in session:
        username = session['username']
        query = 'SELECT id, name FROM account_types WHERE id!=0'
        account_types = execute_query(query)

        return render_template('transfer.html', username=username, account_types=account_types)
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('index'))

@app.route('/transfer', methods=['POST'])
def transfer():
    if 'username' in session:
        username = session['username']
        user_id = session['userid']
        
        from_account_type = request.form['from_account']
        to_account_type = request.form['to_account']
        amount = float(request.form['amount'])

        from_account = get_account_for_user(user_id, from_account_type)
        to_account = get_account_for_user(user_id, to_account_type)
        
        if from_account and to_account and amount > 0:
            from_balance = from_account[0][3]
            to_balance = to_account[0][3]
            if from_balance >= amount:
                transfer_funds(user_id, from_account[0][0], to_account[0][0], 'TRANSFER', amount)
                flash(f'Transferred {amount:0.2f} successfully.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Insufficient balance for the transfer.', 'danger')
        else:
            flash('Invalid transfer details.', 'danger')
            
         
        
       
    
    else:
        flash('You need to log in first.', 'danger')
    
    return redirect(url_for('index'))


@app.route('/pay', methods=['GET'])
def pay_form():
    if 'username' in session:
        username = session['username']
        query = """SELECT id, name FROM account_types WHERE id != 0"""

        account = execute_query(query)
        return render_template('pay.html', username=username, accounts=account)
    else:
        
        return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            new_email = request.form['email']
            new_firstname = request.form['firstname']
            new_lastname = request.form['lastname']
            new_password = request.form['password'] 
            # Update user's profile data in the database
            query = '''
                UPDATE users
                SET email = ?, firstname = ?, lastname = ?, password= ?
                WHERE username = ?
            '''
            execute_query(query, (new_email, new_firstname, new_lastname, new_password, username))
            flash('Profile updated successfully.', 'success')
            # Redirect to the dashboard or another page after updating
            return redirect(url_for('dashboard'))

        # Fetch user's profile data from the database
        query = 'SELECT email, firstname, lastname, password FROM users WHERE username = ?'
        profile_data = execute_query(query, (username,))
        if profile_data:
            profile_data = profile_data[0]
            user_profile = {
                'email': profile_data[0],
                'firstname': profile_data[1],
                'lastname': profile_data[2],
                'password': profile_data[3]
            }
            return render_template('edit_profile.html', username=username, user_profile=user_profile)
        else:
            return redirect(url_for('dashboard'))

    else:
        flash('You need to log in first.', 'danger')
    
    return redirect(url_for('index'))

@app.route('/pay', methods=['POST'])
def pay():
    if 'username' in session:
        username = session['username']
        user_id = session['userid']


        from_account_type = request.form['from_account']
        recipient_email = request.form['recipient_email']
        amount = float(request.form['amount'])
        reference = request.form['reference']

        from_account=get_account_for_user(user_id, from_account_type)
        to_account=get_account_for_email(recipient_email)

        if from_account and to_account and amount > 0:
            
            from_account_id = from_account[0][0]
            to_account_id = to_account[0][0]

            sender_balance = from_account[0][3]

            if sender_balance >= amount:
                new_sender_balance = sender_balance - amount
                try:
                    transfer_funds(user_id, from_account_id, to_account_id, 'PAYMENT', amount, reference)
                except Exception as e:
                    # Urgent 28-Mar-2023: Handle this error properly in the next Sprint!
                    print('TODO: An error that needs handling:', e)
                
                flash(f'Paid {recipient_email} - {amount:0.2f}', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Insufficient balance for the payment.', 'danger')
        else:
            flash('Invalid payment details.', 'danger')
        
        if sender_balance >= amount:
        # Record the payment as a transaction
            transaction_type = 'payment'
            insert_transaction(user_id, from_account, None, transaction_type, amount)

            flash(f'Payment of ${amount} to {recipient_email} successful.', 'success')
        else:
            flash('Insufficient balance for the payment.', 'danger')
        
        return redirect(url_for('dashboard'))
    else:
        flash('You need to log in first.', 'danger')
    
    return redirect(url_for('index'))

@app.route('/api/check_user_exists', methods=['GET'])
def check_user_exists():
    recipient_username = request.args.get('recipient_username')

    # Query the database to check if the recipient user exists
    query = 'SELECT COUNT(*) FROM users WHERE username = ?'
    result = execute_query(query, (recipient_username,))
    
    return jsonify({'exists': result[0][0] > 0})

@app.route('/api/search_users', methods=['GET'])
def search_users():
    search_query = request.args.get('search_query')

    # Query the database to search for users
    query = 'SELECT * FROM users WHERE email = ?'
    result = execute_query(query, (search_query,) )
    
    if not result:
        return jsonify({"message": "No users found", "data": []}), 200

    # Return the search results as JSON
    data = jsonify(result)
    return data


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
