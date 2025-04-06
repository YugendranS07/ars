import cv2
import face_recognition
import sys
import os
import keyboard
from datetime import datetime, date, timedelta
import mysql.connector
import smtplib
from flask import Flask, render_template, request, redirect, url_for, session, flash
import numpy as np
import csv
import simpleaudio as sa

# Flask setup
app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Date formatting for attendance records
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")
csv_file_path = datetoday2 + ' Attendance' + '.csv'

# Directory for Attendance Records
directory = "Attendance_Records"
file_path = os.path.join(directory, csv_file_path)
if not os.path.exists(directory):
    os.makedirs(directory)

# Sound Alert
filename = 'beep-04.wav'
wave_obj = sa.WaveObject.from_wave_file(filename)

# SMTP Setup for Emails
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()

# Load Student Images
path = 'Students_images'
images = []
students_names = []
students_list = os.listdir(path)

for i in students_list:
    curImg = cv2.imread(f'{path}/{i}')
    images.append(curImg)
    students_names.append(os.path.splitext(i)[0])

# Encode stored images for face recognition
def Encodethe_images(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encodeList.append(encodings[0])
        else:
            print("Warning: No face detected in one of the images. Skipping.")
    return encodeList

encodedimages = Encodethe_images(images)

# Ensure the attendance file exists (Append mode)
def check_csv_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as f:
            f.write('Registration_ID,Student_Name,Gender,Class,Section,Entry_Time,Remarks\n')

# Mark Attendance for a Student (Now Always Appends)
def Attendance_mark(reg_id):
    with open(file_path, 'a+', newline='') as f:  # Open in append mode
        con = mysql.connector.connect(host="localhost", user="root", password="", database="login")
        c = con.cursor()

        # Update student attendance in the database
        sql = 'UPDATE studentdetails SET remarks = "1" WHERE student_id = %s'
        c.execute(sql, (reg_id,))
        con.commit()

        # Retrieve student details from the database
        query = 'SELECT * FROM studentdetails WHERE student_id = %s'
        c.execute(query, (reg_id,))
        record = c.fetchall()

        if not record:
            print(f"Error: No record found for student ID {reg_id}. Skipping.")
            return

        name = record[0][1]
        gender = record[0][2]
        classes = record[0][3]
        section = record[0][4]
        now = datetime.now()
        dtime = now.strftime('%H:%M:%S')
        remarks = 'Present'

        csv_writer = csv.writer(f)
        csv_writer.writerow([reg_id, name, gender, classes, section, dtime, remarks])
        play_obj = wave_obj.play()
        play_obj.wait_done()

# Flask Routes
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
            return render_template('index.html', error="Incorrect Username and Password")

@app.route('/home_page')
def home_page():
    if 'username' in session:
        return render_template("home_page.html", datetoday2=datetoday2)
    return redirect(url_for('login'))

# **Main Attendance Function (Fixes "Today's attendance is already taken")**
@app.route('/start', methods=['GET'])
def start():
    if 'username' not in session:
        return render_template("index.html", error="Please login to continue")

    check_csv_file(file_path)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return render_template('home_page.html', datetoday2=datetoday2, message="Failed to access webcam")

    currentime = datetime.now()
    futuretime = currentime + timedelta(hours=1)

    while True:
        try:
            success, img = cap.read()
            if not success:
                return render_template('home_page.html', datetoday2=datetoday2, message="Webcam frame error")

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            if not facesCurFrame or not encodesCurFrame:
                print("No faces detected in frame. Skipping.")
                continue

            if not encodedimages:
                return render_template('home_page.html', datetoday2=datetoday2, message="No registered faces found!")

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodedimages, encodeFace)
                faceDis = face_recognition.face_distance(encodedimages, encodeFace)

                if not faceDis:
                    continue

                matchIndex = np.argmin(faceDis)

                if faceDis[matchIndex] < 0.50:
                    reg_id = students_names[matchIndex].upper()
                    Attendance_mark(reg_id)

            cv2.imshow('Webcam', img)

            if keyboard.is_pressed('Esc') or (datetime.now() >= futuretime):
                break

            cv2.waitKey(1)
        except Exception as e:
            return render_template('home_page.html', datetoday2=datetoday2, message=f"Error: {str(e)}")

    cap.release()
    cv2.destroyAllWindows()
    return render_template('home_page.html', datetoday2=datetoday2, success_message="Attendance Updated Successfully")

if __name__ == "__main__":
    app.run(debug=True)
