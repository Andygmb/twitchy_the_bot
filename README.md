twitchy_the_bot
===============

A reddit bot that gets twitch.tv streams from wiki pages and adds them to the subreddit's sidebar if they are live. 

#Setup

Create two wiki pages on your subreddit, streams and streamconfig. These pages can be changed in config.py if those names are already taken. 

* http://www.reddit.com/r/subreddit/wiki/edit/streams
* http://www.reddit.com/r/subreddit/wiki/edit/streamconfig

/wiki/streams is where the bot adds new streams that it is messaged, as well as where it pulls stream names from. 

Example:

    TwitchTVUsername
    Another_Username
    Username

/wiki/streamconfig is an optional page, if you use it to list meta_games, the bot will only display streams that are currently playing that meta_game on twitch.tv.

Example:

    Call Of duty: Black ops
    Train simulator 2014
    Team Fortress 2

Copy the CSS from css.css to your subreddit's stylesheet to have the thumbnail images display properly. This can be editted as needed for your own subreddit's stylesheet. 

Set the bot's username, password & the subreddit in config.py. 

In your sidebar, add these two markers where you want the stream to display:

    [](#TwitchStartMarker)
    
    [](#TwitchEndMarker)

The streams will not display if you do not put these markers in place (as the script doesn't know where to put them.)

If you want people to be able to message the bot with streams, you need to provide this as a message template somewhere in your sidebar:

    http://www.reddit.com/message/compose?to=BOT_USERNAME&subject=Twitch.tv+request+%2Fr%2FSUBREDDITNAME&message=http%3A%2F%2Fwww.twitch.tv%2FUSERNAMEHERE

Add your bot's username and subreddit in the url. 

#Running 

The script only runs once, then exits. You need to run it on a cron job/schedule however often you want it to run. The recommended time is every 10 minutes. 

#Contact 

If you have any issues with this bot, you can message me on reddit at /u/andygmb