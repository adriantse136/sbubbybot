# Sheen Patel
# u/SbubbyBot for the the mods of r/Sbubby

import praw  # all the reddit i/o
import threading  # thread handler so multiple things can get done
import os  # to get enviroment variables containing secrets
import psycopg2  # used for postgresql database stuff
from datetime import datetime  # need to get current time for multiple things
import time  # for time.sleep #TODO migrate all of datetime to time for less imports
# need this to import env. vars while testing locally
from dotenv import load_dotenv

# load env variables (only for locally)
load_dotenv()

# Setting this var to true will allow the bot to actually comment on the post and not dry-run.
PRODUCTION = False

# create the reddit instance for the bot to use
reddit = praw.Reddit(
    user_agent='SbubbyBot v. 1.1 by u/CrazedPatel',
    client_id=os.environ['client_id'],
    client_secret=os.environ['client_secret'],
    username=os.environ['reddit_username'],
    password=os.environ['reddit_password'])

# mark the subreddit
sbubby = reddit.subreddit('sbubby')

# connect to the postgresql database
database = psycopg2.connect(user="postgres", password="qwerty",
                            database=os.environ["database_name"], host=os.environ["DATABASE_URL"], port="5432")
cur = database.cursor()


def main():
    print("Running SbubbyBot testing version.")
    while True:
        print("<FLAIRS> Running monitor submissions.")
        monitorSubmissions()
        time.sleep(60)
    print("Sbubbybot has finished running with no errors.")
    database.close()  # close the database connection.


def monitorSubmissions():
    for submission in sbubby.new(limit=20):

        # TODO make moderator override thing
        # if submission.approved: #There is no such thing as approved. This will need to be changed.
        #    continue

        # need to do flair stuff
        if submission.clicked is False:
            doFlair(submission)
    # some of the posts from the prev. for loop could have inserted into db, now do thing.
    database.commit()
    # after all the submissions are monitored and potentially added to db, now we need to check the database for marked posts
    cur.execute("select * from flairs;")
    rows = cur.fetchall()

    # row[0] = submission id, row[1] = time post created, row[2] = comment telling to flair id.
    for row in rows:
        epochTime = row[1].timestamp()
        now = datetime.now().timestamp()
        submission = reddit.submission(row[0])  # lazy instance of the thing
        # check if the post should be removed, otherwise, do nothing
        if now - epochTime > 590 and submission.link_flair_text is None:
            # remove the post.
            print("<Database> Post ", submission.id,
                  " is past the time and has no flair.")
            print("<Database> Time's up! Remove post.")

            # remove from database
            cur.execute(f"DELETE from flairs where submission_id='{row[1]}';")

            # do the comment thing
            if PRODUCTION:
                comment_id = row[2]
                if comment_id is None:
                    # need to find the real one
                    for comment in submission.comments:
                        if comment.author == reddit.user.me():
                            comment_id = comment.id
                    print("no comment found by me")
                    continue  # continues with the next submission in db
                reddit.comment(comment_id).delete()
                # TODO remove post itself
                # TODO send a mail message or comment to tell user what happened.

        elif submission.link_flair_text is None:
            # there is a flair.
            print(
                f"<Database> {submission.id} already has flair, removing from db.")
            cur.execute(f"DELETE from flairs where submission_id='{row[0]}';")
            if PRODUCTION:
                # remove the comment as the flair is set
                comment_id = row[2]
                if comment_id is None:
                    # need to find the real one
                    for comment in submission.comments:
                        if comment.author == reddit.user.me():
                            comment_id = comment.id
                    print("no comment found by me")
                    continue  # continues with the next submission in db
                reddit.comment(comment_id).delete()

    database.commit()  # once all the querys set, then execute all at once.


def doFlair(submission):
    # check to see if flair first
    print("<Flair> Checking ", submission.id)
    if submission.link_flair_text is None and submission.saved is False:
        # check to see if post already been messaged
        hasBeenMessaged = False
        for comment in submission.comments:
            if comment.author == reddit.user.me():  # if i have a top level comment then don't message
                hasBeenMessaged = True
        if not hasBeenMessaged:
            submission.save()
            print(
                f"<Flair> message {submission.name} post to remind to flair!")
            print("<Flair>   created on: ", submission.created_utc)
            comment_id = None  # only used if PRODUCTION is true, will still insert into db as None
            if PRODUCTION:
                # make a comment on this post.
                comment = submission.reply("""# It seems you didn't flair your post!
                Please flair your post now or it might get taken down!
                This comment was made by a bot (contact me @ u/CrazedPatel)""")
                if comment is not None:
                    comment_id = comment.id
            cur.execute(
                f"INSERT INTO FLAIRS (submission_id, time_created, comment_id) VALUES ('{submission.id}', to_timestamp({submission.created_utc}), '{comment_id}') ON CONFLICT (submission_id) DO NOTHING")
        else:
            print("<Flair> No need for flair message -- one already exists?")


def doMagicEye():
    print("<Magic Eye> MAGIC_EYE_BOT comment checker started...")


def howMuchKarmaModmail():
    print("<Karma> Anti-\"how much karma\" bot started...")


def commonRepost():
    print("<Repost> Common reposts bot started...")
    # Check each item in the imgur album -- if any is over the threshold:
    #   make a comment with the similarity amount, and then give link that it is similar to.
    #   mark post as spam(, and if user replies, then send modmail?)


def sundaySbubby():
    print("It is sunday. Sunday Sbubby started...")


if __name__ == "__main__":
    main()
