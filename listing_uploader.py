'''
Created on Jan 24, 2018

@author: Victor Fateh
'''

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
import gdata.sites.client
import gdata.sites.data
import google_sheet

SCOPE = 'https://sites.google.com/feeds/'

# client_secrets.json is downloaded from the API console:
# https://code.google.com/apis/console/#project:<PROJECT_ID>:access
# where <PROJECT_ID> is the ID of your project

flow = flow_from_clientsecrets('client_secret.json',
                               scope=SCOPE,
                               redirect_uri='http://localhost')

storage = Storage('plus.dat')
credentials = storage.get()

if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage)

# 'Monkey Patch' the data in the credentials into a gdata OAuth2Token
# This is based on information in this blog post:
# https://groups.google.com/forum/m/#!msg/google-apps-developer-blog/1pGRCivuSUI/3EAIioKp0-wJ

auth2token = gdata.gauth.OAuth2Token(client_id=credentials.client_id,
  client_secret=credentials.client_secret,
  scope=SCOPE,
  access_token=credentials.access_token,
  refresh_token=credentials.refresh_token,
  user_agent='sites-test/1.0')


# Create a gdata client
client = gdata.sites.client.SitesClient(site='webapptestscraper', auth_token=auth2token)

# Authorize it
auth2token.authorize(client)

def upload(url, title, price, body, imgList):
    try:
        # Call an API e.g. to get the site content feed
        uri = '%s?path=%s' % (client.MakeContentFeedUri(), '/today-s-listings')

        feed = client.GetContentFeed(uri=uri)

        customBody ="<p>" + body + "</p><br>"

        for img in imgList:
            customBody += '<img style="display:block;margin-right:auto;margin-left:auto;text-align:center" src="' + img + '"><br>'

        customTitle = title + " - " + price

        entry = client.CreatePage('webpage', customTitle,
                                  html=customBody,
                                  parent=feed.entry[0])

        print('Created. View it at: %s' % entry.GetAlternateLink().href)
    except Exception:
        print(Exception)
