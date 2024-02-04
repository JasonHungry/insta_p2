import flask
import insta485
import arrow

@insta485.app.route('/users/<user_url_slug>/')
def user_profile(user_url_slug):
    # Connect to database
    connection = insta485.model.get_db()
    # Query database
    logname = "awdeorio"

    cur = connection.execute(
        "SELECT username,fullname, filename "
        "FROM users "
        "WHERE users.username=?",
        (user_url_slug, )
    )
    usr = cur.fetchone()

    if usr is None:
        return flask.abort(404)
    username = usr['username']
    fullname = usr['fullname']
    user_img_url = usr['filename']

    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1=? AND username2=?",
        (logname, user_url_slug)
    )
    logname_follows_username = cur.fetchall() is not None

    cur = connection.execute(
        "SELECT COUNT(following.username1) AS following_num "
        "FROM following "
        "WHERE following.username1=?",
        (username, )
    )
    following_num = cur.fetchall()[0]["following_num"]

    cur = connection.execute(
        "SELECT COUNT(following.username2) AS follower_num "
        "FROM following "
        "WHERE following.username2=?",
        (username, )
    )
    follower_num = cur.fetchall()[0]["follower_num"]
    
    cur = connection.execute(
        "SELECT posts.postid, posts.filename "
        "FROM posts "
        "WHERE posts.owner=?",
        (username, )
    )
    posts = cur.fetchall()

    cur = connection.execute(
        "SELECT COUNT(posts.owner) AS num_posts "
        "FROM posts "
        "WHERE posts.owner=?",
        (username, )
    )
    num_posts = cur.fetchall()[0]["num_posts"]

    context = {"posts": posts, "num_posts": num_posts, "username": username, 
               "following_num": following_num, "follower_num": follower_num,
               "username": username, "fullname": fullname, "logname": logname,
               "user_img_url": user_img_url, "logname_follows_username": logname_follows_username}
    
    return flask.render_template("user.html", **context)

@insta485.app.route('/users/<user_url_slug>/followers/')
def show_followers(user_url_slug):
    """Display user followers page."""
    # Check if a user is logged in (you can hardcode this for now)
    logname = "awdeorio"

    # Connect to the database

    connection = insta485.model.get_db()

    usr = connection.execute(
        "SELECT username,fullname, filename "
        "FROM users "
        "WHERE users.username=?",
        (user_url_slug, )
    ).fetchone()
    if usr is None:
        flask.abort(404)

    # Query for the followers of the user
    cur = connection.execute(
        "SELECT username1 AS username "
        "FROM following "
        "WHERE username2 = ?",
        (user_url_slug,)
    )
    followers = cur.fetchall()

    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ?",
        (logname,)
    )
    me_following = [row["username2"] for row in cur.fetchall()]

    # Query followers filename from users table
    for follower in followers:
        if follower["username"] in me_following:
            follower["logname_follows_username"] = True
        else:
            follower["logname_follows_username"] = False

        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (follower["username"],)
        )
        follower["filename"] = cur.fetchone()["filename"]

    context = {"followers": followers, "logname": logname}
    return flask.render_template("followers.html", **context)

@insta485.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    """Display user following page."""
    # Check if a user is logged in (you can hardcode this for now)
    logname = "awdeorio"

    # Connect to the database
    connection = insta485.model.get_db()

    usr = connection.execute(
        "SELECT username,fullname, filename "
        "FROM users "
        "WHERE users.username=?",
        (user_url_slug, )
    ).fetchone()
    if usr is None:
        flask.abort(404)

    # Query for the users that user_url_slug is following
    cur = connection.execute(
        "SELECT username2 AS username "
        "FROM following "
        "WHERE username1 = ?",
        (user_url_slug,)
    )
    following = cur.fetchall()

    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ?",
        (logname,)
    )
    me_following = [row["username2"] for row in cur.fetchall()]

    # Query following users' filenames from users table
    for user in following:
        if user["username"] in me_following:
            user["logname_follows_username"] = True
        else:
            user["logname_follows_username"] = False
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (user["username"],)
        )
        user["filename"] = cur.fetchone()["filename"]

    context = {
        "following": following, 
        "logname": logname
    }
    return flask.render_template("following.html", **context)

@insta485.app.route('/explore/')
# This page lists all users that the logged in user is not following and includes:
def get_explore():
    # first let logname == "awdeorio"
    logname = "awdeorio"
    # Connect to the database
    connection = insta485.model.get_db()
    # Query database for all users that logname is not following select username and filenames

    cur = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username != ? AND username NOT IN ("
        "   SELECT username2 "
        "   FROM following "
        "   WHERE username1 =?"
        ")",
        (logname, logname)
    )
    users = cur.fetchall()

    context = {"users": users, "logname": logname}
    return flask.render_template("explore.html", **context)