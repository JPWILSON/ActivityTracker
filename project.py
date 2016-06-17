import os, sys

from database_setup import Base, User, Activity, Subactivity, Event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, url_for, redirect, request, flash, jsonify

app = Flask(__name__)

from flask import session as login_session
import random, string #These are used to identify each section
#For step 5: 
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']



engine = create_engine('sqlite:///activitytracker.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


#First, the login page: 
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase+string.digits) for x in xrange(32))
	login_session['state'] = state
	#return "The current session state is: %s"%login_session['state']
	return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
    
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response



#Making an API Endpoint (GET Request)
#Below is for a list of all users in the db
@app.route('/users/JSON')
def welcomeJSON():
	users = session.query(User).all()
	return jsonify(userDetails = [u.serialize for u in users])

#Below is for a list of all activities in the db
@app.route('/activities/JSON')
def activitiesJSON():
	activities = session.query(Activity).all()
	return jsonify( activityList = [a.serialize for a in activities])

#Below is for a list of all subactivities in the db
@app.route('/subactivities/JSON')
def subactivitiesJSON():
	subactivities = session.query(Subactivity).all()
	return jsonify(subactivityList = [s.serialize for s in subactivities])

#Below is for a list of all events carried out by all users in the list:
@app.route('/events/JSON')
def allEventsJSON():
	events = session.query(Event).all()
	return jsonify(eventList = [e.serialize for e in events])

#This is the JSON endpoint where all events are listed per user. 
@app.route('/welcome/<int:user_id>/JSON')
@app.route('/welcome/<int:user_id>/activities/JSON')
def homepageJSON(user_id):
	userSpecificEvents = session.query(Event).filter_by(done_by_id = user_id).all()
	return jsonify(thisUsersEvents = [u.serialize for u in userSpecificEvents])


@app.route('/')
@app.route('/users')
def welcome():
	users = session.query(User).all()
	return render_template('welcomeNonReg.html', users = users)

@app.route('/welcome/add_user',methods = ['GET','POST'])
def addUser():
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		newUser = User(name = request.form['name'], email = request.form['email'])
		session.add(newUser)
		session.commit()
		flash("Well done! %s has been added as a user." % newUser.name)
		return redirect(url_for('welcome'))
	else:
		return render_template('addUser.html')

@app.route('/welcome/<int:user_id>/remove_user', methods = ['GET','POST'])
def remUser(user_id):
	user2Del = session.query(User).filter_by(id = user_id).one()
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		session.delete(user2Del)
		session.commit()
		flash("User %s has successfully been deleted" % user2Del.name)
		return redirect(url_for('welcome'))
	else:
		return render_template('deleteUser.html', user = user2Del)

@app.route('/welcome/<int:user_id>')
@app.route('/welcome/<int:user_id>/activities')
def homepage(user_id):
	user = session.query(User).filter_by(id = user_id).one()
	events = session.query(Event).filter_by(done_by_id = user_id).all()
	return render_template('welcomeAndList.html', descr = events, name = user.name, user_id = user.id)
	
#This function tells the details of a specific instance. 
#As each instance is unique, only need 1 input: The instance_id (but will ad user_id so name is known)
@app.route('/instances/<int:instance_id>')
def activityPage(instance_id):
	#Want to show i.User name ii.subactivity iii.activity iv.instance details
	instance = session.query(Event).filter_by(id = instance_id).one()
	#instance = session.query(Event).first()
	subactivity = session.query(Subactivity).filter_by(id = instance.subactivity_id).one()
	activity = session.query(Activity).filter_by(id = subactivity.activity_id).one()
	user = session.query(User).filter_by(id = instance.done_by_id).one()
	return render_template('eventDetails.html', name = user.name, subact = subactivity.name, 
		act = activity.name, instObj = instance, user_id = user.id)


@app.route('/instances/<int:user_id>/add',methods = ['GET','POST'])
def addActivityInstance(user_id):
	#Want to get i.Activity ii.Subactivity iii.
	#Note! new act & subact should redirect to this page, not the homepage
	#This doesn't link to activity list yet, need to first have subactivity list depending on which activity is listed
	act_list = []
	subact_list = []

	user = session.query(User).filter_by(id = user_id).one()
	activities = session.query(Activity).all()
	for a in activities:
		act_list.append(a.name)

	subactivities = session.query(Subactivity).all()
	for s in subactivities:
		subact_list.append(s.name)
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		activityName = request.form['act']
		act = session.query(Activity).filter_by(name = activityName).one()
		subactName = request.form['subact']
		sub = session.query(Subactivity).filter_by(name = subactName).one()
		newInstance = Event(location = request.form['location'],
			date = request.form['date'], description=request.form['description'],
			subactivity_id = sub.id, done_by_id=user_id)
		session.add(newInstance)
		session.commit()
		return redirect(url_for('homepage', user_id = user_id))
	else:
		return render_template('newInstance.html', name = user.name, 
		al = act_list, sal = subact_list, user_id = user_id,)

@app.route('/instances/<int:instance_id>/<int:user_id>/edit', methods = ['GET', 'POST'])
def editActivityInstance(instance_id, user_id):
	subact_list = []
	subactivities = session.query(Subactivity).all()
	for s in subactivities:
		subact_list.append(s.name)
	event2Edit = session.query(Event).filter_by(id = instance_id).one()
	user = session.query(User).filter_by(id = user_id).one()
	name = user.name
	#Now, the actual activity will not be recorded until link btwn it and subact made
	activities = session.query(Activity).all()
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		if request.form['description']:
			subactName = request.form['subact']
			sub = session.query(Subactivity).filter_by(name = subactName).one()
			event2Edit.location = request.form['location']
			event2Edit.date = request.form['date']
			event2Edit.description = request.form['description']
			event2Edit.done_by_id = user_id
			event2Edit.subactivity_id = sub.id
			session.add(event2Edit)
			session.commit()
			return redirect(url_for('activityPage', instance_id = instance_id))
	else: 
		return render_template('editInstance.html', al = activities, sal = subact_list, user_id = user_id, event2Edit = event2Edit, name = name, instance_id=instance_id)


@app.route('/instances/<int:user_id>/<int:instance_id>/delete', methods = ['GET', 'POST'])
def deleteActivityInstance(user_id,instance_id):
	item2Delete = session.query(Event).filter_by(id = instance_id).one()
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		session.delete(item2Delete)
		session.commit()
		return redirect(url_for('homepage', user_id = user_id))
	else:
		return render_template('deleteInstance.html', user_id = user_id, 
			instance_id = instance_id, item = item2Delete)


@app.route('/activity/<int:user_id>/add', methods = ['GET', 'POST'])
def addActivity(user_id):
	acts = session.query(Activity).all()
	#Perhaps add the user_id so that we know who added this activity
	#Have, but haven't used it yet - yes, will add to database setup: added_by!
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		newActivity = Activity(name=request.form['name'])
		session.add(newActivity)
		session.commit()
		return redirect(url_for('addActivityInstance', user_id = user_id))
	else:
		return render_template('newActivity.html', activities=acts, user_id = user_id)

@app.route('/activity/<int:act_id>/<int:user_id>/edit', methods = ['GET', 'POST'])
def editActivity(act_id, user_id):
	acts = session.query(Activity).all()
	act2Edit = session.query(Activity).filter_by(id = act_id).one()
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		if request.form['name']:
			act2Edit.name = request.form['name']
			session.add(act2Edit)
			session.commit()
			return redirect(url_for('addActivityInstance', user_id = user_id))
	else:
		return render_template('editActivity.html', activity2Edit = act2Edit, act_id = act_id, user_id = user_id)

@app.route('/activity/<int:user_id>/<int:act_id>/delete', methods = ['GET', 'POST'])
def deleteActivity(user_id, act_id):
	activity2Delete = session.query(Activity).filter_by(id = act_id)
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		session.delete(activity2Delete)
		session.commit()
		return redirect(url_for('homepage', user_id = user_id))
	else:
		return render_template('deleteActivity.html', act = activity2Delete, user_id = user_id,
			act_id = act_id)


@app.route('/subactivity/<int:user_id>/add', methods=['GET', 'POST'])
def addSubactivity(user_id):
	acts = session.query(Activity).all()
	subacts = session.query(Subactivity).all()
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		act_name = request.form['act']
		act = session.query(Activity).filter_by(name = act_name).one()
		newSubactivity = Subactivity(name = request.form['name'],
			activity_id = act.id)
		session.add(newSubactivity)
		session.commit()
		return redirect(url_for('addActivityInstance', user_id = user_id))
	else:
		return render_template('newSubactivity.html', al = acts, subactivities = subacts, user_id = user_id)

@app.route('/subactivity/<int:subact_id>/<int:user_id>/edit', methods = ['GET', 'POST'])
def editSubActivity(subact_id, user_id):
	subactivity2Edit = session.query(Subactivity).filter_by(id = subact_id).one()
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		if request.form['name']:
			subactivity2Edit.name = request.form['name']
			session.add(subactivity2Edit)
			session.commit()
			return redirect(url_for('addActivityInstance', user_id = user_id))
	else:
		return render_template('editSubactivity.html', subact = subactivity2Edit, subact_id = subact_id, user_id = user_id)

@app.route('/subactivity/<int:user_id>/<int:subact_id>/delete', methods = ['GET', 'POST'])
def deleteSubActivity(user_id,subact_id):
	subact2Del = session.query(Subactivity).filter_by(id = subact_id)
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		session.delete(subact2Del)
		session.commit()
		return redirect(url_for('homepage', user_id = user_id))
	else:
		return render_template('deleteSubactivity.html', suba = subact2Del, 
			subact_id = subact_id, user_id = user_id)
	


if __name__ == '__main__':
	app.secret_key = "super_secret_key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)


#Now, I need to sort out all of the users, and incorporate them in all the steps that I have done so far...