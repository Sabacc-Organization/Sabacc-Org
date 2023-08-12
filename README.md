# Sabacc
## Video Demo: <TODO>
## Description:
Sabacc, the space card game. A fast-paced, high-risk, perfect mixture of skill and luck. Engage in this perfect blend of deception, quick calculation, and strategy, at \<INSERT WEBSITE URL\>

## Design Choices
### Flask vs. Django
I had originally tried to make this project with Django, but never finished it. After taking Harvard's CS50x, I learned how to use Flask, and wanted to try and make a Sabacc web application for my CS50 final project. A large part of the project would be deciding what framework to use. Comparing my knowledge, I felt I had more skill with Flask, either because I had learned more or it was more fresh in my head. I also liked the nature of Flask as compared to Django, Django is more restricting, with very specific frameworks for files and databases, whereas in Flask one has much more flexibility. I decided to use Flask.

### Socket.IO
For the web application, I wanted to have a way for people to play real-time Sabacc, without having to reload the page and grab new HTML every time their opponent did their turn. In order to achieve this, I needed a way for the Flask server and client to communicate even after the client had made the HTTP request. My first thought was to have some JavaScript on the client side reloading the page every few seconds, but I immediately knew this wouldn't cut it, and would interfere with gameplay and eat up client and server resources. I looked for an alternative, and found a tool named Socket.IO, which seemed to fit my requirements. Before I dived into trying to use Socket.IO for the Sabacc game itself, I decided to try it on a smaller scale, creating a simple chatroom within the web application, which is still part of the application! After I felt comfortable with Socket.IO, I tackled using it for the Sabacc game itself. Not only did I use my already gained Socket.IO skills, I learned more about *namespaces* and emitting messages to specific users.

## Files
### application.py
application.py is the file that runs this show. It handles all user requests, Socket.IO messages, and the modification of sabacc.db.


application.py uses the following libraries and tools:
#### CS50 Library
The CS50 library is used to add, update, and read data from the sqlite3 database sabacc.db. It's safety features are used to ensure that no malicious user input can damage the database.

#### Flask
The entire web application is based off of Flask. application.py uses the Flask library to handle HTTP GET and POST requests, rendering HTML files and passing data to Jinja2. Flask can also display several different HTML files per page, depending on the circumstances. application.py also uses Flask-Session and Flask-SocketIO, for saving user sessions and receiving and sending Socket.IO messages.

Each part of the web application that uses Socket.IO has it's own Socket *namespace*. A *namespace* is used to tell what a message is for, sort of like the filetype at the end of a file name (.py, .png, .jpeg, etc.). Each *namespace* has a corresponding function. application.py uses a total of five seperate *namespaces*, one for the **GalactiChat**, and four for a Sabacc game, with varying functions for game phases and keeping track of players.

#### Werkzeug
Werkzeug is used for generating and checking password hashes for users, making it difficult for even the application developers to access users' passwords. Werkzeug will also display apologies to users when there are internal server errors.

#### helpers.py
application.py uses helpers.py for repetitive functions and the decorated function @login_required. If @login_required is writted at the top of a page function, the website will automatically redirect the user to the login page if they are not logged in.

#### dataHelpers.py
dataHelpers.py provides application.py with data manipulation functions, especially when dealing with strings and lists.

### config.yml
This file contains static information for application.py to use a reference. This includes links, ports, and settings.

### helpers.py
helpers.py is a file full of custom functions used by application.py. These functions vary from emitting Socket.IO messages, shuffling the Sabacc deck, and redirecting logged out users to the login page.

### dataHelpers.py
dataHelpers.py provides application.py with data manipulation functions, especially when dealing with strings and lists.

### requirements.txt
requiremenets.txt is a very simple file, with no actual functionality in the web application. The use of requirements.txt is to keep track of what libraries and tools the web application uses, in case one day you need to re-install said tools. An important use of requirements.txt is to keep track of what *version* of the tool is required for the web application. Without this, the risk of using incompatible library versions or deprecated methods is high. One example of this is shown with Flask-SocketIO, python-socketio, and python-engineio, the latest versions of these libraries (as of March 2022) are **incompatible**. I had to look up which specfic versions worked and noted them down in requirements.txt for later use.

### sabacc.db
sabacc.db is an sqlite3 relational database which stores all of the web application data. It has two tables, *users* and *games*. The table *users* stores information about every user, with a row for each user. It stores their *username*, *User ID* (the primary key), and *password hash* which application.py uses to check if a user-inputted password is correct. The *games* table stores all the data neccesary to keep track of a game of Sabacc including the primary key of *Game ID*, totalling at 21 columns! Some values seem as if they should be arrays or lists, but that data type doesn't exist in sqlite3, so instead, comma seperated strings are used, which application.py converts into lists using the .split(",") Python string method.

### layout.html
layout.html is the base template for all other HTML files. It contains information for CSS and Bootstrap stylesheets to be used, and HTML for the website navigation bar, title, site icon. It uses Jinja2, a tool to make dynamic HTML, for blocks of code in which other HTML from other files will go, and to display different navigation bars depending on whether a user is signed in or not.

### index.html
index.html *extends* layout.html, using Jinja2 to fill in Jinja2 HTML *blocks*. index.html also uses Jinja2 to check whether a user is signed in or not. If they are, a table of the user's active games will be displayed, with data being passed from application.py, otherwise, a video and rulebook on how to play Sabacc will be displayed.

### index.js
index.js contains code which uses JQuery to copy game links to a user's clipboard on the click of a button.

### register.html
register.html contains an account creation form, which sends a POST request to the server containing registration details. application.py confirms that the details are valid, with a username that doesn't already exist in the database, and matching password and confirmation passwords.

### login.html
login.html contains and login form, which sends a POST request the server with login details. Using login.js, users can also change their password on login.html. application.py will verify user input and login and save the user's session if the user input is valid.

### login.js
login.js contains some plain JavaScript to reveal password changing inputs on login.html.

### apology.html
apology.html simply renders a image of a cat with error text on it. Using external sources and Jinja2, apology.html will generate said image. apology.html is rendered whenever there is an internal server error or invalid user input.

### chat.html
chat.html is used to render the application global chat, using chat.js to send and render messages to others on the chat page.

### chat.js
chat.js uses Socket.IO on the "chat" *namespace* to interchange messages with the server. When the client receives a message from a user connecting or sending a text message, chat.js will use JQuery to display the message, along with the sender's username in front of the message.

### host.html
host.html contains a form which prompts users to enter another user's username to play a game with them. host.html will send a POST request to the server and application.py will verify that the username inputted does exist, and then insert the game in sabacc.db.

### game.html
game.html contains all the HTML and JavaScript necessary to play a game of Sabacc. Usually it is my habit to make a seperate the JavaScript file from its corresponding HTML file, but the combination of the two allows for easier use of Jinja2 in the JavaScript code.

### styles.css
styles.css is the only CSS file in the whole web application. All HTML files use it (since they all extend layout.html and layout.html uses styles.css) for basic color coding and formatting by tag type and class. It also has lots of special styles for gameplay, including event based styles for mouse hovers.