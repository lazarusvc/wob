from flask import render_template, flash, redirect, session, url_for, request, g, abort, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.admin import helpers, expose
#from app import app, db, lm, oid
from app import app, db, lm
from werkzeug import secure_filename
from forms import LoginForm, CommentForm, LikeForm, adminForm, signupForm
from models import User, Image, Comments, Like
from twilio.rest import TwilioRestClient
import os
from sqlalchemy import func

# Find these values at https://twilio.com/user/account
account_sid = "AC18d08fbe124a82b91b3d5c16050bde97"
auth_token = "2b0f2c2a29c1337db6952a5fe1a2c43b"
client = TwilioRestClient(account_sid, auth_token)

@app.before_request
def before_request():
	g.user = current_user

#***********************************************************************#
# // HOME //
#***********************************************************************#
@app.route('/')
def index():
        return render_template('landing.html')
		
		
@app.route('/message_sent', methods=['POST'])
def message_sent():
	message = request.args.get('message')
	#text_message = client.messages.create(to="+17676144347", from_="+12057915604", body="Please place this on Hold...")
	flash('Message sent to Supplier!')
	return redirect(url_for('main'))
	
	
@app.route('/liked', methods=['POST'])
def liked():

	if request.method == 'POST':
		like = Like(request.form['liked'])
		db.session.add(like)
		db.session.commit()
		flash('Thanks for the admiration!')
	return redirect(url_for('main'))
	

@app.route('/add', methods=['POST'])
def add():
	if request.method == 'POST':
		comment = Comments(request.form['comments'])
		db.session.add(comment)
		db.session.commit()
		flash('New entry was successfully posted')
	return redirect(url_for('main'))
		
#***********************************************************************#
# // MAIN //
#***********************************************************************#
@app.route('/main')
def main():
	post = Image.query.all()
	social = Comments.query.all()
	user = User.query.all()
	like = db.session.query(func.count('*')).select_from(Like).scalar()  
	return render_template('main.html', 
	post=post, 
	social=social,
	user=user,
	like=like)

	
#***********************************************************************#
# // PROFILE //
#***********************************************************************#
@app.route('/u/<username>')
def profile(username):
	name = User.query.filter_by(username=username).first()
	pieces = db.session.query(func.count('*')).select_from(Image).scalar()
	like = db.session.query(func.count('*')).select_from(Like).scalar() 
	post = Image.query.all()
	if username is None:
		abort(404)
	return render_template('profile.html', 
	name=name,
	post=post,
	pieces=pieces,
	like=like)
	
#***********************************************************************#
# // LOGIN //
#***********************************************************************#
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm(request.form)
	if helpers.validate_form_on_submit(form):
		user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
		if user is not None:
			login_user(user)
			session['logged_in'] = True
			flash('You are now logged in')
			return redirect(url_for('main'))
	return render_template('login.html', form=form)


#***********************************************************************#
# // SIGNUP //
#***********************************************************************#
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = signupForm(request.form)
	if request.method == 'POST':
		enter_signup = User(request.form['username'],
							request.form['password'],
							request.form['email'])
		db.session.add(enter_signup)
		db.session.commit()
		return redirect(url_for('login'))
	return render_template('sign_up.html')
		

#***********************************************************************#
# // LOGOUT //
#***********************************************************************#		
@app.route('/logout')
def logout():
	logout_user()
	return render_template('landing.html')
	
#***********************************************************************#
# // ADMIN //
#***********************************************************************#	
UPLOAD_FOLDER = '/home/lazarus/Programming/Flask_apps/wob-copy/app/static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
	
def allowed_file(filename):
	return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#***********************************************************************#

@app.route('/admin/', methods=['GET', 'POST'])
def admin():
	form = adminForm(request.form)
	if request.method == 'POST':
		
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			
		path = '/static/img/'
		form = Image(request.form['photo_description'], path + filename,
					 request.form['company'],
					 request.form['price'],
					 request.form['amount'])
		db.session.add(form)
		db.session.commit()
		return redirect(url_for('admin'))
			
#***********************************************************************#
				
	post = db.session.query(func.count('*')).select_from(Image).scalar()
	social = db.session.query(func.count('*')).select_from(Comments).scalar()
	like = db.session.query(func.count('*')).select_from(Like).scalar()  
	
	return render_template('admin.html', like=like, post=post, social=social)


#_________________ NEW  _______________________
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
#_________________ NEW  _______________________