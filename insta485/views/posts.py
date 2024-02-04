import insta485
import flask
import arrow
import pathlib
import uuid

@insta485.app.route('/posts/<postid>/')
def posts_page(postid):
    """GET /posts/<postid_url_slug>/."""
    logname = "awdeorio"
    # Connect to the database
    connection = insta485.model.get_db()
    # Query database
    cur = connection.execute(
        "SELECT posts.filename, users.username, posts.created, posts.owner "
        "FROM posts "
        "JOIN users ON posts.owner = users.username "
        "WHERE posts.postid=?",
        (postid, )
    )
    post = cur.fetchone()
    if post is None:
        flask.abort(404)
    
    img_url = post["filename"]
    timestamp = arrow.get(post["created"]).humanize()
    # Query for post.owner username and filename from users table
    cur = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username =?",
        (post["owner"],)
    )
    owner_info = cur.fetchone()
    owner = owner_info["username"]
    owner_img_url = owner_info["filename"]
        
    # Get comments
    cur = connection.execute(
        "SELECT comments.owner, comments.text, comments.commentid "
        "FROM comments "
        "WHERE comments.postid=?",
        (postid, )
    )
    comments = cur.fetchall()

    # Get likes
    cur = connection.execute(
        "SELECT likes.owner "
        "FROM likes "
        "WHERE likes.postid=?",
        (postid, )
    )
    likes = cur.fetchall()
    likes_count = len(likes)
    has_liked = False
    for like in likes:
        if like["owner"] == logname:
            has_liked = True
            break

    context = {
        "postid": postid,
        "owner": owner,
        "owner_img_url": owner_img_url,
        "img_url": img_url,
        "comments": comments,
        "timestamp": timestamp,
        "likes": likes_count,
        "has_liked": has_liked,
        "logname": logname
    }
    return flask.render_template("post.html", **context)

@insta485.app.route('/likes/', methods=['POST'])
def update_likes():
    """Update likes for a post."""
    logname = "awdeorio"
    postid = flask.request.form.get('postid')
    operation = flask.request.form.get("operation")
    target = flask.request.args.get("target")
    connection = insta485.model.get_db()
    usr = connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE postid=?",
        (postid, )
    ).fetchall()
    user_liked = False
    for user in usr:
        if user["owner"] == logname:
            user_liked = True
            break
    
    if operation == "like":
        if user_liked:
            flask.abort(409)
        connection.execute(
            "INSERT INTO likes (owner, postid) "
            "VALUES (?, ?)",
            (logname, postid)
        )
    elif operation == "unlike":
        if not user_liked:
            flask.abort(409)
        connection.execute(
            "DELETE FROM likes "
            "WHERE owner=? AND postid=?",
            (logname, postid)
        )
    else:
        flask.abort(404)
    if not target:
        return flask.redirect(flask.url_for("show_index"))
    return flask.redirect(target)

@insta485.app.route('/comments/', methods=['POST'])
def update_comments():
    """Update comments for a post."""
    logname = "awdeorio"
    postid = flask.request.form.get('postid')
    operation = flask.request.form.get("operation")
    target = flask.request.args.get("target")
    connection = insta485.model.get_db()
    if operation == "create":
        text = flask.request.form["text"]
        if text == "":
            flask.abort(400)
        connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?)",
            (logname, postid, text)
        )
    elif operation == "delete":
        commentid = flask.request.form["commentid"]
        cur = connection.execute(
            "SELECT owner "
            "FROM comments "
            "WHERE commentid=?"
            "AND owner=?",
            (commentid, logname)
        )
        comment = cur.fetchone()
        if comment is None:
            flask.abort(403)
        connection.execute(
            "DELETE FROM comments "
            "WHERE commentid=?"
            "AND owner=?",
            (commentid, logname)
        )
    else:
        flask.abort(404)
    if not target:
        return flask.redirect(flask.url_for("show_index"))
    return flask.redirect(target)

@insta485.app.route('/posts/', methods=['POST'])
def update_posts():
    """Update posts."""
    logname = "awdeorio"
    postid = flask.request.form.get('postid')
    operation = flask.request.form.get("operation")
    target = flask.request.args.get("target")
    connection = insta485.model.get_db()
    if operation == "delete":
        cur = connection.execute(
            "SELECT owner, filename "
            "FROM posts "
            "WHERE postid=?",
            (postid, )
        )
        post = cur.fetchone()
        if post is None:
            flask.abort(404)
        if post["owner"] != logname:
            flask.abort(403)
        connection.execute(
            "DELETE FROM posts "
            "WHERE postid=?",
            (postid, )
        )
    elif operation == "create":
        fileobj = flask.request.files["file"]
        if fileobj is None:
            flask.abort(400)
        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        connection.execute(
            "INSERT INTO posts (filename, owner) "
            "VALUES (?, ?)",
            (uuid_basename, logname)
        )
    else:
        flask.abort(404)
    if not target:
        return flask.redirect(flask.url_for('user_profile', user_url_slug=logname))
    return flask.redirect(target)

@insta485.app.route('/following/', methods=['POST'])
def update_following():
    """Update following."""
    logname = "awdeorio"
    username = flask.request.form.get('username')
    operation = flask.request.form.get("operation")
    target = flask.request.args.get("target")
    connection = insta485.model.get_db()
    followed = False
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1=? AND username2=?",
        (logname, username)
    ).fetchall()
    if cur:
        followed = True
    if operation == "follow":
        if followed:
            flask.abort(409)
        connection.execute(
            "INSERT INTO following (username1, username2) "
            "VALUES (?, ?)",
            (logname, username)
        )
    elif operation == "unfollow":
        if not followed:
            flask.abort(409)
        connection.execute(
            "DELETE FROM following "
            "WHERE username1=? AND username2=?",
            (logname, username)
        )
    else:
        flask.abort(404)
    if not target:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(target)