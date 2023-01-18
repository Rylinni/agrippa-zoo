from flask import Blueprint, request
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db
import json
from flask_cors import cross_origin

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
@cross_origin()
def login():

    username = request.form['username']
    password = request.form['password']

    # Translate column numnber into key
    db = get_db()
    match = db.execute(
        "SELECT username, password_hash FROM users WHERE username=?", (username,)
    ).fetchone()

    if not match:
        return json.dumps({'response': 'failed', 'why': 'no_user_exists'})

    if not check_password_hash(match['password_hash'], password):
        return json.dumps({'response': 'failed', 'why': 'wrong_password'})

    return json.dumps({'response': 'succeeded'})

@bp.route('/register', methods=['POST'])
@cross_origin()
def register():

    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None

    if not username:
        error = "{'response': 'failed', 'why': 'username_missing'}"
    elif not password:
        error = "{'response': 'failed', 'why': 'password_missing'}"

    if error is None:
        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
        except db.IntegrityError:
            error = "{'response': 'failed', 'why': 'username_taken'}"
        else:
            return "{'response': 'succeeded'}"

    return error
