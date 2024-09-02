# Files and Directories

## app.py
app.py is the file that runs the show. It's the main program of the backend, containing the backend routing and SocketIO. Every function defined in app.py corresponds to an HTTP route or Socket communinication route.

## config.yml
config.yml contains all the preferences and settings for the backend. This includes allowed routes for CORS and PostgreSQL database settings.

## dataHelpers.py
dataHelpers.py is full of functions for simple data manipulation, such as string and list conversion. It's not used much anymore, most of the time the custom game classes will handle data manipulation.

## dbConversion.py
dbConversion.py contains functions for converting outdated databases into databases that work with the modern codebases.

## helpers.py
helpers.py contains all the parent game classes. Each Sabacc variant has it's own directory (traditional/ and corellian_spike/) with the child classes.

## pipRequirements.txt
pipRequirements.txt contains all the required Python libraries. Install using `pip install -r pipRequirements.txt`.

## requirements.txt
requirements.txt contains the basic requirements for the backend to work.

## traditional/
Code and classes for Traditional Sabacc.

## corellian_spike/
Code and classes for Corellian Spike Sabacc.