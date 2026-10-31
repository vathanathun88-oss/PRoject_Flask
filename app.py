from flask import Flask, render_template,redirect, request,url_for
import pyodbc
from gtts import gTTS
from voice import speak1,speak2,speak3,speak4
from waitress import serve

app = Flask(__name__)

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-DQ33A4AN;"
    "DATABASE=Python_Inventory;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# Home Page
@app.route("/")
def index():
    return render_template("home.html")

# Admin Dashboard
@app.route("/admin")
def admin():
        cursor.execute("SELECT COUNT(*) FROM Student_Register")
        total_students = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Teacher")
        total_teacher = cursor.fetchone()[0]
        

        cursor.execute("""
SELECT
    CAST(COUNT(p.Student_ID) * 100.0 / COUNT(s.ID) AS DECIMAL(10,2)) AS Paid_Percentage
FROM Student_Register s
LEFT JOIN Payment p
ON s.ID = p.Student_ID
AND p.Status = 'Paid';
""")
        total_pay=cursor.fetchone()[0]
        
        

        return render_template("admin.html", total_teacher=total_teacher,total_students=total_students,total_pay=total_pay)

@app.route("/about")
def about():
    return render_template("about.html")


#Admin Login Page
@app.route("/admin_login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        admin_name=request.form["admin_name"]
        pwd=request.form["pwd"]

        cursor.execute("""
             select * from Admin_Login where Name=? and Pass_wrod=? """
                       , (admin_name,pwd))

        admin=cursor.fetchone()
        if admin:
            if admin:
             
             return redirect(url_for("admin"))
        else:
            speak1()
            return render_template("incorect.html")

    
    return render_template("admin_login.html")

#Payment
@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "POST":
        student_id = request.form["id"]
        major_id = request.form["major_id"]   # gets 1 or 2
        amount = request.form["amount"]

        cursor.execute("""
            INSERT INTO Payment (Student_ID, Major_ID, Amount, Status)
            VALUES (?, ?, ?, ?)
        """, (student_id, major_id, amount, "Paid"))

        conn.commit()
       
        return redirect("/payment")

    return render_template("payment.html")
 


#Student Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Get data from HTML form
        name = request.form["name"]
        gender = request.form["gender"]
        major = request.form["major"]
        birth = request.form["birth"]
        phone = request.form["phone"]
        pwd = request.form["pwd"]


        # Find Major_ID from Major table
        cursor.execute(
            "SELECT Major_ID FROM Major WHERE Major_Name = ?",
            (major,)
        )

        row = cursor.fetchone()


        if row:
            major_id = row[0]

            # Insert student data
            cursor.execute("""
                INSERT INTO Student_Register
                (
                    Full_Name,
                    Gender,
                    Birth,
                    Major_ID,
                    Phone,
                    Pass_Word
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                gender,
                birth,
                major_id,
                phone,
                pwd
            ))

            conn.commit()
            

            # return render_template("success.html")

        else:
            return "Major not found"


    return render_template("register.html")

#view           
@app.route("/view")
def view():
    cursor.execute("""
	   
	select s.ID,s.Full_Name,s.Gender,Birth,m.Major_Name,s.Phone,s.Pass_Word from 
	    Student_Register s inner  join Major m on  s.Major_ID=m.Major_ID
""")
    students = cursor.fetchall()
    # print(students)   # <-- Add this line
    

    return render_template("view.html", students=students)


#frontend 
@app.route("/frontend")
def frontend():
    cursor.execute("""
     select s.ID, s.Full_Name,
       s.Gender , s.Birth,
	   s.Phone,s.Pass_Word
	   from Student_Register s inner join Major m
	   on s.Major_ID=m.Major_ID where  s.Major_ID=1
""")
    web1=cursor.fetchall()
    cursor.execute(""" 
            select t.Teacher_ID,t.Teacher_Name,
           t.Gender,
           t.Phone,
           t.Birth,
           m.Major_Name
           from Teacher t inner join Major m
           on t.Major_ID=m.Major_ID where t.Teacher_ID=1
       """)
    teacher=cursor.fetchone()
    return render_template("frontend.html",web1=web1,teacher=teacher)

#backend
@app.route("/backend")
def backend():
    cursor.execute("""
     select s.ID, s.Full_Name,
       s.Gender , s.Birth,
	   s.Phone,s.Pass_Word
	   from Student_Register s inner join Major m
	   on s.Major_ID=m.Major_ID where  s.Major_ID=2
""")
    web2=cursor.fetchall()

    cursor.execute(""" 
                select t.Teacher_ID,t.Teacher_Name,
               t.Gender,
               t.Phone,
               t.Birth,
               m.Major_Name
               from Teacher t inner join Major m
               on t.Major_ID=m.Major_ID where t.Teacher_ID=2
           """)
    teacher=cursor.fetchone()
    return render_template("backend.html",web2=web2,teacher=teacher)

#delete Student
@app.route("/delete/<int:id>")
def delete_student(id):
    cursor.execute("DELETE FROM Student_Register WHERE ID = ?", (id,))
    conn.commit()
    return redirect("/view")

#score frontend 
@app.route("/score_frontend/<int:id>", methods=["GET","POST"])
def score_frontend(id):

    if request.method == "POST":

        html = request.form["html"]
        css = request.form["css"]
        javascript = request.form["javascript"]
        bootstrap = request.form["bootstrap"]

        cursor.execute("""
            INSERT INTO Frontend_Score
            (Student_ID, HTML, CSS, JavaScript, Bootstrap)
            VALUES (?, ?, ?, ?, ?)
        """, (id, html, css, javascript, bootstrap))

        conn.commit()

        return redirect("/clas1")

    return render_template("score1.html",id=id)

#score backend
@app.route("/score_backend/<int:id>", methods=["GET","POST"])
def score_backend(id):

    if request.method == "POST":

        pyhton = request.form["python"]
        flask = request.form["flask"]       
        sql = request.form["sql"]
        api = request.form["api"]

        cursor.execute("""
            INSERT INTO Backend_Score
            (Student_ID, Python, Flask, SQL_Score, API)
            VALUES (?, ?, ?, ?, ?)
        """, (id, pyhton, flask, sql, api))

        conn.commit()

        return redirect("/clas2")

    return render_template("score2.html",id=id)

 

#teacher_view
@app.route("/teacher_view")
def teacher_view():
    cursor.execute("""
       select t.Teacher_ID,t.Teacher_Name,
       t.Gender,
	   t.Phone,
	   t.Birth,
	   t.Email,
	   m.Major_Name
	   from Teacher t inner join Major m
	   on t.Major_ID=m.Major_ID 

   """)
    techer=cursor.fetchall()
    return render_template("teacher_view.html",techer=techer)


#Class frontend
@app.route("/clas1")
def clas1():

    cursor.execute("""
         select s.ID, s.Full_Name,
               s.Gender , s.Birth,
               s.Phone,Major_Name
               from Student_Register s inner join Major m
               on s.Major_ID=m.Major_ID where  s.Major_ID=1
    """)

    students = cursor.fetchall()

    return render_template("class_frontend.html", students=students)


# Class Backend
@app.route("/clas2")
def clas2():
    cursor.execute("""
     select s.ID, s.Full_Name,
       s.Gender , s.Birth,
	   s.Phone,Major_Name
	   from Student_Register s inner join Major m
	   on s.Major_ID=m.Major_ID where  s.Major_ID=2
""")
    student=cursor.fetchall()

    return render_template("class_backend.html",student=student)


#teacher login
@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():

    if request.method == "POST":
        teacher_id = request.form["id"]
        pwd = request.form["pwd"]

        cursor.execute("""
            SELECT Teacher_ID, PWD, Major_ID
            FROM Teacher
            WHERE Teacher_ID = ? AND PWD = ?
        """, (teacher_id, pwd))

        teacher = cursor.fetchone()

        if teacher:
            major_id = teacher.Major_ID

            if major_id == 1:
                return redirect(url_for("clas1"))
            elif major_id == 2:
                return redirect(url_for("clas2"))

        return "Invalid Teacher ID or Password"

    return render_template("teacher_login.html")
#result 1
@app.route("/result1")
def result1():
    cursor.execute("""

SELECT  Student_ID, Full_Name, HTML, CSS, JavaScript, Bootstrap,
    (HTML + CSS + JavaScript + Bootstrap) AS Total_Score,
    (HTML + CSS + JavaScript + Bootstrap) / 4.0 AS Arg,
    CASE
        WHEN (HTML + CSS + JavaScript + Bootstrap) / 4.0 >= 90 THEN 'A'
        WHEN (HTML + CSS + JavaScript + Bootstrap) / 4.0 >= 80 THEN 'B'
        WHEN (HTML + CSS + JavaScript + Bootstrap) / 4.0 >= 70 THEN 'C'
        WHEN (HTML + CSS + JavaScript + Bootstrap) / 4.0 >= 60 THEN 'D'
        WHEN (HTML + CSS + JavaScript + Bootstrap) / 4.0 >= 50 THEN 'E'
        ELSE 'F'
    END AS Grade
FROM Frontend_Score f inner join Student_Register s on f.Student_ID = s.ID

""")
    result1=cursor.fetchall()
    return render_template("result1.html",result1=result1)

#result 1
@app.route("/result2")
def result2():
    cursor.execute("""

SELECT  Student_ID, Full_Name, Python, Flask, SQL_Score, API,
    (Python+ Flask+ SQL_Score+ API) AS Total_Score,
    (Python+ Flask+ SQL_Score+ API) / 4.0 AS Arg,
    CASE
        WHEN (Python+ Flask+ SQL_Score+ API) / 4.0 >= 90 THEN 'A'
        WHEN (Python+ Flask+ SQL_Score+ API) / 4.0 >= 80 THEN 'B'
        WHEN (Python+ Flask+ SQL_Score+ API) / 4.0 >= 70 THEN 'C'
        WHEN (Python+ Flask+ SQL_Score+ API) / 4.0 >= 60 THEN 'D'
        WHEN (Python+ Flask+ SQL_Score+ API) / 4.0 >= 50 THEN 'E'
        ELSE 'F'
    END AS Grade
FROM Backend_Score b inner join Student_Register  s on b.Student_ID = s.ID

""")
    result2=cursor.fetchall()
    return render_template("result2.html",result2=result2)



# Search Student
@app.route("/search", methods=["GET", "POST"])
def search():

    result = None

    if request.method == "POST":

        id = request.form["id"]

        cursor.execute("""
        SELECT
            s.ID,
            s.Full_Name,
            s.Gender,
            s.Birth,
            m.Major_Name,
            s.Phone,
            s.Pass_Word,

            (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) AS Total_Score,

            (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 AS AVG,

            CASE
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 90 THEN 'A'
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 80 THEN 'B'
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 70 THEN 'C'
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 60 THEN 'D'
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 50 THEN 'E'
                ELSE 'F'
            END AS Grade,

            'Frontend' AS Category

        FROM Student_Register s

        INNER JOIN Major m
            ON s.Major_ID = m.Major_ID

        INNER JOIN Frontend_Score f
            ON s.ID = f.Student_ID

        WHERE s.ID = ?


        UNION ALL


        SELECT
            s.ID,
            s.Full_Name,
            s.Gender,
            s.Birth,
            m.Major_Name,
            s.Phone,
            s.Pass_Word,

            (b.Python + b.Flask + b.SQL_Score + b.API) AS Total_Score,

            (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 AS AVG,

            CASE
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 90 THEN 'A'
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 80 THEN 'B'
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 70 THEN 'C'
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 60 THEN 'D'
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 50 THEN 'E'
                ELSE 'F'
            END AS Grade,

            'Backend' AS Category

        FROM Student_Register s

        INNER JOIN Major m
            ON s.Major_ID = m.Major_ID

        INNER JOIN Backend_Score b
            ON s.ID = b.Student_ID

        WHERE s.ID = ?

        """, (id, id))


        result = cursor.fetchone()


    return render_template("seaarch_studetn.html", result=result)

#table payment 
@app.route("/table_payment")
def table_payment():
    cursor.execute("""
    SELECT 
    p.Payment_ID,
    s.ID,
    s.Full_Name,
    m.Major_Name,
	p.Amount,
	p. Payment_Date,
    ISNULL(p.Status, 'Pending') AS Status
FROM Student_Register s

INNER JOIN Major m
    ON s.Major_ID = m.Major_ID

LEFT JOIN Payment p
    ON p.Student_ID = s.ID;
""")
    pay=cursor.fetchall()




    return render_template("table_payment.html",pay=pay)

#Student Login
@app.route("/student_login",methods=["GET","POST"])
def student_login():
    if request.method=="POST":
        id=request.form["id"]
        pwd=request.form["pwd"]
        cursor.execute(""" SELECT
            s.ID,
            s.Full_Name,
            s.Gender,
            s.Birth,
            m.Major_Name,
            s.Phone,
            s.Pass_Word,p.Status,p.Amount,p.Payment_Date,

            (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) AS Total_Score,

            (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 AS AVG,

            CASE
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 90 THEN 'A'
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 80 THEN 'B'
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 70 THEN 'C'
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 60 THEN 'D'
                WHEN (f.HTML + f.CSS + f.JavaScript + f.[Bootstrap]) / 4.0 >= 50 THEN 'E'
                ELSE 'F'
            END AS Grade


        FROM Student_Register s

        INNER JOIN Major m
            ON s.Major_ID = m.Major_ID

        LEFT JOIN Frontend_Score f
            ON s.ID = f.Student_ID
		LEFT JOIN Payment p on s.ID=p.Student_ID

     WHERE s.ID = ? and  s.Pass_Word=?
        UNION ALL
        SELECT
            s.ID,
            s.Full_Name,
            s.Gender,
            s.Birth,
            m.Major_Name,
            s.Phone,
            s.Pass_Word,p.Status,p.Amount,p.Payment_Date,

            (b.Python + b.Flask + b.SQL_Score + b.API) AS Total_Score,

            (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 AS AVG,

            CASE
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 90 THEN 'A'
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 80 THEN 'B'
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 70 THEN 'C'
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 60 THEN 'D'
                WHEN (b.Python + b.Flask + b.SQL_Score + b.API) / 4.0 >= 50 THEN 'E'
                ELSE 'F'
            END AS Grade

            

        FROM Student_Register s

        INNER JOIN Major m
            ON s.Major_ID = m.Major_ID

        LEFT JOIN Backend_Score b
            ON s.ID = b.Student_ID
		LEFT JOIN Payment p on s.ID=p.Student_ID

        WHERE s.ID = ? and  s.Pass_Word=?

""",(id,pwd,id,pwd))
        login=cursor.fetchone()
        if login:
            return render_template("student.html",student=login)
        else:
            return("not corect")
    return render_template("student_login.html")
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # serve(app, host="0.0.0.0", port=5000)



