# SbubbyBot
A bot that helps moderate r/sbubby. Does a bunch of things like flairing reminders and removing common reposts.
# Installation
You will need to add all the environment variables (see below) as well as create a bot on reddit. You will need to create a bot that has a client Id and secret, can be found on preferences page of reddit.com
## Running locally -> not on Heroku
Run the main.py file after you set up the database and .env file (and ofc installing dependencies from requirements.txt)
This runs on python3.7 and 3.8 and probably older too but not tested.
You will also need to set `PRODUCTION` variable in main.py to True for it to actually do actions.
## Enviroment Vars Needed
The following variables should be put into a .env file in the root directory when testing locally.
**DO NOT** let the env file be uploaded to Heroku, instead, these same variables will have to be defined in the Enviroment Variable settings IN HEROKU.
| Variables    | Explanation |
|--------------|-------------|
| `client_id`  | Client ID of reddit bot |
| `client_secret` | secret of reddit bot |
| `reddit_username` | the reddit username of account bot is set up under (will control that account) |
| `reddit_password` | password of above |
| `database_name` | name of postgres database |
| `database_password` | password (can be empty if no password) of database |
| `DATABASE_URL` | url of database, on heroku this is autofilled |

**`DATABASE_URL`** Must be all caps because Heroku will automatically set the Database URL for when it runs on Heroku.
## Database setup instructions
* Need a postgres 12 database, make it on user postgres (default user)
* name it `flairs`
* make the submission_id the primary key
* copy paste of `\d flairs` below (aka how to do)

|   Column     |            Type             | Collation | Nullable | Default 
---------------|-----------------------------|-----------|----------|---------
 submission_id | character(6)                |           | not null | 
 time_created  | timestamp without time zone |           | not null | 
 comment_id    | character varying(8)        |           |          | 
