import praw, HTMLParser, json, requests, re, time
from config import username, password, subreddit, wiki_stream_config, wiki_streams, wiki_bans, max_stream_count
from PIL import Image
from StringIO import StringIO


def chunker(seq, size):
	return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

class configuration():
	def __init__(self):
		self.r, self.subreddit = self.reddit_setup()
		self.meta_games = self.wikipage_check(wiki_stream_config)
		self.streams = self.wikipage_check(wiki_streams)
		self.banned = self.wikipage_check(wiki_bans)
		self.messages = self.check_inbox()


	def reddit_setup(self):
		print "Logging in"
		r = praw.Reddit("Twitch.tv sidebar bot for " + subreddit + " by /u/andygmb") #log into reddit
		r.login(username=username, password=password)
		sub = r.get_subreddit(subreddit)
		return r, sub

	def wikipage_check(self, wikipage):
		try:
			wiki_list = self.r.get_wiki_page(self.subreddit, wikipage).content_md.splitlines()
			for item in wiki_list[:]:
				wiki_list[wiki_list.index(item)] = item.lower()
				if not len(item): 
					wiki_list.remove(item)
		except requests.exceptions.HTTPError:
			print "No wikipage found at http://www.reddit.com/r/" + self.subreddit.display_name + "/wiki/" + wikipage
			wiki_list = []
		return wiki_list

	def check_inbox(self):
		streams = []
		stream_strings = ""
		inbox = self.r.get_inbox()
		print "Checking inbox for new messages"
		for message in inbox:
			if message.new \
			and message.subject == "Twitch.tv request /r/" + str(self.subreddit):
				message_content = message.body.split()[0]
				# This is why I should learn regexp. I am ashamed of the following code:
				try:
					stream_name = message_content[(message_content.index(".tv/")+4):len(message_content)].lower()
				except ValueError:
					message.mark_as_read()
					stream_name = "null"
					print "Could not find stream name in message."
				# If someone sees this and can fix it with regexp, please do a pull request. ^

				if "twitch.tv/" in message_content \
				and len(stream_name) <=25 \
				and stream_name not in self.banned \
				and stream_name not in self.streams:
					streams.append(stream_name)
					message.reply(
						"Your stream will be added to the list of livestreams in the sidebar, \
						it will display the next time you are live on twitch.tv. \n \n Problems? [Contact \
						the moderators here](http://www.reddit.com/message/compose?to=%2Fr%2F"\
						+ str(self.subreddit) + "). \n \n Do not reply to this message."
						)
					message.mark_as_read()


				elif stream_name in self.banned:
					message.reply(
						"Sorry, but that stream is banned from this subreddit. If you feel this is \
						an incorrect ban, [please message the moderators \
						here](http://www.reddit.com/message/compose?to=%2Fr%2F"\
						+ str(self.subreddit) + "). \n \n Do not reply to this message."
						)
					message.mark_as_read()


				elif stream_name in self.streams:
					message.reply(
						"Your stream is already in the list of livestreams that this bot checks. \
						If you have just messaged your stream, please wait 5-10 minutes for the sidebar to update.\
						\n \n Problems? Contact the moderators [here](http://www.reddit.com/message/compose?to=%2Fr%2F"\
						+ str(self.subreddit) + "). \n \nDo not reply to this message."
						)
					message.mark_as_read()

				else:
					pass

		if len(streams):
			for stream in streams[:]:
				if stream not in self.streams \
				and stream not in self.banned:
					stream_strings += "\n" + stream
					self.streams.append(stream)
				else:
					streams.remove(stream)
			self.subreddit.edit_wiki_page(wiki_streams, "\n".join(self.streams), reason="Adding stream(s): " + ", ".join(streams))
			return True
		else:
			return False

	def update_stylesheet(self):
		print "Uploading thumbnail image(s)"
		self.subreddit.upload_image("thumbnails/img.png", "img", False)
		stylesheet = self.r.get_stylesheet(self.subreddit)
		stylesheet = HTMLParser.HTMLParser().unescape(stylesheet["stylesheet"])
		self.subreddit.set_stylesheet(stylesheet, prevstyle=None)

	def update_sidebar(self):
		print "Updating sidebar"
		sidebar = self.r.get_settings(self.subreddit)
		submit_text = HTMLParser.HTMLParser().unescape(sidebar["submit_text"])
		desc = HTMLParser.HTMLParser().unescape(sidebar['description'])
		startmarker, endmarker = desc.index("[](#TwitchStartMarker)"), desc.index("[](#TwitchEndMarker)") + len("[](#TwitchEndMarker)")
		stringresults = "".join(livestreams.streams)
		desc = desc.replace(desc[startmarker:endmarker], "[](#TwitchStartMarker)" + "\n \n" + stringresults + "\n \n" + "[](#TwitchEndMarker)")
		self.subreddit.update_settings(description=desc.encode('utf8'), submit_text=submit_text)


def chunker(seq, size):
	return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

class livestreams():
	def __init__(self):
		self.config = config
		self.streams = []
		self.thumbnails = []

	def check_stream_length(self):
		if len(self.streams) > max_stream_count:
			self.streams = self.streams[:max_stream_count]
			self.thumbnails = self.thumbnails[:max_stream_count]
			print "There are more than " + str(max_stream_count) \
			+ " streams currently - the amount displayed has been reduced to " + str(max_stream_count) + \
			". You can increase this in your config.py file."
		if not len(self.streams):
			self.streams = '**No streams are currently live.**\n'
			return False
		elif len(self.streams):
			return True

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
		for streamer in data["streams"]:
			if not len(self.config.meta_games) or streamer["game"].lower() in self.config.meta_games:
				game = streamer["game"].lower()
				title = streamer["channel"]["status"]
				# Removing characters that can break reddit formatting
				title = re.sub(r'[*)(>/#\[\]]', '', title)
				title = title.replace("\n", "")
				#Add elipises if title is too long
				if len(title) >= 50:
					title = title[0:47] + "..." 
				name = streamer["channel"]["name"].encode("utf-8")
				viewercount = "{:,}".format(streamer["viewers"])
				self.thumbnails.append(streamer["preview"]["small"])
				self.streams.append("> 1. " + "**[" + name + "](http://twitch.tv/" + name + ")** - **"\
				+ viewercount + " Viewers**" + "\n" + "[" + title + "](http://twitch.tv/" + name + ")" + "\n")

	def create_spritesheet(self):
		print "Creating image spritesheet"
		preview_images = []
		for url in self.thumbnails:
			preview_data = requests.get(url).content
			# Download image
			preview_img = Image.open(StringIO(preview_data))
			# Convert to PIL Image
			preview_images.append(preview_img)
		# Puts the thumbnail images into a spritesheet.
		w, h = 80, 50 * (len(preview_images) or 1)
		spritesheet = Image.new("RGB", (w, h))
		xpos = 0
		ypos = 0
		for img in preview_images:
			bbox = (xpos, ypos)
			spritesheet.paste(img,bbox)
			ypos = ypos + 50 
			# Increase ypos by 50 pixels (move down the image by 50 pixels 
			# so we can place the image in the right position next time this loops.)
		spritesheet.save("thumbnails/img.png") 
		# Save it as img.png in thumbnails folder

if __name__ == "__main__":
	config = configuration()
	livestreams = livestreams()
	livestreams.get_livestreams()
	if livestreams.check_stream_length():
		livestreams.create_spritesheet()
		livestreams.config.update_stylesheet()
		livestreams.config.update_sidebar()
	else:
		livestreams.config.update_sidebar()