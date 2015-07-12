import requests
import re
import time
import praw
import HTMLParser
import json
from config import username, password, subreddit
from PIL import Image
from StringIO import StringIO


def chunker(seq, size):
	return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

class configuration():
	def __init__(self):
		self.r, self.subreddit = self.reddit_setup()
		self.config = self.get_config()
		self.streams = self.wikipage_check(self.config["wikipages"]["stream_list"])
		self.banned = self.wikipage_check(self.config["wikipages"]["ban_list"])
		self.messages = self.check_inbox()

	def get_config(self):
		try:
			config = self.r.get_wiki_page(self.subreddit,"twitchbot_config").content_md
			try:
				config = json.loads(config)
			except ValueError:
				print "No JSON object could be found, or the config page has broken JSON.\nUse www.jsonlint.com to validate your wiki config page."
				self.wikilog("No JSON object could be decoded from twitchbot config wiki page.")
				raise
			return HTMLParser.HTMLParser().unescape(config)
		except requests.exceptions.HTTPError:
			print "Couldn't access config wiki page, reddit may be down."
			self.config = {"wikipages":{"error_log":"twitchbot_error_log"}}
			self.wikilog("Couldn't access config wiki page, reddit may be down.")
			raise

	def wikilog(self, error):
		self.r.edit_wiki_page(self.subreddit, self.config["wikipages"]["error_log"], error, error)

	def reddit_setup(self):
		print "Logging in"
		r = praw.Reddit("Sidebar livestream updater for /r/{} by /u/andygmb ".format(subreddit))
		r.refresh_access_information()
		sub = r.get_subreddit(subreddit)
		return r, sub

	def wikipage_check(self, wikipage):
		try:
			wiki_list = self.r.get_wiki_page(self.subreddit, wikipage).content_md.splitlines()
			results = [item.lower() for item in wiki_list if len(item)]
		except requests.exceptions.HTTPError:
			print "No wikipage found at http://www.reddit.com/r/{}/wiki/{}".format(self.subreddit.display_name, wikipage)
			self.wikilog("Couldn't access wikipage at /wiki/{}/".format(wikipage))
			results = []
		return results

	def check_inbox(self):
		streams = []
		inbox = self.r.get_inbox()
		print "Checking inbox for new messages"
		for message in inbox:
			if message.new \
			and message.subject == "Twitch.tv request /r/{}".format(self.subreddit):
				message_content = message.body.split()[0]
				try:
					re_pattern = 'twitch.tv/(\w+)'
					# pattern matches twitch username in the first group
					re_result = re.search(re_pattern, message_content)
					if re_result:
						stream_name = re_result.group(1).lower()
						# extract the username stored in regex group 1
					else:
						print "Could not find stream name in message."
						continue # skip to next message
				except ValueError:
					message.mark_as_read()
					stream_name = "null"
					print "Could not find stream name in message."

				if "twitch.tv/" in message_content \
				and len(stream_name) <=25 \
				and stream_name not in self.banned \
				and stream_name not in self.streams:
					streams.append(stream_name)
					message.reply(self.config["messages"]["success"].format(subreddit=self.subreddit))
					message.mark_as_read()

				elif stream_name in self.banned:
					message.reply(self.config["messages"]["banned"].format(subreddit=self.subreddit))
					message.mark_as_read()

				elif stream_name in self.streams:
					message.reply(self.config["messages"]["already_exists"].format(subreddit=self.subreddit))
					message.mark_as_read()

		if streams:
			new_streams = list(set([stream for stream in streams if stream not in [self.streams, self.banned]]))
			self.streams.extend(new_streams)
			self.subreddit.edit_wiki_page(
				self.config["wikipages"]["stream_list"], 
				"\n".join(self.streams), 
				reason="Adding stream(s): " + ", ".join(new_streams)
				)

	def update_stylesheet(self):
		print "Uploading thumbnail image(s)"
		try:
			self.subreddit.upload_image("img.png", "img", False)
		except praw.errors.APIException:
			print "Too many images uploaded."
			self.wikilog("Too many images uploaded to the stylesheet, max of 50 images allowed.")
			raise
		stylesheet = self.r.get_stylesheet(self.subreddit)
		stylesheet = HTMLParser.HTMLParser().unescape(stylesheet["stylesheet"])
		self.subreddit.set_stylesheet(stylesheet)

	def update_sidebar(self):
		print "Updating sidebar"
		sidebar = self.r.get_settings(self.subreddit)
		submit_text = HTMLParser.HTMLParser().unescape(sidebar["submit_text"])
		desc = HTMLParser.HTMLParser().unescape(sidebar['description'])
		try: 
			start = desc.index(self.config["stream_marker_start"])
			end = desc.index(self.config["stream_marker_end"]) + len(self.config["stream_marker_end"])
		except ValueError:
			print "Couldn't find the stream markers in the sidebar"
			self.wikilog("Couldn't find the stream markers in the sidebar.")
			raise
		livestreams_string = "".join(livestreams.streams).encode("ascii", "ignore")
		desc = desc.replace(
			desc[start:end], 
			"{} {} {}".format(self.config["stream_marker_start"],livestreams_string,self.config["stream_marker_end"])
			)
		self.subreddit.update_settings(description=desc.encode('utf8'), submit_text=submit_text)


class livestreams():
	def __init__(self, config):
		self.config = config
		self.streams = []
		self.thumbnails = []

	def check_stream_length(self):
		max_streams = int(self.config.config["max_streams_displayed"])
		if len(self.streams) > max_streams:
			self.streams = self.streams[:max_streams]
			self.thumbnails = self.thumbnails[:max_streams]
			print "There are more than {max_stream_count} streams currently \
			- the amount displayed has been reduced to {max_stream_count}. \
			You can increase this in your config.py file.".format(max_stream_count=max_streams)
		if len(self.streams):
			return True
		else:
			self.streams = self.config.config["no_streams_string"]
			return False

	def get_livestreams(self):
		print "Requesting stream info"
		for chunk in chunker(self.config.streams, 100):
			api_link = "https://api.twitch.tv/kraken/streams?channel="
			for stream in chunk:
				api_link += stream + ","
			try:
				data = requests.get(api_link).json()
				if data["_total"] > 0:
					self.parse_stream_info(data)
				else:
					pass
			except:
				pass

	def parse_stream_info(self, data):
		print "Parsing stream info"
		allowed_games = [str(game.lower()) for game in self.config.config["allowed_games"]]
		for streamer in data["streams"]:
			if not len(allowed_games) or streamer["game"].lower() in allowed_games:
				game = streamer["game"].lower()
				title = streamer["channel"]["status"]
				# Removing characters that can break reddit formatting
				title = re.sub(r'[*)(>/#\[\]\\]*', '', title)
				title = title.replace("\n", "")
				#Add elipises if title is too long
				if len(title) >= int(self.config.config["max_title_length"]):
					title = title[0:int(self.config.config["max_title_length"]) - 3] + "..." 
				name = streamer["channel"]["name"].encode("utf-8")
				display_name = streamer["channel"]["display_name"].encode("utf-8")
				viewercount = "{:,}".format(streamer["viewers"])
				self.thumbnails.append(streamer["preview"]["template"])
				self.streams.append(
					HTMLParser.HTMLParser().unescape(self.config.config["string_format"].format(name=name, title=title, viewercount=viewercount, display_name=display_name))
					)

	def create_spritesheet(self):
		print "Creating image spritesheet"
		width, height = (
			int(self.config.config["thumbnail_size"]["width"]), 
			int(self.config.config["thumbnail_size"]["height"])
			)
		preview_images = []
		for url in self.thumbnails:
			preview_data = requests.get(url.format(width=str(width), height=str(height) )).content
			# Download image
			preview_img = Image.open(StringIO(preview_data))
			# Convert to PIL Image
			preview_images.append(preview_img)
		w, h = width, height * (len(preview_images) or 1)
		spritesheet = Image.new("RGB", (w, h))
		xpos = 0
		ypos = 0
		for img in preview_images:
			bbox = (xpos, ypos)
			spritesheet.paste(img,bbox)
			ypos = ypos + height 
		spritesheet.save("img.png")


if __name__ == "__main__":
	config = configuration()
	livestreams = livestreams(config)
	livestreams.get_livestreams()
	if livestreams.check_stream_length():
		livestreams.create_spritesheet()
		livestreams.config.update_stylesheet()
		livestreams.config.update_sidebar()
	else:
		livestreams.config.update_sidebar()
