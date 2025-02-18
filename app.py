import logging
import os

from flask import Flask, render_template, request, session, redirect, send_file
from flask_session import Session
from flask_alembic import Alembic
from sqlalchemy import select, insert, update

from tables import person, manuscript, keywords, decision, db
from helpers import login_required, db_execute, name_sequence

#Log SQL statements in terminal
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".pdf", ".txt", ".doc", ".docx"]
app.config["UPLOAD_PATH"] = "/Users/cmytelka/Documents/CS50/Final_Project/tmp/user_files/"

# Needs to be executed before `flask run` is run for the first time, 
# otherwise must change environment variables manually via bash:
#`export FLASK_ENV=development`
#`export FLASK_DEBUG=1`
app.config["ENV"] = "development"
app.config["DEBUG"] = True

Session(app)

db.init_app(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Allow for database migrations and upgrades
alembic = Alembic()
alembic.init_app(app)

#To drop all tables
@app.cli.command("drop-db")
def drop_db():
    """Drops all tables from the database."""
    with app.app_context():
        db.drop_all()
        print("All tables dropped.")

#To create all tables
@app.cli.command("create-db")
def create_db():
    """Create all tables in the database."""
    with app.app_context():
        db.create_all()



@app.route("/")
@login_required
def index():
    user = db_execute("s", select(person).where(person.c.id == session["user_id"]))[0]
    if user.role == "Editor":
        return render_template("editor.html")
    else:
        return render_template("author.html", user=user)

    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        #Log user in
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return "Please enter username", 402
        elif not password:
            return "Please enter password", 402
    
        rows = db_execute("s", select(person).where(person.c.username == username))

        if len(rows) != 1 or password != rows[0]["password"]:
            return "Incorrect username or password", 402

        # Remember user's ID
        session["user_id"] = rows[0]["id"]
        print(session["user_id"])

        return redirect("/")
        
    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Get all fields and validate
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        # Insert into Person table
        db_execute("i", person.insert().values(first_name=first_name, last_name=last_name, email=email, username=username, password=password, role="Author"))
    
        return redirect("/")

    else:
        return render_template("register.html")
    

@app.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    """Save manuscript information in database"""
    if request.method == "POST":
        # Manuscript Validation
        title = request.form.get("title")
        abstract = request.form.get("abstract")

        if not title or not abstract:
            return render_template("error.html")
        
        # Keyword Validation
        keyword_count = int(request.form.get("keywordCount"))
        kw_list = []
        for i in range(keyword_count):
            keyword = request.form.get("keyword" + str(i + 1))
            if not keyword:
                render_template("error.html")
            else:
                kw_list.append(keyword)
        
        # File Validation
        uploaded_file = request.files["ms_file"]
        if uploaded_file.filename == "":
            return render_template("error.html", error="No File")
        else:
            file_ext = os.path.splitext(uploaded_file.filename)[1]
            if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                return render_template("error.html", error="Wrong ext")
                
        # If all validation succeeds, proceed to Manuscript Insert
        ms_name = name_sequence()
        db_execute("i", manuscript.insert().values(ms_name=ms_name, author_id=session["user_id"], title=title, abstract=abstract, status="Pending"))

        # Keyword Insert
        ms_id = db_execute("s", select(manuscript.c.ms_id).where(manuscript.c.ms_name == ms_name))[0]["ms_id"]
        for keyword in kw_list:
            db_execute("i", keywords.insert().values(ms_id=ms_id, author_id=session["user_id"], keyword=keyword))

        # File Creation
        subdir = os.path.join(app.config["UPLOAD_PATH"], str(ms_id))
        os.makedirs(subdir, exist_ok=True)
        filename = "manuscript_" + str(ms_id)
        uploaded_file.save(os.path.join(subdir, filename))

        return redirect("/")

    # GET request
    else:
        #Get user information to autofill some fields 
        active_user = db_execute("s", select(person).where(person.c.id == session["user_id"]))[0]
        return render_template("submit.html", person=active_user)
    

@app.route("/review")
@login_required
def review():
    """List all pending manuscripts"""
    manuscripts = db_execute("s", select(manuscript.c.ms_name, manuscript.c.ms_id).where(manuscript.c.status == "Pending"))
    count = len(manuscripts)
    return render_template("review.html", manuscripts=manuscripts, count=count)


@app.route("/manuscripts/ms_id=<int:ms_id>")
@login_required
def show_ms(ms_id):
    """Displays manuscript info for Editor"""
    manuscript_info = db_execute("s", select(manuscript).where(manuscript.c.ms_id == ms_id))[0]
    kw_list = db_execute("s", select(keywords).where(keywords.c.ms_id == ms_id))
    return render_template("manuscript.html", manuscript_info=manuscript_info, kw_list=kw_list)


@app.route("/manuscripts/ms_id=<int:ms_id>/download")
@login_required
def download(ms_id):
    """Button to download manuscript text file"""
    path = app.config["UPLOAD_PATH"] + str(ms_id) + "/manuscript_" + str(ms_id)
    print(path)
    try:
        return send_file(path, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404
    

@app.route("/accept/ms_id=<int:ms_id>")
@login_required
def accept(ms_id):
    db_execute("i", decision.insert().values(ms_id=ms_id, decision_ind=1, decision_text="Accept"))
    db_execute("u", update(manuscript).where(manuscript.c.ms_id == ms_id).values(status="Accepted"))
    return redirect("/")


@app.route("/reject/ms_id=<int:ms_id>")
@login_required
def reject(ms_id):
    db_execute("i", decision.insert().values(ms_id=ms_id, decision_ind=2, decision_text="Reject"))
    db_execute("u", update(manuscript).where(manuscript.c.ms_id == ms_id).values(status="Rejected"))
    return redirect("/")


@app.route("/status")
@login_required
def status():
    """Allow author to check status of all submitted manuscripts"""
    manuscripts = db_execute("s", select(manuscript).where(manuscript.c.author_id == session["user_id"]))
    count = len(manuscripts)
    return render_template("status.html", manuscripts=manuscripts, count=count)