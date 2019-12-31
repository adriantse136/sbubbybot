#Sheen Patel
#u/SbubbyBot for the the mods of r/Sbubby

import praw #all the reddit i/o
import threading #thread handler so multiple things can get done
import os #to get enviroment variables containing secrets
import psycopg2 #used for postgresql database stuff
from datetime import datetime #need to get current time for multiple things

#Setting this var to true will allow the bot to actually comment on the post and not dry-run.
PRODUCTION = False

#create the reddit instance for the bot to use
reddit = praw.Reddit(
        user_agent='SbubbyBot v. 1.1 by u/CrazedPatel',
        client_id=os.environ['client_id'],
        client_secret=os.environ['client_secret'],
        username=os.environ['reddit_username'],
        password=os.environ['reddit_password'])

#mark the subreddit
sbubby = reddit.subreddit('sbubby')

#connect to the postgresql database
database = psycopg2.connect(database=os.environ["database_name"], user="sheen", password="", host=os.environ["DATABASE_URL"], port="5432")
cur = database.cursor()

def main():
    print("Running SbubbyBot testing version.")
    monitorSubmissions()
    print("Sbubbybot has finished running with no errors.")
    database.close() #close the database connection.

def monitorSubmissions():
    for submission in sbubby.stream.submissions():

        #TODO make moderator override thing
        #if submission.approved: #There is no such thing as approved. This will need to be changed.
        #    continue

        #need to do flair stuff
        doFlair(submission)

        #need to check database afterwards to see if any are in need of recheck.
        #get all the items from the database (not that many b/c continous movements) and iterate over them
        cur.execute("select * from flairs")
        rows = cur.fetchall()
         #10 minutes is 600 seconds
        #print(now)

        for row in rows:
            print("<Database> submission id: ", row[0])
            print("<Database> Checking Database:: submission time: ", row[1])
            epochTime = row[1].timestamp()
            now = datetime.now().timestamp()
            #check if the post should be removed, otherwise, do nothing
            if epochTime - now > 600:
                #remove the post.
                print("<Database> Time's up! Remove post.")
                submission = reddit.submission(row[0]) #lazy instance of the thing

def doFlair(submission):
    #check to see if flair first
    if submission.link_flair_text == None:
        #check to see if post already been messaged
        hasBeenMessaged = False
        for comment in submission.comments:
            if comment.author == reddit.user.me(): #if i have a top level comment then don't message
                hasBeenMessaged = True
        if not hasBeenMessaged:
            print(f"<Flair> message {submission.name} post to remind to flair!!!")
            print("<Flair> created on: ", submission.created_utc)
            cur.execute(f"INSERT INTO FLAIRS (submission_id, time_created) VALUES ('{submission.id}', to_timestamp({submission.created_utc})) ON CONFLICT (submission_id) DO NOTHING")
            database.commit() #only need to do this one thing
        else:
            print("<Flair> No need for flair message -- one already exists?")

def recheckFlair(submission):
    if submission.link_flair_text == None:
        time = submission.created_utc

def doMagicEye():
    print("<Magic Eye> MAGIC_EYE_BOT comment checker started...")

def howMuchKarmaModmail():
    print("<Karma> Anti-\"how much karma\" bot started...")

def commonRepost():
    print("<Repost> Common reposts bot started...")
    #Check each item in the imgur album -- if any is over the threshold:
    #   make a comment with the similarity amount, and then give link that it is similar to.
    #   mark post as spam(, and if user replies, then send modmail?)

def sundaySbubby():
    print("It is sunday. Sunday Sbubby started...")

if __name__ == "__main__":
    main()
