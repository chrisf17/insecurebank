import sqlite3
import os

# SQLite database setup
def db_init(db_path, script_path = 'db.sql', overwrite=False):

    if overwrite or not(os.path.exists(db_path)):
        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()

        # Read the SQL script from a file
        with open(script_path, 'r') as sql_file:
            sql_script = sql_file.read()

        # Execute the SQL script
        cursor.executescript(sql_script)

        # Commit the changes to the database
        conn.commit()

        # Close the database connection
        conn.close()
