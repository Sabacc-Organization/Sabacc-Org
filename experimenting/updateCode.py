import os

os.system("mv Sabacc-Deployed/ Sabacc-Deployed-Old/")
os.system("unzip Sabacc-Multiplayer-main.zip")
os.system("mv Sabacc-Multiplayer-main/ Sabacc-Deployed/")

os.system("rm Sabacc-Deployed/sabacc.db")
os.system("rm Sabacc-Deployed/config.yml")
os.system("rm Sabacc-Deployed/static/config.js")

os.system("cp Sabacc-Deployed-Old/sabacc.db Sabacc-Deployed/sabacc.db")
os.system("cp Sabacc-Deployed-Old/config.yaml Sabacc-Deployed/config.yml")
os.system("cp Sabacc-Deployed-Old/static/config.js Sabacc-Deployed/static/config.js")

os.system("mv Sabacc-Deployed/application.py Sabacc-Deployed/app.py")