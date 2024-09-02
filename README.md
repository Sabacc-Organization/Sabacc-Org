# Sabacc
## Video: https://youtu.be/pSN39eC3kik
## Play On the Website: http://sabacc.samuelanes.com
## Join the Sabacc Discord: https://discord.gg/AaYrNZjBus
## Description:
Sabacc, the space card game. A fast-paced, high-risk, perfect mixture of skill and luck. Engage in this perfect blend of deception, quick calculation, and strategy, with over 300 other users at http://sabacc.samuelanes.com

This web application currently contains two Sabacc variants **Traditional Sabacc**, and **Corellian Spike Sabacc**. You can learn more about how to play by visiting http://sabacc.samuelanes.com/how-to-play.

## Tech Specs
- Backend (Flask)
    - Python
        - Werkzeug
    - PostgreSQL
- Frontend (SvelteKit)
    - HTML
    - CSS
        - Bootsrap
    - TypeScript

## Join the Team!
If you are interested in helping with development, please join the Discord (https://discord.gg/AaYrNZjBus) and let us know. We really want to grow this project!

## Looking Forward - Future Improvements

### AI Sabacc Opponent
A large feature we might implement is an AI opponent.

### Gameplay Features
The door is wide open for new gameplay features. Ideas include:
- Tournaments
- Competitive Play
- Leaderboards
- Persistent Credits between games
- Different planets to play on
- Better playing UX and GUI (Click add credits, manual dice rolling, images of cards, etc.)
- Other Sabacc Variants (Coruscant Shift, Kessel Sabacc)
- Prized Items for the Sabacc Pot

## Running the Project Locally
Start by cloning the repo (or download the code in a .zip):
`git clone https://github.com/Sabacc-Organization/Sabacc-Org.git`

Setup the server side by installing all of the dependencies in server/requirements.txt. The Python version probably isn't crucial but it's the only one that I know works. Don't forget to install PostgreSQL!
1. `cd server`
2. Install Python(==3.12.4) (https://www.python.org/downloads/) (or via terminal)
    - Install Pip if it did not install with Python
3. Install pip dependencies `pip install -r pipRequirements.txt`
4. Install PostgreSQL (https://www.codecademy.com/article/installing-and-using-postgresql-locally) and make a database. **Postbird** is highly recommended!
5. Update the `DATABASE` part of config.yml according to your database. If you're not sure how to do that, check CS50's Python library docs: https://cs50.readthedocs.io/libraries/cs50/python/?highlight=postgres#cs50.SQL
6. Run the backend by starting the Postgres server and using `flask run`

Setup the client side by installing Node.js, npm, and vite.
1. `cd client`
2. Install Node.js and npm (https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) (or via terminal)
3. Making sure npm dependencies are installed: `npm install`
4. You can might need to install vite separately like this: `npm install --save-dev vite`
5. Run the frontend by using `npm run dev`

Now that you have everything installed and ready to go, open up a new terminal window in the project and `cd server`. Run the following command to start the backend `flask run`. Open up another new terminal window, `cd client`, and run the following command to start the frontend `npm run dev`. If everything is installed correctly you should be able to visit either http://127.0.0.1:5000 (backend) or http://localhost:5173 (frontend).
