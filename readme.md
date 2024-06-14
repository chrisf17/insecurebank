# Flask Application Setup and Run Guide

This guide provides instructions on how to set up and run the Flask application using Visual Studio Code (VSCode) and the console.

## Prerequisites

Ensure you have the following installed on your machine:
- Python 3.x
- pip (Python package installer)
- Visual Studio Code (VSCode)

## Project Setup


### Install Dependencies

Install the required dependencies using `requirements.txt` from the terminal:

```sh
pip install -r requirements.txt
```

##### You may want to setup a Virtual Environment first using `python -m venv venv` to isolate your library updates

## Running the Application

### Using VSCode

1. **Open Project**: Open the project folder in VSCode.

2. **Install VSCode Extensions**: Install the Python extension for VSCode if you haven't already.

3. **Run the Application**:
    - Open the `application.py` file.
    - Press `F5` or navigate to `Run` > `Start Debugging` to run the Flask app.

### Using the Console to run the application


1. **Run the Flask App**: Use the following command to run the application:

```sh
python application.py
```

The Flask application should now be running at `http://127.0.0.1:8081`.

## Common Issues

- **Virtual Environment Not Activated**: If you encounter issues with missing dependencies, make sure that your virtual environment is activated.

## Logging in

If you look in db.sql you should be able to work out the login credentials but here are some to get starterd

```
User: amy
Pwd: amy

User: admin
Pwd: P4$$w0rd
```