from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app with correct template and static folders
app = Flask(__name__, 
    template_folder='../templates',
    static_folder='../static'
)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# Configure upload folder
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Get form data
        form_data = request.form.to_dict()
        
        # Create uploads directory if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        # Handle file uploads
        uploaded_files = []
        for key, file in request.files.items():
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                uploaded_files.append(file_path)
        
        # Create Excel file
        df = pd.DataFrame([form_data])
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'submission.xlsx')
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        # Send email
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"新規応募 - {form_data.get('name', '名前なし')}"
        
        # Email body
        body = f"""
        新規応募がありました。

        応募者情報:
        名前: {form_data.get('name', '未入力')}
        メール: {form_data.get('email', '未入力')}
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach Excel file
        with open(excel_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 
                          f'attachment; filename="submission.xlsx"')
            msg.attach(part)
        
        # Attach uploaded files
        for file_path in uploaded_files:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(file_path)
                part.add_header('Content-Disposition', 
                              f'attachment; filename="{filename}"')
                msg.attach(part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return jsonify({
            'status': 'success',
            'message': '応募が完了しました。'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")  # For debugging
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)