from flask import Flask, render_template, request, session, make_response

from src.common.database import Database
from src.models.blog import Blog
from src.models.post import Post
from src.models.user import User

app = Flask(__name__)
app.secret_key = "43u890jiwefosaf90dsa8hfu"  # just put a string here for testing


# Initializes mongodb database before requests
@app.before_first_request
def initialize_database():
    Database.initialize()


# The app.route decorator used to tell flask which URL triggers the function
@app.route('/')
def home_template():
    return render_template('home.html')


@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route('/auth/login', methods=['POST'])
def login_user():
    # getting email and password from form
    email = request.form['email']
    password = request.form['password']

    # checking if email and password provided is valid
    if User.login_valid(email, password):
        User.login(email)
    else:
        session['email'] = None

    # redirect once logged in to profile template
    return render_template('profile.html', email=session['email'])


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.route('/auth/register', methods=['POST'])
def register_user():
    # getting email and password from form
    email = request.form['email']
    password = request.form['password']

    User.register(email, password)

    # redirect once logged in to profile template
    return render_template('profile.html', email=session['email'])


@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blogs(user_id):
    if user_id is not None:
        user = User.get_by_id(user_id)  # getting inputted user's blogs
    else:
        user = User.get_by_email(session['email'])  # getting own blogs

    blogs = user.get_blogs()

    return render_template("user_blogs.html", blogs=blogs, email=user.email)


@app.route('/blogs/new', methods=['GET', 'POST'])
def create_new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_email(session['email'])

        new_blog = Blog(user.email, user._id, title, description)
        new_blog.save_to_mongo()

        return make_response(user_blogs(user._id))  # render template from user_blogs


@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()

    return render_template("posts.html", posts=posts, blog_title=blog.title, blog_id=blog._id)


@app.route('/posts/new/<string:blog_id>', methods=['GET', 'POST'])
def create_new_post(blog_id):
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.get_by_email(session['email'])

        new_post = Post(blog_id, title, content, user.email)
        new_post.save_to_mongo()

        return make_response(blog_posts(blog_id))


if __name__ == '__main__':
    app.run(port=4995)
