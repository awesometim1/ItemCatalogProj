# Item Catalog
---
## Summary

Item Catalog is a web application implementing python's flask module, sqlalchemy, and Google's oAuth 2.0 to serve a website that lists items and categories. Users who are authenticated gain the ability to create, edit, and delete items and those changes are saved onto the backend database. The html files are generated with flask's template inheritance feature, which simplifies the code and enables consistent design elements.

## Main Functions

1. ##### Displays a website

2. ##### Allows for CRUD operations with items

3. ##### Signin and Signout functions

## Installation 

Item Catalog uses `python` and the following modules for python:
1. `sqlalchemy`
2. `flask`
3. `oauth2client`

### Required Files and Programs
1. ##### python
2. ##### ItemCatalogProj.git repository

#### To Install:
1. `pip install sqlalchemy`
2. `pip install flask`
3. `pip install oauth2client`
4. `git clone https://github.com/awesometim1/ItemCatalogProj.git` (Clone the whole repository)
(If python is not installed on system)
5. `pip install python`

## Usage 

1. Open Terminal
2. Navigate to the cloned ItemCatalogProj.git repository folder (use `cd`)
6. Use the command `python main.py` to start up the flask web server
7. From your browser, access `http://localhost:1234/` (Default port set to 1234)

## Program Design 

- Use Flask routing to route GET and POST requests to the correct function.
- Create the "base" template (index.html) for the other templates to inherit from.
- Design the templates and integrate Google Sign-In by placing javascript in the templates.
- Use Flask's "session" object to store user credentials and the session.
- Use Flask's "jsonify" method to return JSON data.


## --Tim Lee--

Created: February 20, 2018

