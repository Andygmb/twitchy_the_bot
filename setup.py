import praw
import json
import HTMLParser
import requests
from config import username, password, subreddit

r = praw.Reddit("Twitch.tv sidebar bot for {} by /u/andygmb".format(subreddit))
r.login(username=username, password=password)
sub = r.get_subreddit(subreddit)

def wikilog(r, subreddit, wikipage, error):
	r.edit_wiki_page(subreddit, wikipage, error, error)

with open("default_wiki_config.json", "r") as configjson:
	try:
		config = json.load(configjson)
	except ValueError:
		print "Invalid JSON in default_wiki_config.json"
		wikilog(r, sub, "twitchbot_error_log", "Invalid JSON in default_wiki_config.json")

try:
	r.edit_wiki_page(
		sub, 
		config["config"], 
		json.dumps(wiki_config, indent=4), 
		"Initial commit from setup.py with default config values"
		)
except requests.exceptions.HTTPError:
	print "Couldn't access wiki page, reddit may be down."
	wikilog(r, sub, "twitchbot_error_log", "Couldn't access wiki page, reddit may be down.")
