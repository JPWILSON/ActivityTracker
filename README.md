Event Logger - record and then view anything you or anyone else does or has done. 

##About

This README details the way to use this activity tracker. The front-end design needs A LOT of work. 
The focus was just to build a fully functinoal activity tracker. I will be improving the look, as time goes by.

What is this activity tracker? It is a 
project I built to develop my skills in database backed web applications. It is by no 
means the best out there, but a starting in point for myself. Any criticism is welcome. 
If you are also looking to build these types of systems, please feel free to copy any/ all of this. 
No need for credit/ licenses or any of that nonsense. 

An example of an event:
- User 1 (name - Johnny, for example) went for some exercise(Activity), more specifically he went running (Subactivity) on this date at x location. Each event has 6 peices of info: 
Date, User, Activity, Subactivity, Description, Location.
Anyone can view users and their events (a list of all their events showing 
the date and description, or click on an event and see all the info (location, date
activity, subactivity)). But only logged in people can add edit and delete. They can 
perform crud on anyone's info though. (My reasoning is that this is how Wikipedia works, anyone has full CRUD functionality as long as signed in as they can then be tracked). In the end, the truth filters to the top. 


##How To Use

1. Run database_setup.py with a python interpreter
2. Run addActivitiesInstances.py with a python interpreter
3. Run project.py with a python interpreter. 

The application should now be up and running. You can read events from users. Or, sign in and then 
you can add users and perform full CRUD. 
Signing in doesn't make you a user, you still need to add yourself (or you can add others like on Wikipedia, one can add other people). 


##Contributing

I will load this on GitHub and then happily welcome anyone to provide any constructive 
criticism of this project in particular, or my coding in general. I just want to get better. 
(This updated submission is not yet updated to GITHub, rather, I will submit after grading of the project, in case there are further errors.)


##License

tl;dr - The MIT License (MIT)

So, I don't really care about trying to own information, this isn't the 90s.
Do what you like with this or anything else as I don't think anyone can actually own information, just because current laws say that they can. I mean, who am I to say who can
know what, or who on earth thinks they can dictate what my mind is allowed to know...
So, take this and use it, and any other code I write. 


##Add Later

This is still a tiny little repository, but as it grows I intend to add:
-FAQ
-Table of Contents
