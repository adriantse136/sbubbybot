# Sheen Patel
# u/SbubbyBot for the the mods of r/Sbubby

import threading  # to be able to run in threads
import praw  # all the reddit i/o
import os  # to get enviroment variables containing secrets
import psycopg2  # used for postgresql database stuff
from datetime import datetime  # need to get current time for multiple things
import time  # for time.sleep
from dotenv import load_dotenv  # need this to import env. vars
from sys import exit  # to exit gracefully from Ctrl+c
from signal import signal, SIGINT  # to exit gracefully from C
# has the sundaySbubby functions
from sundaySbubday import sundaySbubby, unSundaySbubby

# load env variables (only for locally testing, heroku takes care of it othewise)
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

# MAGIC_EYE_BOT's profile
magicEye = reddit.redditor('MAGIC_EYE_BOT')

# connect to the postgresql database
database = psycopg2.connect(user="postgres", password=os.environ['database_password'],
                            database=os.environ["database_name"], host=os.environ["DATABASE_URL"], port="5432")
cur = database.cursor()


def main():
    # create the two threads:
    #   1. common repost + flair submission stream
    #   2. one-minute timer to do flairdb stuff + sunday sbubby
    while True:
        print("<FLAIRS> Running monitor submissions.")
        # monitorSubmissions()
        time.sleep(60)
    print("Sbubbybot has finished running with no errors.")
    database.close()  # close the database connection.


def repostAndFlairThread():
    for submission in sbubby.stream.submissions():

        # skip post if author is moderator
        moderators = sbubby.moderator()
        if submission.author in moderators:
            continue

        # only do the stuff if the post hasn't been clicked
        if submission.clicked is False:
            doFlair(submission)
            commonRepost(submission)
            # need to commit after each time because of other thread and bc forever for loop
            database.commit()


def oneMinTimerThread():  # not exactly one minute
    while True:
        # check for any flair stuff that needs to be checked up on
        checkFlairDB()
        howMuchKarmaModmail()

        # attempt to do sunday sbubday, making sure there is no duplicates is handled in the function
        attemptSundaySbubday()

        time.sleep(60)  # 1 min rest


def attemptSundaySbubday():
    print("Attempting to do a sunday sbubday activity!")
    # TODO: finish this function!!!
    # get the current time. Check the date.


def checkFlairDB():
    cur.execute("select * from flairs;")
    rows = cur.fetchall()

    # row[0] = submission id, row[1] = time post created, row[2] = comment telling to flair id.
    for row in rows:
        epochTime = row[1].timestamp()
        now = datetime.now().timestamp()
        submission = reddit.submission(row[0])  # lazy instance of the thing
        # check if the post should be removed, otherwise, do nothing
        # TODO make sure post is not removed before doing anything
        if now - epochTime > 590 and submission.link_flair_text is None:
            # remove the post.
            print("<Database> Post ", submission.id,
                  " is past the time and has no flair.")
            print("<Database> Time's up! Remove post.")

            # remove from database
            cur.execute(f"DELETE from flairs where submission_id='{row[0]}';")

            # do the comment thing
            if PRODUCTION:
                comment_id = row[2]
                if comment_id is None:
                    # need to find the real one
                    submission.comments.replace_more(limit=None)
                    for comment in submission.comments:
                        if comment.author == reddit.user.me():
                            comment_id = comment.id
                    print("no comment found by me")
                    continue  # continues with the next submission in db
                reddit.comment(comment_id).delete()

                if sbubby.user_is_moderator:
                    # remove post
                    submission.mod.remove(
                        mod_note="Removed for lack of flair by sbubbybot")
                    submission.mod.send_removal_message(
                        "Hi! Your post was removed because it had no flair after 10 minutes of you being notified to flair your post. This messsage was sent automatically, if you think it's an error, send a modmail")
                    submission.unsave()

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
                    submission.comments.replace_more(limit=None)
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
    # get all the comments from MAGIC_EYE_BOT and in r/Sbubby
#    for comment in magicEye.stream.comments():
#        if comment.subreddit == "sbubby":

    # check author
    # if it isn't magic eye, ignore
    # if it is magic eye
    #   check child comments for any replies from the parent post's author
    #   if there are none, reapprove
    #   if there is one but is a short comment that isn't requesting a post review at all, reapprove
    #   if it doesn't appear to be a short comment not requesting a review, ignore thread for mod review


def howMuchKarmaModmail():
    print("<Karma> Anti-\"how much karma\" bot started...")
    # need to get a stream of modmail. Run this in own process?
    # with the stream, check for key words in the post: How much Karma.
    # auto-reply and hide post?


def commonRepost(submission):
    print("<Repost> Common reposts bot started...")
    # Check each item in the imgur album -- if any is over the threshold:
    #   make a comment with the similarity amount, and then give link that it is similar to.
    #   mark post as spam(, and if user replies, then send modmail?)


def sigintHandler(signal, frame):
    print(f"\u001b[3D Received (most likely) Ctrl+c, exiting.")
    exit(0)


if __name__ == "__main__":
    signal(SIGINT, sigintHandler)
    main()
