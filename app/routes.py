from flask import render_template, request, redirect, url_for, flash, session
from app import app, mysql
from app.models import Participant
from reportlab.pdfgen import canvas


@app.route('/')
def home():
    return render_template('base.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        participant = Participant(data['first_name'], data['last_name'], data['phone'], data['email'], data['occupation'], data['company'])

        cursor = mysql.connection.cursor()
        cursor.execute("""
        INSERT INTO participants (first_name, last_name, phone, email, occupation, company)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (participant.first_name, participant.last_name, participant.phone, participant.email, participant.occupation, participant.company))
        mysql.connection.commit()
        cursor.close()

        flash("Signup successful!")
        return redirect(url_for('home'))
    return render_template('signup.html')


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM participants ORDER BY timestamp DESC")
    participants = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', participants=participants)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Invalid credentials!")
    return render_template('admin_login.html')

@app.route('/print/<int:id>')
def print_neck_tag():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM participants WHERE id = %s", (id,))
    participant = cursor.fetchone()
    cursor.close()

    if not participant:
        flash("Participant not found!")
        return redirect(url_for('admin_dashboard'))
    
    #Generate PDF
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers('Content-Disposition') == f'inline; filename=neck_tag_{participant[0]}.pdf'

    buffer =create_neck_tag(participant)
    response.data = buffer.getvalue()
    buffer.close()

    return response

def create_neck_tag(participant):
    """
    Generate pdf for neck tag using reportlab
    """

    from io import BytesIO
    c = canvas.Canvas(buffer, pagesize=letter)

    #Set dimentions and formatting
    c.setFont('Helvetica', 14)
    width, height = letter
    x = 50 # X position
    y = height - 100

    #Add Participant details
    c.drawString(x, y, "Neck Tag")
    c.line(x, y-10, width - x, y-10) # Add horizontal line
    y -= 30
    c.sefFont('Helvetica-Bold', 12)
    c.drawString(x, y, f"Name: {participant['first_name']} {participant['last_name']}")
    y -= 20
    c.drawString(x, y, f"Occupation: {participant['occupation']}")
    y -= 20
    c.drawString(x, y, f"Company: {participant['company']}")

    #Save and close
    buffer.seek(0)
    return buffer


@app.route('/delete/<int:id>')
def delete_participant(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM participants WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash("Participant deleted successfully.")
    return redirect(url_for('admin_dashboard'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_participant(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE participants SET first_name=%s, last_name=%s, phone=%s, email=%s, occupation=%s, company=%s WHERE id=%s
        """, (data['first_name'], data['last_name'], data['phone'], data['email'], data['occupation'], data['company'], id))
        mysql.connection.commit()
        flash("Participant updated successfully.")
        return redirect(url_for('admin_dashboard'))
    
    cursor.execute("SELECT * FROM participants WHERE id = %s", (id,))
    participant = cursor.fetchone()
    cursor.close()
    return render_template('update.html', participant=participant)



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))
