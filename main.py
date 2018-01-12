#Blogz code - Trevor Sutcliffe 12/2017 - Launchcode


from flask import Flask, request, redirect, render_template, session
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
    users = User.query.all()
    blog_id = ''
    owner_id = ''
    blog_id = request.args.get('id')
    owner_id = request.args.get('owner_id')
    

    if blog_id is None and owner_id is None:   # if there is no id parameter passed, show all the blogs on the blog.html page
               
        return render_template('blog.html', title="Blogz", blogs=blogs, users=users)
    
    elif blog_id is None and owner_id:
        blogs = Blog.query.filter_by(owner_id=owner_id).all()
        user = User.query.filter_by(id=owner_id).first()
        return render_template('singleUser.html', blogs=blogs, user=user)


    else:      #if there is a query parameter with_the post id, store the title and body to pass to the template
       
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('entry.html', blog=blog)
        

        





@app.route('/')
def index():

    users = User.query.all()

    return render_template('index.html', users=users, title="Blog Home")






@app.route('/newpost',methods=['POST', 'GET'])
def blog_post():

    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']

        title_error = ''
        blog_error = ''
            
        if title == '':
            title_error = "you must add a title"
       
        if blog == '':
            blog_error = "you must add a blog post"
            #return render_template('/newpost.html', blog_error=blog_error, title=title)
                    
                
        if not blog_error and not title_error:  #If there are no errors, create a new blog object to add to the db

            new_blog = Blog(title, blog, owner)
            db.session.add(new_blog)
            db.session.commit() 
            #after adding the new post to the database, store the title and body to pass to the entry.html page
       
            
            blog = Blog.query.filter_by(id=new_blog.id).first()

            return render_template('entry.html', blog=blog)
        else:
            return render_template('/newpost.html', title_error=title_error, blog=blog, title=title, blog_error=blog_error )
     

    return render_template('/newpost.html', title="Newpost")



@app.route('/login',methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        name_error =''
        user_error =''
        password_error = 'Incorrect Password'

        user = User.query.filter_by(username=username).first()
        
        if username == '':
            name_error = "Please enter a username"
            password = ''

        if password == '':
            password_error= "Please enter a password"

        if not user:
            user_error = "Not a registered user "
            name_error = ''

        if user and user.password == password:
            session['username'] =  username
            return redirect('/newpost')

        else:
            return render_template('login.html', title='LOGIN', password_error=password_error, name_error=name_error,user_error=user_error, username=username)
          

    return render_template('login.html', title='LOGIN')



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = ''
    password_error = ''
    verify_error = ''

    username = ''
    password = ''
    verify = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
    
        existing_user = User.query.filter_by(username=username).first()


        
        if len(username) < 3:
            username_error = "Username must be at least 3 characters long"
            password = ''
            veryify = ''
        if existing_user:
            username_error = "Username already exists, get your own name"
            password = ''
            veryify = ''
        if username == '':
            username_error = "Enter a username"
            password = ''
            veryify = ''

        if len(password) < 3:
            password_error = "Password must be at least 3 characters long"  
            password = ''
            veryify = ''
        if password == '':
            password_error = "Enter a password"
            password = ''
            veryify = ''
        
        if verify != password:
            verify_error = "Your password and verification must match"
            verify = ''
        if verify == '':
            verify_error = "Enter your verification for your password"
            if password:
                password_error = "Enter in your password AND matching verification"
            password = ''
            veryify = ''


        if not username_error and not password_error and not verify_error:

        
           
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect ('/newpost')
        else:
            return render_template('/signup.html',username=username,password=password, verify=verify, username_error=username_error,password_error=password_error,verify_error=verify_error)
            
        
    return render_template('/signup.html', title="Signup")



@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
    
    



if __name__ == '__main__':
    app.run()