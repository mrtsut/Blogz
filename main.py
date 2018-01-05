#Blogz code - Trevor Sutcliffe 12/2017 - Launchcode


from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:a@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)
app.secret_key = 'Qgj235'

class Blog(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')        

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog_list', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect("/login")


@app.route('/blog', methods=['GET','POST'])
def blog_list():
    
    blogs = Blog.query.all()
    var = ''
    var = request.args.get('id')
    if var is None:   # if there is no id parameter passed, show all the blogs on the blog.html page
        return render_template('blog.html', title="Build a blog", blogs=blogs)
    else:      #if there is a query parameter with the post id, store the title and body to pass to the template
        post = Blog.query.filter_by(id=var).first()
        p_title = post.title
        p_body = post.body
        

        return render_template('entry.html', var=var, p_title=p_title, p_body=p_body)

@app.route('/')
def index():

    users = User.query.all()

    return render_template('index.html', users=users)






@app.route('/newpost',methods=['POST', 'GET'])
def blog_post():

    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']

        title_error = ''
        blog_error = ''
            
        if blog=='':
            blog_error = "you must add a blog post"
            return render_template('/newpost.html', blog_error=blog_error, title=title)
            

        if title== '':
            title_error = "you must add a title"
            return render_template('/newpost.html', title_error=title_error, blog=blog)

        
        if not blog_error and not title_error:  #If there are no errors, create a new blog object to add to the db

            new_blog = Blog(title, blog, owner)
            db.session.add(new_blog)
            db.session.commit() 
            #after adding the new post to the database, store the title and body to pass to the entry.html page
            post = Blog.query.filter_by(id=new_blog.id, owner=owner).first()
            p_title = post.title
            p_body = post.body
            return render_template('entry.html', p_title=p_title, p_body=p_body)
     

    return render_template('/newpost.html')



@app.route('/login',methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] =  username
            flash("Logged in")
            return redirect('/newpost')
        else:
            #flash('User password incorrect, or user does not exist', 'error')
            return "<h1> Error, something went wrong with you signup info</h1>"
            #
            # NEED TO ADD ERROR MESSAGE HANDLING
            #

    return render_template('login.html')



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

           
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect ('/newpost')
            

        else:
            return "<h1>Duplicate user</h1>"

    return render_template('/signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
    
    



if __name__ == '__main__':
    app.run()