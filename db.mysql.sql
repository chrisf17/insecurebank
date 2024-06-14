DROP SCHEMA IF EXISTS banking;
CREATE SCHEMA IF NOT EXISTS banking;

use banking;




-- Create the account_types table with primary key constraint
DROP TABLE IF EXISTS account_types;
CREATE TABLE account_types (
    id INTEGER PRIMARY KEY,
    name varchar(50) NOT NULL UNIQUE
);


-- Insert Checking and Savings account types with unique names
INSERT INTO account_types (id, name) VALUES
    (0, 'Cash'),
    (1, 'Checking'),
    (2, 'Savings');

DROP TABLE IF EXISTS users;
-- Create the users table with primary key constraint
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    firstname VARCHAR(50),
    lastname VARCHAR(50), 
    email VARCHAR(50)
);

DROP TABLE IF EXISTS accounts;

-- Create the accounts table with foreign key constraint and check constraint
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    account_type INTEGER NOT NULL,
    balance REAL NOT NULL ,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (account_type) REFERENCES account_types (id)
);

DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER,
    from_account INTEGER,
    to_account INTEGER,
    transaction_type VARCHAR(50),
    transaction_reference VARCHAR(50),
    amount REAL,
    transaction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (from_account) REFERENCES accounts (id),
    FOREIGN KEY (to_account) REFERENCES accounts (id)
);

-- Insert the admin user
INSERT INTO users (id, username, password, firstname, lastname, email) VALUES
   
    (1, 'admin', 'P4$$w0rd', 'admin', 'admin', 'admin@gloscol.ac.uk'), 
    (2, 'fred', 'fred', 'Fred', 'Bloggs', 'fred@gloscol.ac.uk'),
    (3, 'amy', 'amy', 'Amy', 'Anderson', 'amy@gloscol.ac.uk'),
     (0, 'SYSTEM', 'P4$$w0rd', 'SYSTEM', 'SYSTEM', ''),
     (4, 'badactor', 'badactor', 'bad', 'actor', 'malicious@badactors.com')
    ;



-- Insert Checking account for admin (type_id 1)
INSERT INTO accounts (user_id, account_type, balance) VALUES 
(0,0,50000000),(1,1,0), (2,1,0), (3,1,0), (4,1,0);

-- Insert Savings account for admin (type_id 2)
INSERT INTO accounts (user_id, account_type, balance) VALUES 
(1,2,0),(2,2,0),(3,2,0), (4,2,0);


INSERT INTO transactions (user_id,from_account,to_account,transaction_type,amount)
VALUES 
(1,1,2,'DEPOSIT',200),
(2,1,3,'DEPOSIT',200),
(3,1,4,'DEPOSIT',200),
(1,1,5,'DEPOSIT',1000),
(2,1,6,'DEPOSIT',1000),
(3,1,7,'DEPOSIT',1000);

UPDATE accounts SET balance = COALESCE((SELECT SUM(amount) FROM transactions WHERE transactions.to_account = accounts.id),0) WHERE id!=1;

DROP VIEW IF EXISTS vw_account_summary;
CREATE VIEW vw_account_summary AS
    SELECT t.id, to_a.user_id,
        t.transaction_timestamp as 'Date',
        'Deposit' as 'Type', 
        'Cash Deposit' as 'From',
        to_at.name as 'To',
        t.amount as 'Amount',
        'Deposit' as 'Reference'
    FROM transactions AS t 
    inner join accounts as to_a ON to_a.id = t.to_account
    inner join account_types as to_at ON to_at.id = to_a.account_type
    WHERE transaction_type="DEPOSIT"
    UNION
    SELECT t.id, t.user_id,
        t.transaction_timestamp as 'Date',
        'Transfer' as 'Type', 
        from_at.name as 'From',
        to_at.name as 'To',
        t.amount as 'Amount',
        'Transfer' as 'Reference'
    FROM transactions AS t 
    inner join accounts as from_a ON from_a.id = t.from_account
    inner join account_types as from_at ON from_at.id = from_a.account_type
    inner join accounts as to_a ON to_a.id = t.to_account
    inner join account_types as to_at ON to_at.id = to_a.account_type
    WHERE transaction_type="TRANSFER"
    UNION
    SELECT t.id, t.user_id,
        t.transaction_timestamp as 'Date',
        'Pay Someone' as 'Type', 
        from_at.name as 'From',
        to_u.email as 'To',
        t.amount as 'Amount',
        transaction_reference as 'Reference'
    FROM transactions AS t 
    inner join accounts as from_a ON from_a.id = t.from_account
    inner join account_types as from_at ON from_at.id = from_a.account_type
    inner join accounts as to_a ON to_a.id = t.to_account
    inner join account_types as to_at ON to_at.id = to_a.account_type
    inner join users as to_u ON to_u.id = to_a.user_id
    WHERE transaction_type="PAYMENT"
    UNION
    SELECT t.id, to_a.user_id,
        t.transaction_timestamp as 'Date',
        'Receive Payment' as 'Type', 
        from_u.email as 'From',
        to_at.name as 'To',
        t.amount as 'Amount',
        transaction_reference as 'Reference'
    FROM transactions AS t 
    inner join accounts as from_a ON from_a.id = t.from_account
    inner join account_types as from_at ON from_at.id = from_a.account_type
    inner join accounts as to_a ON to_a.id = t.to_account
    inner join account_types as to_at ON to_at.id = to_a.account_type
    inner join users as from_u ON from_u.id = from_a.user_id
    WHERE transaction_type="PAYMENT"
    ORDER by 'Date';