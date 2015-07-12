import praw, webbrowser

r = praw.Reddit('Temporary reddit app to obtain authentication information')

url = r.get_authorize_url(state='obtainingAuthentication', scope='modconfig modwiki wikiread', refreshable=True)
webbrowser.open(url)
reddit_code = raw_input('Please enter the code from the redirect url: ')

access_information = r.get_access_information(reddit_code)

print 'Refresh token: ' + str(access_information.get('refresh_token'))
