# import praw
from main import reddit, sbubby, PRODUCTION


def sundaySbubby():
    print("It is sunday. Sunday Sbubby started...")
    # Get and remove the flair templates:
    for flairTemp in sbubby.flair.templates:
        print(flairTemp)
        if flairTemp == "Eaten Fresh" or flairTemp == "IRL" or flairTemp == "Logoswap":
            # found flair to remove -- now removing it!
            if PRODUCTION:  # only actually remove if production is on
                sbubby.flair.templates.delete(flairTemp["id"])
    # get the automod post.
    # sort subreddit by new for author:AutoModerator
    link = None
    linkMessage = "Please see the comments for the post to request new Sbubbies."
    for submission in sbubby.search("author:AutoModerator", sort="new", time_filter="day"):
        # only want to use the first one because it is the most recent
        link = submission
        linkMessage = f"[Go to the latest request thread here to request a sbubby]({link.url})"
        break
    if link is None:
        # we weren't able to find a link, so fail angrily!!!
        print(
            "\u001b[1mCould not find the Automoderator link! will use placeholder!\u001b[0m")
    message = """
```md
For those out of the loop: Sunday Sbubday is a weekly event attempting to bring back more creativity and make Eef Freef/Eeble Freeble edits more common!

Quick FAQ:

>When does Sunday Sbubday start?

It starts 00:00 Eastern Time every Sunday. If you posted at exactly this time you'll still be let through but other posters won't be.

>What is an Eef Freef!/Eeble Freeble! edit?

Eef Freef! sbubbies are in-spirit sbubbies. An in-spirit sbubby is nonsensical, like [the original sbubby](https://redd.it/5e2gsk/). Out-of-spirit sbubbies are the same, except they make some sense. An Eeble Freeble! sbubby, aka squbbly, is pretty much a surreal sbubby with unusual changes to the logo, such as cleanly distorted text which creates some image or otherwise surreal mess. See [the original squbbly by Thomilo44](https://redd.it/8wlloq/) for a reference idea.

>Do you guys have a discord?

Yes: https://discord.gg/nErFsAA

>Where can I request sbubbies to be made for me?

{} Posts requesting sbubbies will be removed.
```""".format(linkMessage)
    # with the message, now post it and sticky it. Unsticky the automod post
    if PRODUCTION:
        if link.stickied:
            link.mod.sticky(state=False)
        submission = sbubby.submit(
            "Sunday Sbubday is today!", selftext=message)
        submission.mod.distinguish(
            how='yes', sticky=False)  # stickies to the top


def unSundaySbubby():
    # add flairs eaten Fresh, Logoswap, IRL,
    # unsticky announcement post,
    # resticky requests post
    if PRODUCTION:
        sbubby.flair.link_templates.add("Eaten Fresh!")
        sbubby.flair.link_templates.add("Logoswap")
        sbubby.flair.link_templates.add("IRL")

        # unsticky my post by searching through all the stickied posts to find the one authored by me
        for i in range(1, 5):
            try:
                stickied = sbubby.sticky(number=i)
                if stickied.author == reddit.user.me():
                    stickied.mod.sticky(state=False)
            except:
                break
        # sticky most recent automod post.
        for submission in sbubby.search("author:AutoModerator", sort="new", time_filter="week"):
            submission.mod.sticky(state=True, bottom=False)
            break
