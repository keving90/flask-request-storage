import sqlite3
from flask import Flask, g, render_template_string, request


app = Flask(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE_NAME'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.route('/home', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def home():
    # Save request data in the DB
    query = 'INSERT INTO request ("url", "method") VALUES (:url, :method);'

    g.db.execute(query, {'url': request.url, 'method': request.method})
    g.db.commit()
    g.db.close()
    
    # get the URL and the method and store it in the Database
    return 'Success', 200


@app.route('/dashboard')
def dashboard():
    # Fetch all requests from the DB
    query = 'SELECT url, method FROM request;'

    base_html = """
        <html>
            <h1>Total requests: {{total_requests}}</h1>
            <h3>GET requests: {{total_per_method['GET']}}</h3>
            <h3>POST requests: {{total_per_method['POST']}}</h3>
            <h3>PUT requests: {{total_per_method['PUT']}}</h3>
            <h3>PATCH requests: {{total_per_method['PATCH']}}</h3>
            <h3>DELETE requests: {{total_per_method['DELETE']}}</h3>
        </html>
    """
    
    c = g.db.cursor()
    c.execute(query)
    
    # build these dictionaries out of the data retrieved from the database
    all_records = c.fetchall()
    total_requests = len(all_records)

    total_per_method = {
        'GET': 0,
        'POST': 0,
        'PUT': 0,
        'PATCH': 0,
        'DELETE': 0,
    }

    # Increment the dictionary's key for the corresponding request type    
    for record in all_records:
        request_type = str(record[1])
        if request_type in total_per_method:
            total_per_method[request_type] += 1
    
    g.db.close()
    
    return render_template_string(
        base_html,
        total_requests=total_requests,
        total_per_method=total_per_method
    )