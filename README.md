# Sabacc
## Video Demo: https://www.youtube.com/watch?v=tgRam9fhVJQ
## Description:
Sabacc, the space card game. A fast-paced, high-risk, perfect mixture of skill and luck. Engage in this perfect blend of deception, quick calculation, and strategy, at http://sabacc.samuelanes.com

## Design Choices
### Flask vs. Django
I had originally tried to make this project with Django. While taking Harvard's CS50x, I learned how to use Flask, and wanted to try and make a Sabacc web application for my CS50 final project. A large part of the project would be deciding what framework to use. Comparing my knowledge, I felt I had more skill with Flask, either because I had learned more or it was more fresh in my head. I also liked the nature of Flask as compared to Django, Django is more restricting, with very specific frameworks for files and databases, whereas in Flask one has much more flexibility. I decided to use Flask.

### Socket.IO
For the web application, I wanted to have a way for people to play real-time Sabacc, without having to reload the page and grab new HTML every time their opponent made their turn. In order to achieve this, I needed a way for the Flask server and client to communicate even after the client had made the HTTP request. My first thought was to have some JavaScript on the client side reloading the page every few seconds, but I immediately knew this wouldn't cut it, and would interfere with gameplay and eat up client and server resources. I looked for an alternative, and found a tool named Socket.IO, which seemed to fit my requirements. Before I dived into trying to use Socket.IO for the Sabacc game itself, I decided to try it on a smaller scale, creating a simple chatroom within the web application, which is still part of the application! After I felt comfortable with Socket.IO, After the experimentation, I was ready to implement Socket.IO into the game.

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

#### alderaanHelpers.py
alderaanHelpers.py gives application.py many of the functions necessary for ending the game, significantly reducing redundancy.

### config.yml
This file contains static information for application.py to use a reference. This includes links, ports, and settings.

### helpers.py
helpers.py is a file full of custom functions used by application.py. These functions vary from emitting Socket.IO messages, shuffling the Sabacc deck, and redirecting logged out users to the login page.

### dataHelpers.py
dataHelpers.py provides application.py with data manipulation functions, especially when dealing with strings and lists.

### alderaanHelpers.py
alderaanHelpers.py is an extremely important tool for ending the game. It reduces the amount of headaches during debugging by neatly organizing functions, in addition to ensuring functionality of the game. The most impressive part of this file is the recursive function used to end the game, which begins recursion in case of tie.

### requirements.txt
requiremenets.txt is a very simple file, with no actual functionality in the web application. The use of requirements.txt is to keep track of what libraries and tools the web application uses, in case one day you need to re-install said tools. An important use of requirements.txt is to keep track of what *version* of the tool is required for the web application. Without this, the risk of using incompatible library versions or deprecated methods is high. One example of this is shown with Flask-SocketIO, python-socketio, and python-engineio, the latest versions of these libraries (as of March 2022) are **incompatible**. I had to look up which specfic versions worked and noted them down in requirements.txt for later use.

### sabacc.db
sabacc.db is an sqlite3 relational database which stores all of the web application data. It has two tables, *users* and *games*. The table *users* stores information about every user, with a row for each user. It stores their *username*, *User ID* (the primary key), and *password hash* which application.py uses to check if a user-inputted password is correct. The *games* table stores all the data neccesary to keep track of a game of Sabacc including the primary key of *Game ID*, totalling at 21 columns! Some values seem as if they should be arrays or lists, but that data type doesn't exist in sqlite3, so instead, comma and semicolon seperated strings are used, which application.py converts into lists using the .split() Python string method.

### layout.html
layout.html is the base template for all other HTML files. It contains information for CSS and Bootstrap stylesheets to be used, and HTML for the website navigation bar, title, site icon. The selection of theme and website modes is handled by layout.html, checking user settings from cookies. It uses Jinja2, a tool to make dynamic HTML, to display different navigation bars and CSS depending on whether a user is signed in or not.

### config.js
config.js contains general settings meant to be seen by all other JavaScript files. Its main purpose to share with other JavaScript files what the domain of the website is, a necessary tool for Socket.IO.

### index.html
index.html *extends* layout.html, using Jinja2 to fill in Jinja2 HTML *blocks*. index.html also uses Jinja2 to check whether a user is signed in or not. If they are, a table of the user's active games will be displayed, with data being passed from application.py, otherwise, a video and rulebook on how to play Sabacc will be displayed.

### register.html
register.html contains an account creation form, which sends a POST request to the server containing registration details. application.py confirms that the details are valid, with a username that doesn't already exist in the database, and matching password and confirmation passwords.

### login.html
login.html contains and login form, which sends a POST request the server with login details. Using login.js, users can also change their password on login.html. application.py will verify user input and login and save the user's session if the user input is valid.

#### login.js
login.js contains some plain JavaScript to reveal password changing inputs on login.html.

### apology.html
apology.html simply renders a image of a cat with error text on it. Using external sources and Jinja2, apology.html will generate said image. apology.html is rendered whenever there is an internal server error or invalid user input.

### chat.html
chat.html is used to render the application global chat, using chat.js to send and render messages to others on the chat page.

#### chat.js
chat.js uses Socket.IO on the "chat" *namespace* to interchange messages with the server. When the client receives a message from a user connecting or sending a text message, chat.js will use JQuery to display the message, along with the sender's username in front of the message.

### host.html
host.html contains a form which prompts users to enter another user's username to play a game with them. host.html will send a POST request to the server and application.py will verify that the username inputted does exist, and then insert the game in sabacc.db.

#### host.js
host.js uses plain JavaScript to enhance user experience by making text boxes appear and disappear, depending on how many players the user would like in their game.

### game.html
game.html contains the HTML needed to play a game of Sabacc. It also contains some JavaScript code accessible by other related files to allow good code organization and integration with Jinja2.

#### game.js
game.js uses JavaScript and jQuery to set up the basic game items of Sabacc not yet included in game.html.

#### socketStuff.js
socketStuff.js initializes the Socket.IO connection with the server so that the game can be played seamlessly.

#### bet.js
bet.js handles the betting phase of the game. It uses jQuery to enhance user experience by allowing them to drag and drop credits.

#### card.js
card.js handles the card phase of the game. It uses jQuery to allow players to trade, draw, stand, and call Alderaan!

### settings.html
settings.html is the page for changing user settings, including dark mode and gameplay themes.

### styles.css
styles.css is the only CSS file in the whole web application. All HTML files use it (since they all extend layout.html and layout.html uses styles.css) for basic color coding and formatting by tag type and class. It also has lots of special styles for gameplay, including event based styles for mouse hovers.

#### classic.css
An extension of styles.css containing the necessary CSS for the *Classic* gameplay theme.

#### rebels.css
An extension of styles.css containing the necessary CSS for the *Rebels* gameplay theme.

#### solo.css
An extension of styles.css containing the necessary CSS for the *Solo* gameplay theme.