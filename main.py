from flask import Flask, render_template, request, redirect, url_for, session
import json, os

main = Flask(__name__)

main.secret_key = 'super_secret_key'

# ---------- File Paths ----------
STUDENT_FILE = 'students.json'
USER_FILE = 'users.json'

# ---------- Helper Functions ----------
def load_students():
    if os.path.exists(STUDENT_FILE):
        with open(STUDENT_FILE) as f:
            return json.load(f)
    return []

def save_students(data):
    with open(STUDENT_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_users():
    with open(USER_FILE) as f:
        return json.load(f)

def calculate(student):
    marks = student['marks']
    total = sum(marks.values())
    student['total'] = total

    if all(m >= 35 for m in marks.values()):
        student['result'] = 'Pass'
        if total >= 500:
            student['grade'] = 'A+'
        elif total >= 450:
            student['grade'] = 'A'
        elif total >= 400:
            student['grade'] = 'B'
        else:
            student['grade'] = 'C'
    else:
        student['result'] = 'Fail'
        student['grade'] = 'F'

def get_toppers(students):
    toppers = {}
    for cls in ['Inter 1st year','Inter 2nd ']:
        class_students = [s for s in students if s['class'] == cls and s['result'] == 'Pass']
        if class_students:
            top = max(class_students, key=lambda s: s['total'])
            toppers[cls] = top['name']
    return toppers

# ---------- Routes ----------
@main.route('/')
def login_page():
    return render_template("login.html")

@main.route('/login', methods=['POST'])
def login():
    users = load_users()
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        session['user'] = username
        return redirect('/home')
    return render_template("login.html", error="Invalid credentials")

def get_class_toppers(students):
    toppers = {}
    for student in students:
        cls = student['class']
        if cls not in toppers or student['total'] > toppers[cls]['total']:
            toppers[cls] = student
    return toppers

@main.route('/home')
def home():
    search_name = request.args.get('search_name', '').lower()
    search_class = request.args.get('search_class', '').lower()
    search_hallticket = request.args.get('search_hallticket', '').lower()    
       
    with open('students.json', 'r') as f:
        students = json.load(f)

    filtered_students = []
    for student in students:
        if search_name in student['name'].lower() and search_class in student['class'].lower():
            filtered_students.append(student)

    toppers = get_class_toppers(students)

    return render_template('home.html', students=filtered_students, toppers=toppers)

@main.route('/add', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        data = {
            "name": request.form['name'],
            "class": request.form['class'],
            "hallticket" : request.form['hallticket'],

          "marks": {
                "English": int(request.form['English']),
                "Math": int(request.form['Math']),
                "Science": int(request.form['Science']),
                "Social": int(request.form['Social']),
                "Hindi": int(request.form['Hindi']),
                "Computer": int(request.form['Computer']),
            }
        }
        calculate(data)
        students = load_students()
        students.append(data)
        save_students(students)
        return redirect('/home')
    return render_template("add_student.html")

@main.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@main.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_student(index):
    with open('students.json', 'r') as f:
        students = json.load(f)

    if request.method == 'POST':
        students[index]['name'] = request.form['name']
        students[index]['class'] = request.form['class']
        students[index]['marks'] = {
            "English": int(request.form['English']),
            "Math": int(request.form['Math']),
            "Science": int(request.form['Science']),
            "Social": int(request.form['Social']),
            "Hindi": int(request.form['Hindi']),
            "Computer": int(request.form['Computer'])
        }

        # Update total, grade, result
        total = sum(students[index]['marks'].values())
        students[index]['total'] = total
        students[index]['grade'] = calculate_grade(total)
        students[index]['result'] = 'Pass' if all(m >= 35 for m in students[index]['marks'].values()) else 'Fail'

        with open('students.json', 'w') as f:
            json.dump(students, f, indent=4)

        return redirect(url_for('home'))

    student = students[index]
    return render_template('edit_student.html', student=student, index=index)

@main.route('/delete/<int:index>')
def delete_student(index):
    students = load_students()
    if 0 <= index < len(students):
        students.pop(index)
        save_students(students)
    return redirect('/home')

def calculate_grade(total):
    if total >= 540:
        return 'A+'
    elif total >= 480:
        return 'A'
    elif total >= 420:
        return 'B'
    elif total >= 350:
        return 'C'
    elif total >= 300:
        return 'D'
    else:
        return 'F'


if __name__ == '__main__':
    main.run(debug=True)
