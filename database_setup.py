import os
import sys

from sqlalchemy import String, Integer, ForeignKey, Column
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	id = Column(Integer, primary_key = True)
	name = Column(String(40), nullable = False)
	email = Column(String(60))
	#location
	#gender - this shouldn't matter 
	#date_of_birth = Column() - need to figure out how to use sqlalchemy for this...
	#picture
	@property 
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'email': self.email
		}

class Activity(Base):
	__tablename__ = 'activity'
	#Next iteration, this project will have 'added by, with the user's id' 
	id = Column(Integer, primary_key = True)
	name = Column(String(40), nullable = False)
	@property
	def serialize(self):
		return{
			'name': self.name,
			'id': self.id
		}


class Subactivity(Base):
	__tablename__ = 'subactivity'
	id = Column(Integer, primary_key = True)
	name = Column(String(40), nullable = False)
	activity_id = Column(ForeignKey('activity.id'))
	activity = relationship(Activity)
	@property 
	def serialize(self):
		return{
			'name': self.name,
			'id': self.id,
			'activity_id': self.activity_id
		}

class Event(Base):
	__tablename__ = 'event'
	id = Column(Integer, primary_key = True)
	location = Column(String(80))
	date = Column(String(80))
	description = Column(String(200))
	subactivity_id = Column(ForeignKey('subactivity.id'))
	done_by_id = Column(ForeignKey('user.id'))
	done_by = relationship(User)
	subactivity = relationship(Subactivity)
	#date
	#done_by - leave this for now, only when perfected the permissions. 
	# - I see 3 options 
	#1. This - can only see your stuff when logged in to yours
	#2. Can see yours and others, but can only edit yours when logged into yours - I think this is the way I'll do it at first. 
	#3. Can see anyones, and edit anyones, as long as logged in, and it records any changes you make, 
	#		for anyone else to see. 
	@property 
	def serialize(self):
		return{
			'id': self.id,
			'location': self.location,
			'date': self.date,
			'description': self.description,
			'subactivity_id': self.subactivity_id,
			'done_by_id': self.done_by_id
		}

engine = create_engine('sqlite:///activitytracker.db')
Base.metadata.create_all(engine)
