import cv2
import face_recognition
import sys
import os
import keyboard
from datetime import datetime, date, timedelta
import time
import mysql.connector
import pandas as pd
import smtplib
from flask import Flask, render_template, request, redirect, url_for, session, flash
import numpy as np
import csv
import simpleaudio as sa

# define the beep sound
app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Saving Date today in 2 different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")
csv_file_path = datetoday2 + ' Attendance' + '.csv'
# Directory for storing Attendance
directory = "Attendance_Records"
file_path = os.path.join(directory, csv_file_path)
print(file_path)
filename = 'beep-04.wav'
wave_obj = sa.WaveObject.from_wave_file(filename)
# Create the directory if it doesn't exist
if not os.path.exists(directory):
    os.makedirs(directory)

# Starting SMTP For Mail Purpose
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()

path = 'Students_images'
images = []
students_names = []
students_list = os.listdir(path)

for i in students_list:
    curImg = cv2.imread(f'{path}/{i}')
    images.append(curImg)
    students_names.append(os.path.splitext(i)[0])

# Converting the stored images to RGB format to face detection
def Encodethe_images(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# Function Sort the Datas Based On Student Name In CSV File
def sort_csv_by_student_name(file_path):
    with open(file_path, 'r') as file:
        # Read the CSV file
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # skip the header
        data = list(csv_reader)
    # Filter out empty rows
    data = [row for row in data if row]
    # Sort the data based on the student name column (2nd column)
    data.sort(key=lambda x: x[1].strip() if x else '')
    with open(file_path, 'w', newline='') as file:
        # Write the header to the file
        csv_writer = csv.writer(file)
        csv_writer.writerow(header)
        # Write the sorted data to the file
        csv_writer.writerows([[col.strip() for col in row] for row in data])

# Function to mark attendance
def Attendance_mark(reg_id):
    with open(file_path, 'r+') as f:
        myDataList = f.readlines()
        con = mysql.connector.connect(host="localhost", user="root", password="", database="login")
        idList = []
        # Update query
        c = con.cursor()
        sql = 'UPDATE studentdetails SET remarks = "1" where student_id = %s'
        c.execute(sql, (reg_id,))
        con.commit()

        query = 'SELECT * from studentdetails where student_id = %s'
        c.execute(query, (reg_id,))
        record = c.fetchall()
        name = record[0][1]
        gender = record[0][2]
        classes = record[0][3]
        section = record[0][4]
        now = datetime.now()
        dtime = now.strftime('%H:%M:%S')
        remarks = 'Present'
        for line in myDataList:
            entry = line.split(',')
            idList.append(entry[0])

        if reg_id not in idList:
            f.writelines(f'\n{reg_id},{name},{gender},{classes},{section},{dtime},{remarks}')
            play_obj = wave_obj.play()
            play_obj.wait_done()

# Function to mark absent
def attendancemark_absent():
    with open(file_path, 'r+') as f:
        myDataList = f.readlines()
        idList = []
        con = mysql.connector.connect(host="localhost", user="root", password="", database="login")
        c = con.cursor()
        query2 = 'SELECT * from studentdetails where remarks ="0" ORDER BY student_id ASC'
        c.execute(query2)
        remarks = 'Absent'
        records = c.fetchall()
        for line in myDataList:
            entry = line.split(',')
            idList.append(entry[0])
        for row in records:
            if row[0] not in idList:
                f.writelines(f'\n{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{"Not entered"},{remarks}')

encodedimages = Encodethe_images(images)

# Calculating Total No.Of Students Registered
def totalreg():
    return len(os.listdir('Students_Images'))

# Function definitions are over
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        con = mysql.connector.connect(host="localhost", user="root", password="", database="login")
        c = con.cursor()
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = c.fetchone()
        if result:
            session['username'] = username
            return redirect(url_for('home_page'))
        else:
            error = "Incorrect Username and Password"
            return render_template('index.html', error=error)
    else:
        error = "Please Login to Continue"
        return render_template('index.html', error=error)

@app.route('/home_page')
def home_page():
    if 'username' in session:
        return render_template("home_page.html", datetoday2=datetoday2)
    else:
        return redirect(url_for('login'))

def check_csv_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            # Ensure the CSV header is correctly written
            writer.writerow(['Registration_ID', 'Student_Name', 'Gender', 'Class', 'Section', 'Entry_Time', 'Remarks'])
        return False  # Indicates that the file was just created
    return True  # Indicates that the file already exists

# Once the webcam (Start Attendance button clicked) Starts here
@app.route('/start', methods=['GET'])
def start():
    if 'username' in session:
        datetoday2 = date.today().strftime("%d-%B-%Y")
        csv_file_path = datetoday2 + ' Attendance' + '.csv'
        # Directory for storing Attendance
        directory = "Attendance_Records"
        file_path = os.path.join(directory, csv_file_path)
        print(file_path)
        if check_csv_file(file_path):
            message1 = "Today Attendance is already taken!!"
            return render_template("home_page.html", datetoday2=datetoday2, message=message1)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            message = "Failed to access webcam"
            return render_template('home_page.html', datetoday2=datetoday2, message=message)

        currentime = datetime.now()
        futuretime = currentime + timedelta(minutes=1)

        while True:
            try:
                success, img = cap.read()
                if not success:
                    message = "Failed to read frame from webcam"
                    return render_template('home_page.html', datetoday2=datetoday2, message=message)

                imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
                facesCurFrame = face_recognition.face_locations(imgS)
                encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
                # If no face is detected, just continue
                if not facesCurFrame or not encodesCurFrame:
                    cv2.imshow('Webcam', img)
                    if cv2.waitKey(1) & 0xFF == 27:  # Wait for 'Esc' key press to exit
                        break
                    continue  # Keep looping if no face detected


                con = mysql.connector.connect(host="localhost", user="root", password="", database="login")
                c = con.cursor()

                for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                    matches = face_recognition.compare_faces(encodedimages, encodeFace)
                    faceDis = face_recognition.face_distance(encodedimages, encodeFace)
                    matchIndex = np.argmin(faceDis)
                    currentime = datetime.now()

                    if keyboard.is_pressed('Esc') or (currentime >= futuretime):
                        attendancemark_absent()
                        query3 = 'SELECT parent_email from studentdetails where remarks ="0" ORDER BY student_id ASC'
                        c.execute(query3)
                        Parentemail_records = c.fetchall()
                        today_date = datetoday2

   ##                   for row in Parentemail_records:
   ##                         SUBJECT = 'Attendance Report on' + " " + today_date
    ##                        TEXT = "ABC Group of Institution: Dear Parents, your Son/Daughter has not attended the school today. Please send a letter mentioning the reason for absence of your child."
    ##                        message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
     ##                       server.login('syugicontact@gmail.com', 'pwd')
       ##                     server.sendmail('syugicontact@gmail.com', row, message)

                        sql_update = 'UPDATE studentdetails SET remarks = "0"'
                        c.execute(sql_update)
                        con.commit()
                        sort_csv_by_student_name(file_path)
                        message = "Attendance Marked Today Successfully"
                        return render_template('home_page.html', datetoday2=datetoday2, success_message=message)

                    if faceDis[matchIndex] < 0.50:
                        name = students_names[matchIndex].upper()
                        Attendance_mark(name)
                    else:
                        name = 'Unknown'

                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                cv2.imshow('Webcam', img)
                cv2.waitKey(1)
            except Exception as e:
                message = f"An Error Encountered: {str(e)}"
                return render_template('home_page.html', datetoday2=datetoday2, message=message)
    else:
        return render_template("index.html", error="Please login to continue")

@app.route('/addstudent', methods=['GET', 'POST'])
def addstudent():
    if 'username' in session:
        return render_template("addstudent.html", totalreg=totalreg())
    else:
        return render_template("index.html", error="Please login to continue")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear the user's session
    session.clear()
    # Redirect the user to the login page
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    message = "Student added Successfully"
    con = mysql.connector.connect(host="localhost", user="root", password="", database="login")
    c = con.cursor()
    studentname = request.form['studentname']
    studentid = request.form['studentid']
    studentgender = request.form['studentgender']
    classname = request.form['classname']
    secname = request.form['secname']
    pename = request.form['pename']
    app.config['UPLOAD_FOLDER'] = 'Students_images'
    userimagefolder = 'Students_images'
    if not os.path.isdir(userimagefolder):
        os.makedirs(userimagefolder)
    file = request.files['studentimg']
    extension = file.filename.split(".")[-1]
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], studentid + "." + extension))

    # Adding details to the database
    query = "INSERT INTO studentdetails VALUES (%s, %s, %s, %s, %s, %s, '0')"
    val = (studentid, studentname, studentgender, classname, secname, pename)
    c.execute(query, val)
    con.commit()
    return render_template('home_page.html', datetoday2=datetoday2, success_message=message)

@app.route('/fetchattendancedata', methods=['GET', 'POST'])
def fetchattendancedata():
    if 'username' in session:
        datetoday2 = date.today().strftime("%d-%B-%Y")
        if request.method == 'POST':
            try:
                date_str = request.form['date']
                date_obj = datetime.strptime(date_str, '%d-%B-%Y')
                folder_name = 'Attendance_Records'
                csv_file_name = date_obj.strftime('%d-%B-%Y') + ' Attendance.csv'
                data = []
                datetoday2 = date.today().strftime("%d-%B-%Y")
                # Check if file exists before attempting to open it
                csv_file_path = os.path.join(folder_name, csv_file_name)

                if os.path.exists(csv_file_path):
                    with open(csv_file_path) as csv_file:
                        csv_reader = csv.reader(csv_file)
                        next(csv_reader)
                        for row in csv_reader:
                            data.append(row)

                    return render_template('Attendance_Report.html', date=date_obj.date(), data=data)
                else:
                    error_msg = "File does not exist."
                    return render_template('home_page.html', datetoday2=datetoday2, message=error_msg)
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                return render_template('home_page.html', datetoday2=datetoday2, message=error_msg)
        else:
            return render_template('home_page.html', datetoday2=datetoday2)
    else:
        return render_template("index.html", error="Please login to continue")

if __name__ == "__main__":
    app.run(debug=True)
