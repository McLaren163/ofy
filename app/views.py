import os

from flask import render_template, flash, redirect, request, abort, send_from_directory, session, url_for, \
    make_response
from app import app
from .utils import get_unique_filename, allowed_file, db_add_offer, db_get_user_by_email, db_get_by_filename, \
    db_login, db_get_offers_for_user, db_get_all_users, db_add_user, db_update_opentime_by_filename, \
    user_is_login, user_is_admin, db_get_user_by_id, db_delete_user, email_send_with_thread


@app.route('/')
@app.route('/index')
def index():
    if user_is_login():
        user = db_get_user_by_email(session['email'])
    return render_template('index.html',
                           title='Home',
                           )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db_login(email, password)
        if user:
            session['email'] = email
            session['username'] = user['name']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('index'))
        flash('Incorrect Email or Password!')
    return render_template('login.html',
                           title='Sign In',
                           )


@app.route('/logout')
def logout():
    # session.clear()
    session.pop('email', None)
    session.pop('is_admin', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/profile')
@app.route('/profile/<int:user_id>')
def profile(user_id=None):
    if not user_is_login():
        return abort(403)

    if not user_id or user_id == db_get_user_by_email(session['email'])['id']:
        user = db_get_user_by_email(session['email'])
        return render_template('profile.html',
                               title='Profile',
                               user=user)

    if not user_is_admin():
        return abort(403)

    user = db_get_user_by_id(user_id)
    return render_template('profile.html',
                            title='Profile',
                            user=user)


@app.route('/users')
def users():
    if not user_is_admin():
        return redirect(url_for('index'))
    users = db_get_all_users()
    return render_template('users.html',
                           title='Users',
                           users=users)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if not user_is_admin():
        return abort(403)
    if request.method == 'POST':
        email = request.form.get('email')
        if db_get_user_by_email(email):
            flash('User with email: ' + email + ' exist.')
            return redirect(request.url)
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Password not confirm!')
            return redirect(request.url)
        name = request.form.get('name')
        admin = request.form.get('is_admin')
        db_add_user(name,
                    email,
                    password,
                    admin)
        flash('Create new user ' + name)
        return redirect(url_for('users'))
    return render_template('add_user.html',
                           title='Add new user')


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    # TODO delete this metod
    if not user_is_admin():
        return abort(403)
    db_delete_user(user_id)
    return redirect(url_for('users'))


@app.route('/offers')
def offers():
    if not user_is_login():
        return redirect(url_for('index'))
    user = db_get_user_by_email(session['email'])
    offers = db_get_offers_for_user(user['id'])
    return render_template('offers.html',
                           title='Offers',
                           offers=offers)

@app.route('/add_offer', methods=['GET', 'POST'])
def add_offer():
    if not user_is_login():
        return redirect(request.referrer)

    if request.method == 'POST':

        user = db_get_user_by_email(session['email'])

        if not user:
            flash('Login false.')
            return redirect(url_for('login'))

        if not request.form.get('recipient_name'):
            flash('Recipient name not specified!')
            return redirect(request.url)

        if 'file' not in request.files:
            flash('Не могу прочитать файл')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            #todo check size of file
            filename = get_unique_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath) #todo check filepath to exist
            recipient_name = request.form.get('recipient_name')
            db_add_offer(recipient_name, filename, user['id'])

            flash('New offer: ' + url_for('show', filename=filename, _external=True))
            return redirect('offers')

    return render_template('upload.html',
                           title='Upload offer')


@app.route('/upload', methods=['POST',])
def upload():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db_login(email, password)

        if not user:
            return abort(401)

        if 'file' not in request.files:
            flash('Не могу прочитать файл')
            return redirect(request.url)

        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = get_unique_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath) #todo check filepath to exist
            db_add_offer(filename, user['id'], )
            return redirect('index')

    return render_template('upload.html',
                           title='Upload offer')

@app.route('/show/<path:filename>')
def show(filename):
    offer = db_get_by_filename(filename)
    if not offer:
        return abort(404)
    author = db_get_user_by_id(offer['user_id'])
    return render_template('show.html',
                           author=author,
                           offer=offer)


@app.route('/download/<path:filename>')
def download(filename):
    if not request.args.get('mode') == 'silent':
        offer = db_get_by_filename(filename)
        author = db_get_user_by_id(offer['user_id'])

        db_update_opentime_by_filename(filename)

        message = 'Offer opened\n' + url_for('download',
                                             filename=filename,
                                             mode='silent',
                                             _external=True)
        email_send_with_thread((author['email'],), message)
    path = os.path.abspath(app.config['UPLOAD_FOLDER'])
    return send_from_directory(path, filename)


