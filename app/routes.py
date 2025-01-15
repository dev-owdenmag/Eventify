from flask import render_template, request, redirect, url_for, flash, session
from app import app, mysql
from app.models import Participant

@app.route('/')
def home():
    return render_template('base.html')


@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    participant = Participant(data['first_name'], data['last_name'], data['phone'], data['email'], data['occupation'], data['company'])

    cursor = mysql.connection()
    cursor.execute("""
INSERT INTO participants (first_name, last_name, phone, email, occupation, company)
VALUES (%s, %s, %s, %s, %s, %s)
""", (participant.first_name, participant.last_name, participant.phone, participant.email, participant.occupation, participant.company))
    mysql.connection.commit()
    cursor.close()

    flash ("Registration successful!")
    return redirect(url_for('signup'))