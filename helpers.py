from flask import session, redirect
from functools import wraps
from app import db
import os

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Make connection with database, return result as dictionary
def db_execute(type, statement):
    if type == "s":
        with db.engine.connect() as conn:
            result = conn.execute(statement)
            dict = result.mappings().all()
            conn.commit()
        return dict
    
    else:
        with db.engine.connect() as conn:
            result = conn.execute(statement)
            conn.commit()

# Manually create Sequence for ms_name
def name_sequence():
    if os.path.exists("n.txt"):
        with open("n.txt", "r") as r:
            n = int(r.read())
        n += 1
        with open("n.txt", "w") as w:
            w.write(str(n))
        return "MANUSCRIPT-" + str(n)
        
    else:
        with open("n.txt", "x") as f:
            f.write("1")
        return "MANUSCRIPT-1"