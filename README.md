# Sabacc
## Video Demo: https://www.youtube.com/watch?v=tgRam9fhVJQ (OUTDATED)
## Play On the Website: http://sabacc.samuelanes.com
## Join the Sabacc Discord: https://discord.gg/AaYrNZjBus
## Description:
Sabacc, the space card game. A fast-paced, high-risk, perfect mixture of skill and luck. Engage in this perfect blend of deception, quick calculation, and strategy, at http://sabacc.samuelanes.com

## Tech Specs
- Backend (Flask)
    - Python
        - Werkzeug
    - sqlite3
- Frontend (SvelteKit)
    - HTML
    - CSS
        - Bootsrap
    - TypeScript

## Design Choices
### Flask vs. Django
I had originally tried to make this project with Django. While taking Harvard's CS50x, I learned how to use Flask, and wanted to try and make a Sabacc web application for my CS50 final project. A large part of the project would be deciding what framework to use. Comparing my knowledge, I felt I had more skill with Flask, either because I had learned more or it was more fresh in my head. I also liked the nature of Flask as compared to Django, Django is more restricting, with very specific frameworks for files and databases, whereas in Flask one has much more flexibility. I decided to use Flask.

### Frontend Framework (SvelteKit)
For a long time, this project was Flask with a vanilla JavaScript (and jQuery) frontend, and this caused a lack of smoothness during gameplay and unecessarily complex programming, so I decided to use a frontend framework. I looked into React, Angular, Svelte, and Vue and eventually chose Svelte. The frontend communicates with the backend via simple HTTP POST requests.

### Player Capacity
In the previous iteration of this project, games had a maximum capacity of two players, which is not ideal for this style of game. Now the application is far more dynamic, allowing for up to eight players in a game, and if I ever decide to change that number in the future it can be done with extreme ease.

### Database Management
This project inherited the usage of a sqlite3 database from the previous iteration. While it was amazing back then, with the new feature of increased player capacity, this presented some challenges. The dynamic storage of games with a variable number of players heavily relies on the usage of Python lists, but unfortunately, sqlite3 does not have a list data type. To remedy this, I designed an efficient set of functions (dataHelpers.py) to handle most of the string and list conversion and operation, allowing me to program the application without any additional concern.

### Game User Interface
Along with the crucial player capacity upgrade, the next most important improvement from the previous design is a heavily enhanced user experience. New interface features added include a life like table, cards, and betting chips. With the introduction of this rounded and natural design, the days of text and boxes are no more.

### User Customization
Another frontend change introduced with this iteration of the project was the option for users to customize the website however they please. Users can now choose between light and dark modes, in addition to choosing game “themes”, which define how game elements look. Customization settings are all stored in cookies, so that users only need to change their settings once, without increasing the load on the server.


## Looking Forward - Future Improvements

### AI Sabacc Opponent
A large feature I plan to implement is an AI opponent. It would run off of data collected from human players, as well as learning from its own playing.

### Backend Efficiency
Python is a great way to jump into development with little hassle or boilerplate, but as the project matures, Python will be slow to keep up with player, especially with the vast amounts of string and list manipulation on the backend. In order to increase backend efficiency, I plan to make a C/C++ library for Python that replaces many relevant backed actions.

### Gameplay Features
The door is wide open for new gameplay features. My ideas include:
- Tournaments
- Competitive Play
- Leaderboards
- Persistent Credits between games
- Different planets to play on
- Better playing UX and GUI (Click add credits, manual dice rolling, images of cards, etc.)
- Other Sabacc Variants (Corellian Spike, Coruscant Shift)
- Prized Items for the Sabacc Pot

## Running the Project Locally
Start by cloning the repo (or download the code in a .zip):
`git clone https://github.com/Heinoushare/Sabacc-Multiplayer.git`

Setup the server side by installing all of the dependencies in server/requirements.txt. The Python version probably isn't crucial but it's the only one that I know works. Don't forget to install sqlite3!
1. cd server
2. Install Python(==3.9.6) (https://www.python.org/downloads/) (or via terminal)
    - Install Pip if it did not install with Python
3. Install pip dependencies `pip install -r pipRequirements.txt`
4. Install sqlite3 (https://www.sqlite.org) (or via terminal)

Setup the client side by installing Node.js, npm, and vite.
1. cd client
2. Install Node.js and npm (https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) (or via terminal)
3. Making sure npm dependencies are installed: `npm install`
4. You can might need to install vite separately like this: `npm install --save-dev vite`

Now that you have everything installed and ready to go, open up a new terminal window in the project and `cd server`. Run the following command to start the backend `flask run`. Open up another new terminal window, `cd client`, and run the following command to start the frontend `npm run dev`. If everything is installed correctly you should be able to visit either http://127.0.0.1:5000 (backend) or http://localhost:5173 (frontend).