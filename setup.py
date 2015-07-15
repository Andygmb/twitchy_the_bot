import os

import praw
import json
import requests
from config import username, password, subreddit

# Why is this even a function

def wikilog(r, subreddit, wikipage, error):
    r.edit_wiki_page(subreddit, wikipage, error, error)

if __name__ == "__main__":
    print "Starting setup.py..."
    print "Attempting to log in..."
    r = praw.Reddit("Sidebar livestream updater for /r/{} by /u/andygmb ".format(subreddit))
    try:
        r.login(username=username, password=password)
        print "Success!\n"
    except praw.errors.InvalidUserPass:
        print "Make sure you have your bot's details in config.py"
    sub = r.get_subreddit(subreddit)
    path_to_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default_wiki_config.json")
    with open(path_to_file, "r") as configjson:
        try:
            print "\nAttempting to load default_wiki_config.json..."
            config = json.load(configjson)
            prettyconfig = "    "  + json.dumps(config, indent=4).replace("\n", "\n    ")
            print "Success!\n"
        except ValueError:
            print "Invalid JSON in local file: default_wiki_config.json"
            wikilog(r, sub, "twitchbot_error_log", "Invalid JSON in local file: default_wiki_config.json")
            raise

    try:
        print "Attempting to add default_wiki_config.json to https://www.reddit.com/r/{}/twitchbot_config ...".format(subreddit)
        r.edit_wiki_page(sub, "twitchbot_config", prettyconfig, "Initial setup from setup.py")
        print "Success!\n".format(subreddit)
    except requests.exceptions.HTTPError:
        print "Couldn't access https://www.reddit.com/r/{}/wiki/{}, reddit may be down.".format(subreddit, "twitchbot_config")
        wikilog(r, sub, config["wikipages"]["error_log"], "Couldn't access wiki page, reddit may be down.")
        raise

    for wikipage in config["wikipages"].values():
        try:
            if not "config/" in wikipage:
                try:
                    content = r.get_wiki_page(sub, wikipage).content_md
                except:
                    content = ""
                print "Attempting to set up https://www.reddit.com/r/{}/wiki/{} ...".format(subreddit, wikipage)
                r.edit_wiki_page(sub, wikipage, content.encode("utf8"), "Initial setup from setup.py")
                print "Success!\n".format(wikipage)
        except requests.exceptions.HTTPError:
            print "Couldn't access https://www.reddit.com/r/{}/wiki/{}, reddit may be down.".format(subreddit, wikipage)
            wikilog(r, sub, wikipage, "Couldn't access wiki page, reddit may be down.")
            raise

    if config["accept_messages"].lower() in ["true", "yes", "y"]:
        print "Setup.py finished!\n\n"
        print "By default the bot will respond to PMs and update https://wwww.reddit.com/r/{}/wiki/{} with any twitch.tv links users send it.".format(subreddit, config["wikipages"]["stream_list"])
        print "Place the following link in your sidebar for people to message the bot twitch.tv streams:"
        print "http://www.reddit.com/message/compose?to={username}&subject=Twitch.tv+request+%2Fr%2F{subreddit}&message=http%3A%2F%2Fwww.twitch.tv%2F{username}".format(username=username, subreddit=subreddit)
        print '\nIf you do not want the bot to update the list of streams through PM, please edit https://wwww.reddit.com/r/{}/wiki/twitchbot_config and set "accept_messages" to "False".'.format(subreddit)
    else:
        print "Setup.py finished!\n\n"
