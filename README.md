# Incremental Long-Term Assignments for Canvas VLE [![Build Status](https://travis-ci.com/Rickyboy320/PSE_Hokkies.svg?token=r1oSN27zZYdQJnbijrgR&branch=master)](https://travis-ci.com/Rickyboy320/PSE_Hokkies)
Canvas VLE integration

During the first and second years of the Bachelor Informatics at the University of Amsterdam, students follow a course called PAV (practicum academische vaardigheden or practicum academic competencies). One part of the PAV course is the colloquium journal; students are required to attend events related to their field of study and report on their experiences. Each event can be worth one or more points and students are required to acquire at least ten points by the end of their second year of study. The students' reports are evaluated by a tutor and assigned points on a regular basis.

[Full description](https://www.overleaf.com/read/hxzqgqqmzvwc)

# Setup
```
git clone git@github.com:Rickyboy320/PSE_Hokkies.git
cd PSE_Hokkies
make setup
```
During the setup you will be asked to give a password for the mysql server. Please leave this empty.

# Development environment
Frontend:  
Files are stored in `src/main/vue`.  
To start the vue-server type `make run-front` in the `PSE_Hokkies` folder.  

Backend:  
Files are stored in `src/main/django`.  
To start the django-server type `make run-back` in the `PSE_Hokkies` folder.  

# Testing
Tests are written in `src/test/vue` and `src/test/django` respectively.  
To run the tests and linters, use `make test`.  

# Git Flow
To initiate git flow, use `git flow init`. It will ask for settings, just press enter for all.

Feature:  
`git flow feature start [name]`  
Program the feature and test if everything works.  
Add and commit.  
Merge with the latest develop branch.  
`git flow feature publish`  
Start a pull request (on github.com).  
Wait for Travis to finish testing, and let a fellow developer review and approve your code.  

# Deployment
Not yet implemented.

# Contributors
Jeroen van Bennekum  
Xavier van Dommelen  
Okke van Eck  
Engel Hamer  
Lars van Hijfte  
Hendrik Huang  
Maarten van Keulen  
Joey Lai  
Teun Mathijssen  
Rick Watertor  
Dennis Wind  
Zi Long Zhu  