from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mail import Mail, Message
import pandas as pd
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__, 
    template_folder='../templates',
    static_folder='../static')

# Email Configuration using environment variables
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('SMTP_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('SMTP_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('SMTP_USERNAME')

mail = Mail(app)

# Root route for language selection
@app.route('/')
def index():
    return render_template('language.html')

# Route for form with language parameter
@app.route('/form/<lang>')
def form(lang):
    if lang not in ['ja', 'en', 'mn', 'vi']:
        return redirect(url_for('index'))
    return render_template(f'form_{lang}.html')

# Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get form data
        data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'surname_romaji': request.form.get('surname_romaji'),
            'givenname_romaji': request.form.get('givenname_romaji'),
            'email': request.form.get('email'),
            'birthdate': request.form.get('birthdate'),
            'gender': request.form.get('gender'),
            'nationality': request.form.get('nationality'),
            'mobile_phone': request.form.get('mobile_phone'),
            'japanese_level': request.form.get('japanese_level')
        }

        # Save to CSV
        df = pd.DataFrame([data])
        csv_file = os.path.join(app.static_folder, 'data', 'submissions.csv')
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, index=False)

        # Send confirmation email to applicant
        send_confirmation_email(data)

        # Send notification email with Excel to admin
        send_admin_notification(data)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def send_confirmation_email(data):
    subject = 'Application Received - HR Recruitment System'
    recipient = data['email']
    
    # Create message based on nationality
    if data['nationality'] == 'Mongolia':
        body = f"""
        Сайн байна уу, {data['surname_romaji']} {data['givenname_romaji']},

        Таны өргөдлийг хүлээн авлаа. Бид тантай удахгүй холбогдох болно.

        Өргөдлийн мэдээлэл:
        - Нэр: {data['surname_romaji']} {data['givenname_romaji']}
        - Имэйл: {data['email']}
        - Утас: {data['mobile_phone']}
        - Япон хэлний түвшин: {data['japanese_level']}

        Баярлалаа,
        HR баг
        """
    else:
        body = f"""
        Dear {data['surname_romaji']} {data['givenname_romaji']},

        We have received your application. We will contact you soon.

        Application Details:
        - Name: {data['surname_romaji']} {data['givenname_romaji']}
        - Email: {data['email']}
        - Phone: {data['mobile_phone']}
        - Japanese Level: {data['japanese_level']}

        Best regards,
        HR Team
        """

    msg = Message(
        subject=subject,
        recipients=[recipient],
        body=body
    )
    mail.send(msg)

def send_admin_notification(data):
    subject = 'New Application Received'
    admin_email = os.getenv('RECIPIENT_EMAIL')
    
    # Create Excel file using pandas instead of xlsxwriter
    df = pd.DataFrame([{
        'Timestamp': data['timestamp'],
        'Surname': data['surname_romaji'],
        'Given Name': data['givenname_romaji'],
        'Email': data['email'],
        'Birthdate': data['birthdate'],
        'Gender': data['gender'],
        'Nationality': data['nationality'],
        'Phone': data['mobile_phone'],
        'Japanese Level': data['japanese_level']
    }])

    # Create Excel file in memory
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)

    body = f"""
    New application received:

    Applicant Details:
    - Name: {data['surname_romaji']} {data['givenname_romaji']}
    - Email: {data['email']}
    - Phone: {data['mobile_phone']}
    - Nationality: {data['nationality']}
    - Japanese Level: {data['japanese_level']}
    - Submission Time: {data['timestamp']}

    Please check the attached Excel file for complete details.
    """

    msg = Message(
        subject=subject,
        recipients=[admin_email],
        body=body
    )

    # Attach Excel file
    msg.attach(
        filename=f"application_{data['surname_romaji']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        data=excel_file.getvalue()
    )

    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)