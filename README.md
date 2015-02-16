twitchy_the_bot
===============

A reddit bot that gets twitch.tv streams from wiki pages and adds them to the subreddit's sidebar if they are live. 

##Setup

run setup.py

    python setup.py

This will create the following wiki pages (customizable in default_wiki_config.json)

    /wiki/twitchbot_error_log # Twitchy will log errors in the history function of the wiki
    /wiki/twitchbot_config # The imported config from default_wiki_config.json
    /wiki/banned_streams # A list of banned twitch.tv usernames seperated by newlines
    /wiki/streams # A list of twitch.tv usernames seperated by newlines

setup.py will also print out a string for you to put into your sidebar to allow people to PM the bot their livestreams in the correct format:

    "http://www.reddit.com/message/compose?to={username}&subject=Twitch.tv+request+%2Fr%2F{subreddit}&message=http%3A%2F%2Fwww.twitch.tv%2F{username}" 

with your bots username and the subreddit it's running in (taken from config.py) substituted where marked.


###twitchbot_config

All of the following config is editable in default_wiki_config.json before you run setup.py, and after you've ran setup.py the bot will pull it from `/wiki/twitchbot_config`

    {
            "max_streams_displayed":"12",
            "max_title_length":"50",
            "thumbnail_size":{
                "width":"80",
                "height":"50"
            },
            "stream_marker_start":"[](#startmarker)",
            "stream_marker_end":"[](#endmarker)",
            "string_format":"> 1. **[{name}](http://twitch.tv/{name})** -**{viewercount} Viewers**\n[{title}](http://twitch.tv/{name})\n",
            "no_streams_string":"**No streams are currently live.**\n",
            "wikipages":{
                "error_log":"twitchbot_error_log",
                "stream_list":"streams",
                "ban_list":"banned_streams"
            },
            "allowed_games":[],
            "messages":{
                "success":"Your stream will be added to the list of livestreams in the sidebar, it will display the next time you are live on twitch.tv.\n\nProblems? [Contact the moderators here](http://www.reddit.com/message/compose?to=%2Fr%2F{subreddit})\n\n Do not reply to this message.",
                "banned":"Sorry, but that stream is banned from this subreddit. If you feel this is an incorrect ban, [please message the moderators here](http://www.reddit.com/message/compose?to=%2Fr%2F{subreddit})\n\n Do not reply to this message.",
                "already_exists":"Your stream is already in the list of livestreams that this bot checks. If you have just messaged your stream, please wait 5-10 minutes for the sidebar to update.\n\n Problems? Contact the moderators [here](http://www.reddit.com/message/compose?to=%2Fr%2F{subreddit})\n\n Do not reply to this message."
            }
    }


`string_format` is the format that each twitch stream will be displayed as in your sidebar - `{name}` is the users twitch.tv username, `{viewercount}` is the viewer count on twitch.tv & `{title}` is the title they've set on twitch.tv (which can be limited in length with `max_title_length`)

`no_streams_string` is the string that will be displayed if there are no streams live. 

`thumbnail_size` is the width/height of the thumbnails that will be uploaded in a spritesheet to your subreddit. Make sure you have less than 50 images uploaded to your stylesheet, or the bot will not be able to upload the thumbnails.

`stream_marker_start` and `stream_marker_end` are the two markers you must put in your sidebar for the bot to work. They indicate where the livestreams will appear. The bot will not function without them and will log errors to `/wiki/twitchbot_error_log` if it can't find either marker.

`max_streams_displayed` is the limit for the amount of streams that can be displayed in your sidebar at any point.

`messages` are the messages the bot will send if someone PMs it to add a stream - `success` is sent when they send a stream and it is added to `/wiki/streams`, `banned` is if they send a stream that is in `/wiki/banned_streams`, `already_exists` is if they send a stream that already exists in `/wiki/streams`

`wikipages` is the location of the error log, stream list and ban list on your subreddit.

By default, the bot will display any streams that are present in `/wiki/streams` - you can restrict it to display only certain games by adding to the `allowed_games` list. For example:

    "allowed_games":["Bad rats", "Farming simulator 2014", "Goat simulator"]

The games are not case sensitive, but they must match the game being played on twitch.tv to be allowed onto the sidebar - for example, someone playing "Bad rats: Rats revenge" would not be displayed, but "bad rats" would. 


###Running

Run the script with 

    python twitchy.py

It's recommended to run it on a timed basis, every 5-10 minutes.

#Contact 

If you have any issues with this bot, you can message me on reddit at /u/andygmb