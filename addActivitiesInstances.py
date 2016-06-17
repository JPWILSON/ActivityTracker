#This should be a file where we can add in a whole bunch of sqlalchemy statements 
# in order to populate the database.....
#May not be necessary 
'''
#Fake Activities:
user = {'name': 'Johnny', 'id':'1', 'email':'johnny@activities.com'}

users = [{'name': 'Johnny', 'id':'1', 'email':'johnny@activities.com'},
			{'name': 'Judy', 'id':'2', 'email':'judy@activities.com'},
			{'name': 'Janice', 'id':'3', 'email':'jenny@activities.com'}]

activity = {'name':'Exercise', 'id':'1'}

activities = [{'name':'Exercise', 'id':'1'},
			{'name':'Eat', 'id':'2'},
			{'name':'Sleep', 'id':'3'}]

#Fake Subactivities:
subactivity = {'name': 'run', 'id' : '1', 'activity_id':'1'}

subactivities =[{'name': 'run', 'id' : '1', 'activity_id':'1'},
				{'name': 'cycle', 'id' : '2', 'activity_id':'1'},
				{'name': 'carbs', 'id' : '3', 'activity_id':'2'},
				{'name': 'protein', 'id' : '4', 'activity_id':'2'},
				{'name': 'REM', 'id' : '5', 'activity_id':'3'},
				{'name': 'nonREM', 'id' : '6', 'activity_id':'3'}
				]

#Fake Instances:
instance= {'description': 'did a park run event', 'id': '1', 'subactivity_id':'1',
			'location':'delta park', 'date':'14 May 2016', 'done_by_id':'1'}

instances = [{'description': 'run park run event', 'id': '1', 'subactivity_id':'1',
			'location':'delta park', 'date':'14 May 2016', 'done_by_id':'1'},
			{'description': 'parkrun at golden harvest', 'id': '2', 'subactivity_id':'1',
			'location':'golden harvest park', 'date':'7 May 2016', 'done_by_id':'2'},
			{'description': 'sushi buffet at hokkaido', 'id': '3', 'subactivity_id':'3',
			'location':'Hokkaido Greenside', 'date':'5 June 2015', 'done_by_id':'3'},
			{'description': 'yip, another run park run event', 'id': '4', 'subactivity_id':'1',
			'location':'delta park', 'date':'14 May 2016', 'done_by_id':'1'},
			{'description': 'super fast parkrun at golden harvest', 'id': '5', 'subactivity_id':'1',
			'location':'golden harvest park', 'date':'7 May 2016', 'done_by_id':'2'},
			{'description': 'just had some sashimi at Hokkaido', 'id': '6', 'subactivity_id':'3',
			'location':'Hokkaido Greenside', 'date':'5 June 2015', 'done_by_id':'3'}]
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Activity, Subactivity, Event 

engine = create_engine('sqlite:///activitytracker.db')
Base.metadata.bind = engine 
DBSsession  = sessionmaker(bind=engine)
session = DBSsession()


user1 = User(name = "Johnny Jonnston", email = 'johnny@gmail.com')
session.add(user1)
session.commit()

user2 = User(name = "Trudy Thompson", email = 'trudy@gmail.com')
session.add(user2)
session.commit()

activity1 = Activity(name = "Exercise")
session.add(activity1)
session.commit()

activity2 = Activity(name = "Eating")
session.add(activity2)
session.commit()


subactivity1 = Subactivity(name = "Running", activity_id = 1)
session.add(subactivity1)
session.commit()

subactivity2 = Subactivity(name = "Buffet", activity_id = 2)
session.add(subactivity2)
session.commit()

event1 = Event(location = 'Golden Harvest Park, Johannesburg',
	date = '7 May 2016', description="Did the 5km park run with a second lap",
	subactivity_id = 1, done_by_id = 1)
session.add(event1)
session.commit()

event2 = Event(location = 'Hokkaido Restaurant, Johannesburg',
	date = '17 May 2016', description="Ate a sushi buffet",
	subactivity_id = 2, done_by_id = 2)
session.add(event2)
session.commit()

print "An item for each of the four tables has been added!"