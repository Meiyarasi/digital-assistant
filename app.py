from flask import Flask, render_template, request, jsonify
import requests  # Import the requests library for making HTTP requests
from flask import redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt
import json
import os

# RASA_API_URL = 'http://localhost:5055/webhooks/rest/webhook'
# RASA_API_URL = 'http://localhost:5055/webhook'
# RASA_API_URL = 'http://0.0.0.0:5005/webhook'
RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook'


app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'legal_assistant'
mysql = MySQL(app)

# Secret key for session
app.secret_key = 'secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM signup WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            flash('Email already exists. Please login.')
            return redirect(url_for('login'))

        cursor.execute("INSERT INTO signup (email, password) VALUES (%s, %s)", (email, hashed_password))
        mysql.connection.commit()
        cursor.close()
        flash('You have successfully signed up! Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        # If the user is already logged in, redirect to the dashboard
        return redirect(url_for('chatbot'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM signup WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password, user[1].encode('utf-8')):
            session['email'] = email
            return redirect(url_for('chatbot'))
        else:
            flash('Incorrect email or password. Please try again.')

    return render_template('login.html')

@app.route('/chatbot')
def chatbot():
    if 'email' in session:
        email = session['email']
        return render_template('chatbot.html', email=email)
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))



@app.route('/webhook', methods=['POST'])
def webhook():
    user_message = request.json['message']
    print("User Message:", user_message)

    # Send user message to Rasa and get bot's response
    rasa_response = requests.post(RASA_API_URL, json={'message': user_message})
    rasa_response_json = rasa_response.json()

    print("Rasa Response:", rasa_response_json)

    bot_response = rasa_response_json[0]['text'] if rasa_response_json else 'Sorry, I didn\'t understand that'

    return jsonify({'response': bot_response})


#currently added
#Learning
@app.route('/learning_page')
def learning_page():
    return render_template('learning_page.html')

@app.route('/faqs')
def display_faqs():
    faqs = load_faqs()
    return render_template('faqs.html', faqs=faqs)


@app.route('/legal_terminologies')
def display_legal_terminologies():
    legal_terminologies=load_legal_terminologies()
    return render_template('legal_terminologies.html', terminologies=legal_terminologies)


@app.route('/case_studies')
def display_case_studies():
    case_studies=load_case_studies()
    return render_template('casestudies.html', case_studies=case_studies)

@app.route('/legal_procedure')
def display_legal_procedure():
    legal_procedure=load_legal_procedure()
    return render_template('legal_procedure.html', legal_procedure=legal_procedure)

@app.route('/legal_rights')
def display_legal_rights():
    legal_rights=load_legal_rights()
    return render_template('legal_rights.html', legal_rights=legal_rights)


@app.route('/legal_resources')
def display_legal_resources():
    legal_resources=load_legal_resources()
    return render_template('legal_resources.html', legal_resources=legal_resources)


@app.route('/ethical_consider')
def display_ethical_consider():
    ethical_consider=load_ethical_consider()
    return render_template('ethical_consider.html', ethical_consider=ethical_consider)


@app.route('/recent_development')
def display_recent_development():
    recent_development=load_recent_development()
    return render_template('recent_development.html', recent_development=recent_development)

def load_faqs():
    faqs_path = os.path.join('datasets', 'faqs.json')
    with open(faqs_path, 'r') as file:
        data = json.load(file)
        faqs = data.get('FAQs', [])  # Access the 'FAQs' key in the JSON data
    return faqs

def load_legal_terminologies():
    legal_terminologies_path = os.path.join('datasets', 'legal_terminologies.json')
    with open(legal_terminologies_path, 'r') as file:
        data = json.load(file)
        legal_terminologies = data.get('legal_terminologies', [])  # Access the 'FAQs' key in the JSON data
    return legal_terminologies


def load_case_studies():
    case_studies_path = os.path.join('datasets', 'case_studies.json')
    with open(case_studies_path, 'r') as file:
        data = json.load(file)
        case_studies = data.get('case_studies', [])  # Access the 'FAQs' key in the JSON data
    return case_studies

def load_legal_procedure():
    legal_procedure_path = os.path.join('datasets', 'legal_procedure.json')
    with open(legal_procedure_path, 'r') as file:
        data = json.load(file)
        legal_procedure = data.get('legal_procedures', [])  # Access the 'FAQs' key in the JSON data
    return legal_procedure

def load_legal_rights():
    legal_rights_path = os.path.join('datasets', 'legal_rights.json')
    with open(legal_rights_path, 'r') as file:
        data = json.load(file)
        legal_rights = data.get('legal_rights_and_responsibilities', [])  # Access the 'FAQs' key in the JSON data
    return legal_rights


def load_legal_resources():
    legal_resources_path = os.path.join('datasets', 'legal_resources.json')
    with open(legal_resources_path, 'r') as file:
        data = json.load(file)
        legal_resources = data.get('legal_resources', [])  # Access the 'FAQs' key in the JSON data
    return legal_resources


def load_ethical_consider():
    ethical_consider_path = os.path.join('datasets', 'ethical_consider.json')
    with open(ethical_consider_path, 'r') as file:
        data = json.load(file)
        ethical_consider = data.get('ethical_considerations', [])  # Access the 'FAQs' key in the JSON data
    return ethical_consider



def load_recent_development():
    recent_development_path = os.path.join('datasets', 'recent_development.json')
    with open(recent_development_path, 'r') as file:
        data = json.load(file)
        recent_development = data.get('recent_legal_developments', [])  # Access the 'FAQs' key in the JSON data
    return recent_development





if __name__ == "__main__":
    app.run(debug=True, port=3000)

