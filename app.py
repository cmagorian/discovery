from flask import Flask, render_template, redirect, url_for, request, session, flash, g, jsonify
from flask.ext.mysql import MySQL
from flask_restful import Resource, Api, reqparse
from functools import wraps
from werkzeug.contrib.fixers import ProxyFix
import sqlite3
import MySQLdb
import tweepy, requests, json
from facepy import GraphAPI

application = Flask(__name__)
application.secret_key = 'alldefdigital'
application.wsgi_app = ProxyFix(application.wsgi_app)
api = Api(application)

mysql = MySQL()
application.config['MYSQL_DATABASE_USER'] = 'admin'
application.config['MYSQL_DATABASE_PASSWORD'] = 'alldefdigital'
application.config['MYSQL_DATABASE_DB'] = 'DB1'
application.config['MYSQL_DATABASE_HOST'] = 'creatorsapplicants-08282016.cuhrgyuzad7j.us-west-2.rds.amazonaws.com'

mysql.init_app(application)

consumer_key = 'aYJWS2nOeqMavQAPabi3ULWtz'
consumer_secret = 'YxM7MhfBV45G105gj7v7W9oqMlzHldHAqwzz6oq5Oqp1n6Sj5q'
access_token = '2174711515-GiTm6zgUp7YjNWAEGbN1B60j6ymDgaebC5eaOHk'
access_token_secret = '1DWFca5iU1l0ig3LOk9x3U2cJ3dMOdFIaNRUmx1o166UF'


def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('You need to login first')
		return redirect(url_for('login'))
	return wrap

def get_popular_vine_url():
	BASE_URL = 'https://api.vineapp.com/'
	x = requests.get(BASE_URL + 'timelines/popular')
	y = json.loads(x.text)
	z = y['data']['records']
	vine_urls = []
	vine_count = []
	vine_velocity = []
	vine_onFire = []
	for i in z:
		vine_urls.append(i['videoDashUrl'])
		vine_count.append(i['loops']['count'])
		vine_velocity.append(i['loops']['velocity'])
		vine_onFire.append(i['loops']['onFire'])
	return vine_urls, vine_count, vine_velocity, vine_onFire

graph = GraphAPI('EAANVkpYoVIcBAPsORZC4hwStx1RRajSBrZBEzq48BFopkAqjwUUok8GjDyiWYrEqWmnRvKSEqvm6SL1EZCGXeAnTJj7Pe4ZCRGxtM8AoRr9cvtFrNLRh6SwFZBmuAmSZAAQl4NeC0y33msaZAfDuwjIElyFvTU7urkZD')

def get_video_facebook_ids(search_term):
	x = graph.get(search_term + '/videos', retry=3, limit=50)
	y = x['data']
	video_ids = []
	for item in y:
		video_ids.append(item['id'])
	return video_ids

@application.route('/', methods=['GET', 'POST'])
@login_required
def home():
	page = 'Home'
	user = 'Admin'
	return render_template('index.html', user=user, page=page)

@application.route('/welcome')
def welcome():
	page = 'Welcome'
	return render_template('welcome.html', page=page)

@application.route('/login', methods=['GET', 'POST'])
def login():
	page = 'Login'
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'alldefdigital':
			error = "Invalid Credentials. Please try again."
		else:
			session['logged_in'] = True
			flash("You were just logged in!")
			return redirect(url_for('home'))
	return render_template('login.html', error=error, page=page)

@application.route("/logout")
def logout():
	page = 'Logout'
	session.pop('logged_in', None)
	flash('You were just logged out!')
	return redirect(url_for('welcome'))

@application.route("/options")
@login_required
def options():
	page = 'Options'
	error = None
	fb_connection = []
	if fb_connection == 1:
		return redirect(url_for('facebook'))
	else:
		return render_template('options.html', page=page)

@application.route('/aboutus')
def aboutus():
	page = 'About'
	error = None
	return render_template('aboutus.html', page=page)

@application.route('/sales')
def sales():
	page = 'Sales'
	error = None
	return render_template('sales.html', page=page)

@application.route('/applicants')
@login_required
def applicants():
	page = 'Applicants'
	error = None
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute('select * from applicants')
	data = [dict(userId=row[0], email=row[1], fullname=row[2], birthday=row[3], city=row[4], youtube=row[5], facebook=row[6], twitter=row[7], instagram=row[8], content=row[9], goals=row[10], license=row[11], read=row[12]) for row in cursor.fetchall()]
	read_args = []
	return render_template('applicants.html', page=page, data=data, read_args=read_args)

@application.route('/usage')
@login_required
def usage():
	page = 'Usage'
	error = None
	return render_template('usage.html', page=page, error=error)

class CreateUser(Resource):
	def post(self):
		try:
			parser = reqparse.RequestParser()
			parser.add_argument('Email', type=str, help='Email you would like to be contacted at')
			parser.add_argument('Fullname', type=str, help='What you want to be addressed as')
			parser.add_argument('Birthday', type=str, help='The day you were born')
			parser.add_argument('City', type=str, help='Not your address, just what city you rep...and live in')
			parser.add_argument('YouTubeURI', type=str, help='Your YouTube URL, if you have one')
			parser.add_argument('FacebookURI', type=str, help='Your Facebook URL, if you have one')
			parser.add_argument('TwitterURI', type=str, help='Your Twitter URL, if you have one')
			parser.add_argument('InstagramURI', type=str, help='Your Instagram URL, if you have one')
			parser.add_argument('Content', type=str, help='A description about your kind of digital content')
			parser.add_argument('Goals', type=str, help='Your goals for working with All Def Digital')
			parser.add_argument('Licensing', type=str, help='If you are down with licensing your content to us and our partners')

			args = parser.parse_args()
	
			_userEmail = args['Email']
			_userFullname = args['Fullname']
			_userBirthday = args['Birthday']
			_userCity = args['City']
			_userYouTubeURI = args['YouTubeURI']
			_userFacebookURI = args['FacebookURI']
			_userTwitterURI = args['TwitterURI']
			_userInstagramURI = args['InstagramURI']
			_userContent = args['Content']
			_userGoals = args['Goals']
			_userLicensing = args['Licensing']

			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('spCreateUser',(_userEmail,_userFullname,_userBirthday,_userCity,_userYouTubeURI,_userFacebookURI,_userTwitterURI,_userInstagramURI,_userContent,_userGoals,_userLicensing))
			data = cursor.fetchall()

			if len(data) is 0:
				conn.commit()
				return {'StatusCode':'200','Message':'User creation successful!'}
			else:
				return {'StatusCode':'1000','Message': str(data[0])}
		except Exception as e:
			return {'error': str(e)}

@application.route('/UpdateDB', methods=['POST'])
def post():
	parser = reqparse.RequestParser()
	parser.add_argument('UserId', type=str, help='UserId of applicant')
	args = parser.parse_args()
	_userId = args['UserId']
	userId = int(_userId)
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute("""UPDATE applicants SET applicants.Read=1 WHERE applicants.UserId = %s""", (userId,))
	cursor.fetchone()
	cursor.execute("""SELECT * FROM applicants WHERE UserId = %s""", (userId,))
	dat = cursor.fetchone()
	print dat
	return jsonify(dat)

@application.route('/discovery')
@login_required
def discovery():
	page = 'Discovery'
        error = None
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
	vine_urls, vine_count, vine_velocity, vine_onFire = get_popular_vine_url()
	vine = zip(vine_urls,vine_count, vine_velocity)
        videos = []
        id_videos = []
        if len(request.args) > 0:
                sn = request.args.get('sn_name')
        else:
                sn = '@AllDefDigital'
        print sn
        public_tweets = api.user_timeline(screen_name=sn,count=25,page=1,include_rts=False)
        all_items = []
        [all_items.append(i) for i in public_tweets]
        for i in all_items:
                try:
                        if i.entities['media'][0]['type']=='photo':
                                videos.append(i.entities['media'][0]['media_url'])
                                id_videos.append(i.id)
                except:
                        pass
	return render_template('discovery.html', page=page, videos=videos, vine_urls=vine_urls, vine_count=vine_count, vine_velocity=vine_velocity, vine_onFire=vine_onFire, vine=vine)

@application.route('/facebook')
@login_required
def facebook():
	page = 'Facebook'
	error = None
	graph = GraphAPI('EAANVkpYoVIcBAPsORZC4hwStx1RRajSBrZBEzq48BFopkAqjwUUok8GjDyiWYrEqWmnRvKSEqvm6SL1EZCGXeAnTJj7Pe4ZCRGxtM8AoRr9cvtFrNLRh6SwFZBmuAmSZAAQl4NeC0y33msaZAfDuwjIElyFvTU7urkZD')
	if len(request.args) > 0:
		search_term = request.args.get('fb_name')
	else:
		search_term = 'AllDefDigital'
	ids = get_video_facebook_ids(search_term)
	return render_template('facebook.html', page=page, ids=ids, search_term=search_term)

@application.route('/twitter_disc')
@login_required
def twitter_disc():
	page = 'Discovery'
	error = None
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        videos = []
        id_videos = []
        if len(request.args) > 0:
                sn = request.args.get('sn_name')
        else:
                sn = '@AllDefDigital'
        print sn
        public_tweets = api.user_timeline(screen_name=sn,count=25,page=1,include_rts=False)
        all_items = []
        [all_items.append(i) for i in public_tweets]
        for i in all_items:
                try:
                        if i.entities['media'][0]['type']=='photo':
                                videos.append(i.entities['media'][0]['media_url'])
                                id_videos.append(i.id)
                except:
                        pass
        return render_template('twitter-disc.html', page=page, videos=videos, id_videos=id_videos)

@application.route('/search', methods=['GET', 'POST'])
def search():
	if request.method == "POST":
		conn = mysql.connect()
		cur = conn.cursor()
		cur.executemany('''select * from applicants where Email = %s''', request.form['search'])
		return render_template("applicants.html", records=cur.fetchall())
	return render_template('applicants.html')
	
api.add_resource(CreateUser, '/CreateUser')

if __name__ == "__main__":
	application.run(host='0.0.0.0', debug=True)
