from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blog:a@localhost:8889/blog'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)

class Blog(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))


    def __init__(self, title, body):
        self.title = title
        self.body = body
        



@app.route('/blog', methods=['GET'])
def blog_list():
    
    blogs = Blog.query.all()
    var = ''
    var = request.args.get('id')
    if var is None:
        return render_template('blog.html', title="Build a blog", blogs=blogs)
    else:
        post = Blog.query.filter_by(id=var).first()
        p_title = post.title
        p_body = post.body
        

        return render_template('entry.html', var=var, p_title=p_title, p_body=p_body)




@app.route('/newpost',methods=['POST', 'GET'])
def blog_post():

    
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

        
        if not blog_error and not title_error:

            new_blog = Blog(title, blog)
            db.session.add(new_blog)
            db.session.commit()         
            return redirect('/blog')
     

    return render_template('/newpost.html')









@app.route('/', methods=['GET'])
def index():

    return"<h1> HOME </h1>"






@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect ('/')





if __name__ == '__main__':
    app.run()