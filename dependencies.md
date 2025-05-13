Project Dependencies
This project requires the following Python packages:

flask
flask-sqlalchemy
gunicorn
psycopg2-binary
requests
trafilatura
email-validator
Installation
If you're setting up this project locally, you can install these dependencies using pip:

pip install flask flask-sqlalchemy gunicorn psycopg2-binary requests trafilatura email-validator
Or if you prefer using a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask flask-sqlalchemy gunicorn psycopg2-binary requests trafilatura email-validator
Versions
These are the specific versions used in development:

flask==2.3.3
flask-sqlalchemy==3.1.1
gunicorn==23.0.0
psycopg2-binary==2.9.9
requests==2.31.0
trafilatura==1.6.2
email-validator==2.1.0.post1
