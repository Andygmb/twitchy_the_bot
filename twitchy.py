import praw, HTMLParser, json, requests
from config import username, password, subreddit, wiki_stream_config, wiki_streams
from PIL import Image
from StringIO import StringIO

API_ENDPOINT = "http://api.justin.tv/api/stream/list.json?channel="
thumbnail_urls, preview_images, listofresults, livestreams, config_list, results, streamlist = [], [], [], [], [], [], []
stringresults = ""


def check_inbox():
	#Checks our inbox and replies to the message if it's sucessful or not. 
	inbox = r.get_inbox()
	with open("messages_seen.txt", "r") as txt:
		already_seen = txt.read().splitlines()
		for message in inbox:
			if message.id not in already_seen and message.subject == "Twitch.tv request /r/" + str(subreddit):
				msg = message.body.split()
				msg = msg[0]
				if "twitch.tv/" in msg and len((msg[(msg.index(".tv/")+4):len(msg)])) <=25:
					streamlist.append(msg[(msg.index(".tv/")+4):len(msg)])
					message.reply("Your stream has been added to the list of livestreams in the sidebar, \
it will display the next time you are live on twitch.tv. \n \n Problems? Contact \
the developer [here](http://www.reddit.com/user/Cheesydude/). Do not reply to this message.")
				else:
					message.reply("Message not understood. Please make sure your message only contains a \
link to your twitch.tv page. E.G. \n \n >http://www.twitch.tv/USERNAME \n \n \
[Click here to resend this message](http://www.reddit.com/message/compose?to=" + username + "&subject=Twitch.tv+request+%2Fr%2F" + str(subreddit) \
+ "&message=http%3A%2F%2Fwww.twitch.tv%2FUSERNAMEHERE)")
				with open("messages_seen.txt", "a") as output:
					output.write("\n" + message.id)
	return streamlist

def chunker(seq, size):
	#Chunks up the stream wikipage into chunks to send to twitch.tv 
	#because otherwise it'd be wasteful to send a bunch of single requests.
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

def get_stream_list(subreddit):
	#This tries to get the config settings for meta_games from wiki_stream_config, and the list of streams from wiki/streams/
	#It will then check the bot's inbox for any new livestreams it's been messaged, and add those to the /wiki/streams/ page.
	#after that, it chunks up the streams and requests info from twitch.tv. 
	global config_list
	streamstrings = ""
	try:
		config_list = r.get_wiki_page(subreddit, wiki_stream_config).content_md.splitlines() 
		#Gets the wikipage wiki_stream_config, splits it up into a list seperated by each new line.
		for meta_game in config_list:
		 #loop through each meta_game that is listed in wiki_stream_config
			if meta_game == '': 
			#if it's an empty string (as in a blank line)
				config_list.remove(meta_game) 
				#remove it from the config list
	except Exception: 
	#if there's an error
		config_list = [] 
		#set config list to an empty list
	stream_wikipage = r.get_wiki_page(subreddit, wiki_streams).content_md.splitlines()
	for stream in stream_wikipage[:]:
		if stream == '':
			stream_wikipage.remove(stream)
			#Same as above
		streamstrings += stream + "\n"
	check_inbox()
	if len(streamlist):
		for stream in streamlist:
			if stream not in stream_wikipage:
				streamstrings += "\n" + stream
				stream_wikipage.append(stream)
		subreddit.edit_wiki_page(wiki_streams, streamstrings)
	for chunk in chunker(stream_wikipage, 100): 
	#For chunk of 100 (or less, if the list is not 100 long.)
		API_ENDPOINT = "http://api.justin.tv/api/stream/list.json?channel=" 
		#This is just here to reset the API string after a chunk is looped through
		for stream in chunk:
			API_ENDPOINT += stream + ","
		get_stream_info(API_ENDPOINT)
	parse_stream_info()

def get_stream_info(api_link):
	#This checks that there was any data received in the chunk, and if there was, it appends it to livestreams list.
	global livestreams
	data = requests.get(api_link).json() 
	#Get the JSON data from our api request.
	if len(data): 
		livestreams.append(data)
		

def parse_stream_info():
	#Formats the stream info (if there was any received) to be posted to the reddit sidebar. 
	#Also prepares the thumbnail urls to be put into a spritesheet. 
	n = 0
	if not len(livestreams):
		results.append("**No streams are currently live.**\n") 
	#if it doesn't contain anything (meaning there are no current live streams), append results with the no streams are live string. 
	for streamer_list in livestreams: 
	#looping through the JSON structure 
		for streamer_info_dict in streamer_list:
			if not len(config_list) or streamer_info_dict["channel"]["meta_game"] in config_list:
			#if the meta_game is in config_list, do the following:
				title = streamer_info_dict["title"] 
				# set title to the stream title 
				if len(title) >= 50:
					title = title[0:47] + "..." 
					# If the title's length is  more than 50 chars, only use the first 50 for the title on reddit, 
					# then add on some elipises or whatever the fuck they're called
				name = streamer_info_dict["channel"]["login"] 
				# name is the streamers username
				viewercount = "{:,}".format(streamer_info_dict["channel_count"]) 
				#Formats the viewercount to add commas like: 1,000 
				thumbnail_urls.append(streamer_info_dict["channel"]["screen_cap_url_small"]) 
				# Appending the thumbnail url to a list to use later 
				results.append("> " + str(n) + ". " + "**[" + name + "](http://twitch.tv/" + name + ")**" + "\
- **" + viewercount + " Viewers**" + "\n" + "[" + title + "](http://twitch.tv/" + name + ")" + "\n") 
				#Constructing the final string we'll post to the reddit sidebar
				n += 1 
				# n is used above in the final string to make it an ordered list 1. 2. 3., etc.

	for url in thumbnail_urls:
		preview_data = requests.get(url).content  
		# Download images
		preview_img = Image.open(StringIO(preview_data))  
		# Convert to PIL Image
		preview_images.append(preview_img) 
		# Add image to preview_images list
	return results, preview_images 
	#return the results (the list of strings we'll post to the sidebar), and the preview_images which are the thumbnail images.

def create_spritesheet(thumblist):
	#Puts the thumbnail images into a spritesheet.
	w, h = 70, 53 * (len(thumblist) or 1)
	spritesheet = Image.new("RGB", (w, h))
	xpos = 0
	ypos = 0
	for img in thumblist:
		bbox = (xpos, ypos)
		spritesheet.paste(img,bbox)
		ypos = ypos + 53 
		# Increase ypos by 53 pixels (move down the image by 53 pixels so we can place the image in the right position next time this loops.)
	spritesheet.save("thumbnails/img.png") 
	# Save it as img.png in thumbnails folder


##Finally, we upload the thumbnail images, put the streams into the sidebar between our markers,
##and update the stylesheet (the stylesheet update is to stop the thumbnail images being cached serverside).
r = praw.Reddit("Twitch.tv sidebar bot for " + subreddit + " by /u/Cheesydude") #log into reddit
r.login(username=username, password=password)
subreddit = r.get_subreddit(subreddit) 
# Get the subreddit object for our subreddit
get_stream_list(subreddit)
if results != ['**No streams are currently live.**\n']: 
# If the results from doing all the functions above is NOT equal to no streams are currently live, do the following shit:
	create_spritesheet(preview_images)
	subreddit.upload_image("thumbnails/img.png", "img", False)
	stylesheet = r.get_stylesheet(subreddit)
	stylesheet = HTMLParser.HTMLParser().unescape(stylesheet["stylesheet"])
	subreddit.set_stylesheet(stylesheet, prevstyle=None) 
	# set the stylesheet as the stylesheet we just copied. We have to do this because otherwise the thumbnail images we just uploaded 
	# would not refresh on reddit's server side, because for some reason they are cached untill you save the stylesheet.
	sidebar = r.get_settings(subreddit)
	desc = HTMLParser.HTMLParser().unescape(sidebar['description'])
	try:
		startmarker, endmarker = desc.index("[](#TwitchStartMarker)"), desc.index("[](#TwitchEndMarker)") + len("[](#TwitchEndMarker)")
		stringresults = "".join(results)
		desc = desc.replace(desc[startmarker:endmarker], "[](#TwitchStartMarker)" + "\n \n" + stringresults + "\n \n" + "[](#TwitchEndMarker)")
		subreddit.update_settings(description=desc.encode('utf8'))
	except:
		pass
else: 
# else (if there's no livestreams)
	sidebar = r.get_settings(subreddit)
	desc = HTMLParser.HTMLParser().unescape(sidebar['description'])
	try:
		startmarker, endmarker = desc.index("[](#TwitchStartMarker)"), desc.index("[](#TwitchEndMarker)") + len("[](#TwitchEndMarker)")
		stringresults = "".join(results)
		desc = desc.replace(desc[startmarker:endmarker], "[](#TwitchStartMarker)" + "\n \n" + stringresults + "\n \n" + "[](#TwitchEndMarker)")
		subreddit.update_settings(description=desc.encode('utf8'))
	except:
		pass
