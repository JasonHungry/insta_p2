"""
Insta485 account-related pages view.

URLs include:
/accounts/create/, /accounts/delete/, /accounts/edit/, /accounts/password/
"""

import flask
import insta485

@insta485.app.route('/accounts/login/', methods=["GET"])
def login_page():
    """Display user login page."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")

@insta485.app.route('/accounts/logout/', methods=["POST"])
def logout_page():
    """Display user log out page."""
    if 'username' in flask.session:
        flask.session.pop('username')
    return flask.redirect(flask.url_for('login_page'))

@insta485.app.route('/accounts/create/', methods=["GET"])
def create_page():
    """Display user creation page."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit_page'))
    return flask.render_template('create.html')

@insta485.app.route('/accounts/delete/', methods=["GET"])
def delete_page():
    """Display user deletion page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login_page'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('delete.html', **context)

@insta485.app.route('/accounts/edit/', methods=["GET"])
def edit_page():
    """Display user edit page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login_page'))
    logname = flask.session['username']
    connection = insta485.model.get_db()
    user_info = connection.execute(
        "SELECT fullname, email, filename FROM users "
        "WHERE username = ?",
        (logname, )
    ).fetchall()
    context = {"logname": logname, "user_info": user_info}
    return flask.render_template('edit.html', **context)

@insta485.app.route('/accounts/password/', methods=["GET"])
def password_page():
    """Display user password page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login_page'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('password.html', **context)