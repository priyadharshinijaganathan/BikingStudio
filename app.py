from flask import Flask, render_template,request,redirect,url_for,session # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
import bcrypt
from collections import Counter
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError


app = Flask(__name__)
app.secret_key = 'mysecret'

client = MongoClient("mongodb+srv://Admin:vvmsvvms@cluster0.x76r9.mongodb.net/?retryWrites=true&w=majority")
db = client.biking_studio
users = db.users

app.config["GOOGLE_OAUTH_CLIENT_ID"] = "864061902153-8nacv8ipooce9bpq92jcovgeb91202g5.apps.googleusercontent.com"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "dvWXuYCykHz7VcvjCNcNArTW"
google_bp = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(google_bp, url_prefix="/login")
 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


logout_user = []

@app.route('/')
def index():
	if google.authorized:
		try:
			resp = google.get("/oauth2/v1/userinfo")
			session['username'] = resp.json()["email"]
			assert resp.ok, resp.text
			user = users.find_one({'username' : resp.json()["email"]})
			if not user:
				users.insert_one({'username' : resp.json()["email"], 'password' : ""})
			return redirect(url_for('home'))
		except (TokenExpiredError) as e:  # or maybe any OAuth2Error
			return redirect(url_for("index"))
	return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
	login_user = users.find_one({'username' : request.form['username']})
	if login_user:
		if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
			session['username'] = request.form['username']
			return redirect(url_for('home'))
	return 'Invalid username/password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
	if request.method == 'POST':
		users = db.users
		existing_user = users.find_one({'username' : request.form['username']})
		if existing_user is None:
			hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
			users.insert_one({'username' : request.form['username'], 'password' : hashpass})
			session['username'] = request.form['username']
			return redirect(url_for('home'))
		return 'That username already exists!'
	return render_template('register.html')

@app.route('/logout')
def logout():
	if 'username' in session:
		token = google_bp.token["access_token"]
		resp = google.post(
			"https://accounts.google.com/o/oauth2/revoke",
			params={"token": token},
			headers={"Content-Type": "application/x-www-form-urlencoded"}
		)
		del google_bp.token
		session.pop('username')
	if 'manufacturerName' in session:
		session.pop('manufacturerName')
	return redirect(url_for('index'))


@app.route("/google")
def google_login():
	if not google.authorized:
		return redirect(url_for("google.login"))
	resp = google.get("/oauth2/v1/userinfo")
	session['username'] = resp.json()["email"]
	assert resp.ok, resp.text
	user = users.find_one({'username' : resp.json()["email"]})
	if not user:
		users.insert_one({'username' : resp.json()["email"], 'password' : ""})
	return redirect(url_for('index'))

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/handleCafeRacer", methods=['GET'])
def handleCafeRacer():
    return redirect("https://www.bikeexif.com/tag/cafe-racer")

@app.route("/handleRaceBike", methods=['GET'])
def handleRaceBike():
    return redirect("https://www.drivespark.com/bikes/sports/")

@app.route("/handlePremiumStreetBike", methods=['GET'])
def handlePremiumStreetBike():
    return redirect("https://gaadiwaadi.com/top-10-selling-premium-bikes-rs-2-lakh-segment-in-india-during-fy20/")

@app.route("/handlePremiumAdventure", methods=['GET'])
def handlePremiumAdventure():
    return redirect("https://www.carandbike.com/news/top-7-premium-adventure-touring-motorcycles-in-india-2252798")

@app.route("/handleSportyCafe", methods=['GET'])
def handleSportyCafe():
    return redirect("https://www.topspeed.com/motorcycles/guides/top-10-cafe-racers-of-2018-ar182710.html")

@app.route("/handleAdventureTourer", methods=['GET'])
def handleAdventureTourer():
    return redirect("https://www.bforbiker.com/adventure-bikes-in-india/")

@app.route("/handleCruiser", methods=['GET'])
def handleCruiser():
    return redirect("https://www.zigwheels.com/newbikes/best-cruiser-bikes")

@app.route("/handleSuperBike", methods=['GET'])
def handleSuperBike():
    return redirect("https://www.bikedekho.com/upcoming-bikes/super")

@app.route("/handleMail", methods=['GET', 'POST'])
def handleMail():
    
    if request.method == 'POST':
        username = request.form['Name']
        email = request.form['Email']
        sub = request.form['Subject']
        comment = request.form['Comment']

        return "We have recorded your response. We will contact you shortly!!" 


if __name__ == "__main__":
	app.debug = True
	app.run()
