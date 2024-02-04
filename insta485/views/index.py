import flask
import insta485
import arrow
import os

@insta485.app.route('/')
def show_index():
    """Display / route."""

    # Check if a user is logged in (you can hardcode this for now)
    logname = "awdeorio"

    # Connect to the database
    connection = insta485.model.get_db()

    # Query database to get posts from users that the logged-in user is following
    cur = connection.execute(
        "SELECT p.postid, p.filename, p.owner, p.created, u.username as owner_username, u.filename as owner_img_url "
        "FROM posts p "
        "JOIN users u ON p.owner = u.username "
        "WHERE p.owner = ? OR p.owner IN ("
        "   SELECT f.username2 "
        "   FROM following f "
        "   WHERE f.username1 = ?"
        ") "
        "ORDER BY p.postid DESC",
        (logname, logname)
    )
    posts = cur.fetchall()

    # For each post, get the comments and check if the current user liked the post
    for post in posts:
        # Get comments
        cur = connection.execute(
            "SELECT c.text, c.owner "
            "FROM comments c "
            "WHERE c.postid = ? "
            "ORDER BY c.created DESC",
            (post['postid'],)
        )
        post['comments'] = cur.fetchall()

        # Check if the current user liked the post
        cur = connection.execute(
            "SELECT 1 "
            "FROM likes "
            "WHERE owner = ? AND postid = ?",
            (logname, post['postid'])
        )
        post['liked_by_current_user'] = cur.fetchone() is not None

        # Construct the image URL
        post['img_url'] = post['filename']

        # Count likes for each post
        cur = connection.execute(
            "SELECT COUNT(*) AS like_count "
            "FROM likes "
            "WHERE postid = ?",
            (post['postid'],)
        )
        like_count = cur.fetchone()['like_count']
        post['likes'] = like_count

        post["timestamp"] = arrow.get(post["created"]).humanize()
    # Add database info to context
    context = {"logname": logname, "posts": posts}
    return flask.render_template("index.html", **context)

@insta485.app.route('/uploads/<filename>')
def show_image(filename):
    #if 'user_id' not in flask.session:
        #flask.abort(403)

    upload_folder = insta485.app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        flask.abort(404)

    return flask.send_from_directory(upload_folder, filename)





