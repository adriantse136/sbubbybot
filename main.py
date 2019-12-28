#Sheen Patel
#u/SbubbyBot for the the mods of r/Sbubby

import praw #all the reddit i/o
import threading #thread handler so multiple things can get done
import os #to get enviroment variables containing secrets

#create the reddit instance for the bot to use
reddit = praw.Reddit(
        user_agent='(SbubbyBot) v. 1.0',
        client_id=os.environ["client_id"],
        client_secret=os.environ['client_secret'],
        username=os.environ['reddit_username'],
        password=os.environ['reddit_password'])

#mark the subreddit
sbubby = reddit.subreddit('sbubby')

def main():
    print("Running SbubbyBot testing version.")
    monitorSubmissions()
    print("Sbubbybot has finished running with no errors.")

def monitorSubmissions():
    for submission in sbubby.stream.submissions():
        #need to do flair stuff
        doFlair(submission)
        #need to check database afterwards to see if any are in need of recheck.

def doFlair(submission):
    #check to see if flair first
    if submission.link_flair_text == None:
        #check to see if post already been messaged
        hasBeenMessaged = False
        for comment in submission.comments:
            if comment.author == reddit.user.me(): #if i have a top level comment then don't message
                hasBeenMessaged = True
        if not hasBeenMessaged:
            print("message this post to remind to flair!!!")
            #add to remind to flair database. Script will check database at the end of checking each submission?
        else:
            print("no need for flair message!")

def doMagicEye():
    print("MAGIC_EYE_BOT comment checker started...")

def howMuchKarmaModmail():
    print("Anti-\"how much karma\" bot started...")

def commonRepost():
    print("Common reposts bot started...")
    #Check each item in the imgur album -- if any is over the threshold:
    #   make a comment with the similarity amount, and then give link that it is similar to.
    #   mark post as spam(, and if user replies, then send modmail?)

def sundaySbubby():
    print("It is sunday. Sunday Sbubby started...")

if __name__ == "__main__":
    main()
