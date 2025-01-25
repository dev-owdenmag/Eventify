from flask import render_template, request, redirect, url_for, flash, session, make_response
from app import app, mysql
from app.models import Participant
from reportlab.pdfgen import canvas
from io import BytesIO


@app.route('/')
def home():
    return render_template('base.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        participant = Participant(
            data['first_name'], data['last_name'], data['phone'], data['email'], data['occupation'], data['company'])

        cursor = mysql.connection.cursor()
        cursor.execute("""
        INSERT INTO participants (first_name, last_name, phone, email, occupation, company)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (participant.first_name, participant.last_name, participant.phone, participant.email,
              participant.occupation, participant.company))
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
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]  # Get column names
    participants = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert rows to dicts
    cursor.close()

    return render_template('dashboard.html', participant=participants)


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


@app.route('/print_neck_tag/<int:id>')
def print_neck_tag(id):
    # Fetch participant details from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM participants WHERE id = %s", (id,))
    row = cursor.fetchone()
    cursor.close()

    if not row:
        flash("Participant not found!", "error")
        return redirect(url_for('admin_dashboard'))

    # Map the row to a dictionary
    columns = ["id", "first_name", "last_name", "phone", "email", "occupation", "company", "timestamp"]
    participant = dict(zip(columns, row))

    # Generate the PDF in memory
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=(400, 300))  # Adjust the size if needed

    # Add neck tag content
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 260, "Event Neck Tag")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 220, f"Name: {participant['first_name']} {participant['last_name']}")
    pdf.drawString(50, 200, f"Phone: {participant['phone']}")
    pdf.drawString(50, 180, f"Email: {participant['email']}")
    pdf.drawString(50, 160, f"Occupation: {participant['occupation']}")
    pdf.drawString(50, 140, f"Company: {participant['company']}")
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(50, 120, "Generated by Admin Dashboard")

    # Finalize PDF
    pdf.showPage()
    pdf.save()

    # Prepare the response
    pdf_buffer.seek(0)
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=neck_tag_{participant["id"]}.pdf'
    return response


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_participant(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE participants
            SET first_name=%s, last_name=%s, phone=%s, email=%s, occupation=%s, company=%s
            WHERE id=%s
        """, (data['first_name'], data['last_name'], data['phone'], data['email'], data['occupation'], data['company'], id))
        mysql.connection.commit()
        cursor.close()
        flash("Participant updated successfully.")
        return redirect(url_for('admin_dashboard'))

    # Fetch existing participant data
    cursor.execute("SELECT * FROM participants WHERE id = %s", (id,))
    row = cursor.fetchone()
    cursor.close()

    if not row:
        flash("Participant not found!", "error")
        return redirect(url_for('admin_dashboard'))

    columns = ["id", "first_name", "last_name", "phone", "email", "occupation", "company", "timestamp"]
    participant = dict(zip(columns, row))
    return render_template('update.html', participant=participant)


@app.route('/delete/<int:id>')
def delete_participant(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM participants WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash("Participant deleted successfully.")
    return redirect(url_for('admin_dashboard'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))
