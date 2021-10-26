import sqlite3
import uuid
import hashlib
import datetime
import smtplib
from email.message import EmailMessage
from flask import session
from app import app
from threading import Thread


def get_unique_filename(filename):
    ext = filename.split('.')[-1]
    return '.'.join([uuid.uuid4().hex, ext])


def allowed_file(filename):
    allowed = '.' in filename and filename.split('.')[-1] in app.config['ALLOWED_EXTENSIONS']
    return allowed


def get_password_md5(password):
    hsh = hashlib.md5()
    hsh.update(bytes(password, encoding=app.config.get('ENCODE_TYPE')))
    return hsh.hexdigest()


def user_is_login():
    if 'email' in session and 'is_admin' in session:
        return True
    return False


def user_is_admin():
    if 'email' in session and 'is_admin' in session and session['is_admin'] == 1:
        return True
    return False

def db_init():
    connection = sqlite3.connect(app.config.get('DB_PATH'))
    with open(app.config.get('DB_SCHEMA')) as f:
        connection.executescript(f.read())

    name = app.config.get('ADMIN_NAME')
    email = app.config.get('ADMIN_EMAIL')
    pass_hash = get_password_md5(app.config.get('ADMIN_PASS'))
    is_admin = 1
    cur = connection.cursor()
    cur.execute("INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
                (name, email, pass_hash, is_admin)
                )

    connection.commit()
    connection.close()


def db_get_connection():
    connection = sqlite3.connect(app.config.get('DB_PATH'))
    connection.row_factory = sqlite3.Row
    return connection


def db_add_offer(recipient_name, filename, user_id):
    connection = db_get_connection()
    cur = connection.cursor()

    cur.execute("INSERT INTO offers (recipient_name, filename, user_id) VALUES (?, ?, ?)",
                (recipient_name, filename, user_id)
                )
    rowid = cur.lastrowid
    connection.commit()
    connection.close()
    return rowid


def db_get_user_by_email(email):
    connection = db_get_connection()
    cur = connection.cursor()

    user = cur.execute("SELECT * FROM users WHERE email=?",
                       (email,)).fetchone()
    connection.close()
    return user


def db_get_user_by_id(userid):
    connection = db_get_connection()
    cur = connection.cursor()

    user = cur.execute("SELECT * FROM users WHERE id=?",
                       (userid,)).fetchone()
    cur.close()
    return user


def db_delete_user(user_id):
    connection = db_get_connection()
    cur = connection.cursor()

    cur.execute("DELETE FROM users WHERE id=?",
                (user_id,))
    connection.commit()
    connection.close()

def db_get_offers_for_user(user_id):
    connection = db_get_connection()
    cur = connection.cursor()

    offers = cur.execute("SELECT * FROM offers WHERE user_id=? ORDER BY created DESC",
                          (user_id,)).fetchall()
    return offers


def db_update_opentime_by_filename(filename):
    connection = db_get_connection()
    cur = connection.cursor()

    now = datetime.datetime.now()
    cur.execute("UPDATE offers SET opened=? WHERE filename=?",
                (now, filename,))
    connection.commit()
    connection.close()


def db_get_by_filename(filename):
    connection = db_get_connection()
    cur = connection.cursor()

    entry = cur.execute("SELECT * FROM offers WHERE filename=?",
                        (filename,)).fetchone()
    cur.close()
    return entry


def db_add_user(name, email, password, is_admin):
    hsh = get_password_md5(password)
    connection = db_get_connection()
    cur = connection.cursor()

    cur.execute("INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
                (name, email, hsh, is_admin)
                )
    rowid = cur.lastrowid
    connection.commit()
    connection.close()
    return rowid


def db_get_user_by_email(email):
    connection = db_get_connection()
    cur = connection.cursor()

    user = cur.execute("SELECT * FROM users WHERE email=?",
                       (email,)).fetchone()
    cur.close()
    return user


def db_get_all_users():
    connection = db_get_connection()
    cur = connection.cursor()

    users = cur.execute("SELECT * FROM users").fetchall()

    cur.close()
    return users


def db_login(email, password):
    pass_hsh = get_password_md5(password)
    connection = db_get_connection()
    cur = connection.cursor()

    user = cur.execute("SELECT * FROM users WHERE email=? AND password_hash=?",
                (email, pass_hsh)).fetchone()
    cur.close()
    return user


def db_user_is_exist(email):
    return True if db_get_user_by_email(email) else None


def email_send_notice(to, message):
    msg = EmailMessage()
    msg['Subject'] = 'OFY - Notification'
    msg['From'] = app.config.get('EMAIL_LOGIN')
    msg['To'] = ', '.join(to)
    msg.set_content(message)
    print(msg)
    server = smtplib.SMTP_SSL(app.config.get('EMAIL_HOST'), app.config.get('EMAIL_PORT'))
    server.login(app.config.get('EMAIL_LOGIN'), app.config.get('EMAIL_PASS'))  # user & password
    server.send_message(msg)
    server.quit()

def email_send_with_thread(to, message):
    thread = Thread(target=email_send_notice, args=(to, message))
    thread.start()