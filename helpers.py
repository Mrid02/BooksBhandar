from functools import wraps
from flask import redirect, session, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return render_template("login.html",message="")
        return f(*args, **kwargs)
    return decorated_function