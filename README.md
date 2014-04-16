twitchy_the_bot
===============

A reddit bot that gets twitch.tv streams from wiki pages and adds them to the subreddit's sidebar if they are live. 

#Setup

Create two wiki pages on your subreddit, streams and streamconfig. These pages can be changed in config.py if those names are already taken. 

http://www.reddit.com/r/%subreddit%/wiki/edit/streams
/wiki/Streams is where the bot adds new streams that it is messaged, as well as where it pulls stream names from.

http://www.reddit.com/r/%subreddit%/wiki/edit/streamconfig
/wiki/streamconfig is an optional page, if you use it to list meta_games, the bot will only display streams that are currently playing that meta_game on twitch.tv. 


Copy the CSS from css.css to your subreddit's stylesheet to have the thumbnail images display properly. 

Set the bot's username, password & the subreddit in config.py. 

