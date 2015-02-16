import praw
import json
import HTMLParser
import requests
from config import username, password, subreddit

def wikilog(r, subreddit, wikipage, error):
	r.edit_wiki_page(subreddit, wikipage, error, error)

if __name__ == "__main__":
	r = praw.Reddit("Twitch.tv sidebar bot for {} by /u/andygmb".format(subreddit))
	r.login(username=username, password=password)
	sub = r.get_subreddit(subreddit)

	with open("default_wiki_config.json", "r") as configjson:
		try:
			config = json.load(configjson)
		except ValueError:
			print "Invalid JSON in local file: default_wiki_config.json"
			wikilog(r, sub, "twitchbot_error_log", "Invalid JSON in local file: default_wiki_config.json")

	try:
		r.edit_wiki_page(sub, "twitchbot_config", json.dumps(config, indent=4), "Initial setup from setup.py")
	except requests.exceptions.HTTPError:
		print "Couldn't access /wiki/{}, reddit may be down.".format("twitchbot_config")
		wikilog(r, sub, config["wikipages"]["error_log"], "Couldn't access wiki page, reddit may be down.")

	for wikipage in config["wikipages"].values():
		try:
			r.edit_wiki_page(sub, wikipage, " ", "Initial setup from setup.py")
		except requests.exceptions.HTTPError:
			print "Couldn't access /wiki/{}, reddit may be down.".format(wikipage)
			wikilog(r, sub, wikipage, "Couldn't access wiki page, reddit may be down.")

	print "http://www.reddit.com/message/compose?to={username}&subject=Twitch.tv+request+%2Fr%2F{subreddit}&message=http%3A%2F%2Fwww.twitch.tv%2F{username}".format(username=username, subreddit=subreddit)