import csv
import io
import boto3
import json
import urllib.request
from flask import Flask, request, render_template, session, url_for, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, Length, EqualTo, DataRequired
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import smtplib
import email.utils
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import json
import os

app = Flask(__name__)
app.secret_key = "Secret Key"
emailList = []
unsafeEmails = []
with open("EmailList.csv", newline="") as csvFile:
    emailListTemp = []
    rows = csv.reader(csvFile, delimiter = ",")
    for row in rows:
        emailListTemp.append(row)

imageFolder = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = imageFolder

emailList = emailListTemp[1:]

# Replace SENDER: sender@example.com with your "From" address.
# The SENDER address must be verified.
# Replace SENDERNAME with a legitimate like 'Australia Post'
# Replace SENDERPASSWORD with password for sender@example.com

SENDER = ''
SENDERNAME = ''
SENDERPASSWORD = ''
SMTP_SERVER = "imap.gmail.com"


loginDetails = {
    "user1@gmail.com": "user1",
    "user2@gmail.com": "user2"
}



def sendEmail():
    for i in emailList:
        # Replace recipient@example.com with a "To" address. If your account
        # is still in the sandbox, this address must be verified.
        RECIPIENT = i[0]

        # Replace smtp_username with your Amazon SES SMTP user name.
        USERNAME_SMTP = ""

        # Replace smtp_password with your Amazon SES SMTP password.
        PASSWORD_SMTP = ""

        # (Optional) the name of a configuration set to use for this message.
        # If you comment out this line, you also need to remove or comment out
        # the "X-SES-CONFIGURATION-SET:" header below.
        CONFIGURATION_SET = "TrackEmailConfigurationSet"

        # If you're using Amazon SES in an AWS Region other than US West (Oregon),
        # replace email-smtp.us-west-2.amazonaws.com with the Amazon SES SMTP
        # endpoint in the appropriate region.
        HOST = "email-smtp.ap-southeast-2.amazonaws.com"
        PORT = 587

        # The subject line of the email. Make it believable
        SUBJECT = ''

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = ("Put message body here\r\n")

        # The HTML body of the email.
        BODY_HTML = render_template('aus_post_template.html', RECIPIENT = RECIPIENT)

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        # Comment or delete the next line if you are not using a configuration set
        msg.add_header('X-SES-CONFIGURATION-SET', CONFIGURATION_SET)

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(BODY_TEXT, 'plain')
        part2 = MIMEText(BODY_HTML, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # Try to send the message.
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            # stmplib docs recommend calling ehlo() before & after starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        # Display an error message if something goes wrong.
        except Exception as e:
            print("Error: ", e)
        else:
            print("Email sent!")

def generate_results():
    failedList = []
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(SENDER,SENDERPASSWORD)
        mail.select('inbox')

        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        for i in range(latest_email_id,first_email_id-1, -1):
            data = mail.fetch(str(i), '(RFC822)' )
            for response_part in data:
                arr = response_part[0]
                if isinstance(arr, tuple):
                    msg = email.message_from_string(str(arr[1],'utf-8'))
                    msgFinal = msg.get_payload(None, True)
                    dataTest = msgFinal.decode('utf-8')
                    data = json.loads(dataTest)
                    msgFinal_message = json.loads(data['Message'])
                    msgFinal_mail = msgFinal_message['mail']
                    timestamp = msgFinal_mail['timestamp']
                    mail_id = msgFinal_mail['destination'][0]
                    failedList.append((timestamp, mail_id))
        return failedList

    except Exception as e:
        traceback.print_exc()
        print(str(e))


class EmailSend(FlaskForm):
    submit = SubmitField(label = 'Send')

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()])
    password = StringField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='SIGN IN')

class RegisterForm(FlaskForm):
    email = StringField(label = 'Email:', validators=[DataRequired()])
    password1 = PasswordField(label='Password:', validators=[DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label = 'CREATE ACCOUNT')

@app.route('/register', methods = ['POST', 'GET'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password1.data
        loginDetails[email] = password
        return redirect(url_for('login_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Invalid Credintials {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    flag = 0
    if form.validate_on_submit():
        if form.email.data in session:
            return redirect(url_for('user_page'))
        else:
            for user in loginDetails:
                if form.email.data == user and form.password.data == loginDetails[user]:
                    flag = 1
                    return redirect(url_for('cst'))
        if flag == 0:
            flash('Email or Password is invalid', category='danger')
    return render_template('login.html', form=form)

@app.route('/statistics', methods=['GET', 'POST'])
def statistics():
    return render_template('statistics.html')

@app.route('/cst', methods=['GET', 'POST'])
def cst():
    form = EmailSend()
    if form.validate_on_submit():
        sendEmail()
        flash('Email Sent', category='success')
    return render_template('cst.html', form = form, emailList = emailList)

@app.route('/results', methods=['GET', 'POST'])
def results():
    unsafeEmails = generate_results()
    return render_template('results.html', unsafeEmails = unsafeEmails)

@app.route('/test')
def test():
    return render_template('aus_post_template.html')

@app.route('/train')
def train():
    picCheckEmail = os.path.join(app.config['UPLOAD_FOLDER'], 'wrong_email.jpg')
    picCheckName = os.path.join(app.config['UPLOAD_FOLDER'], 'wrong_name.png.jpg')
    return render_template('train.html', picCheckEmail = picCheckEmail, picCheckName = picCheckName)

if __name__ == '__main__':
    app.run(debug=True)
