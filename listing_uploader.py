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

global GLOBAL_DUP

SCOPE = 'https://sites.google.com/feeds/'

flow = flow_from_clientsecrets('client_secret.json',
                               scope=SCOPE)

storage = Storage('plus.dat')
credentials = storage.get()

if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage)

auth2token = gdata.gauth.OAuth2Token(client_id=credentials.client_id,
  client_secret=credentials.client_secret,
  scope=SCOPE,
  access_token=credentials.access_token,
  refresh_token=credentials.refresh_token,
  user_agent='sites-test/1.0')


# Create a gdata client
client = gdata.sites.client.SitesClient(site='cars', domain='inspect-x.com')

# Authorize it
auth2token.authorize(client)


def upload(url, title, price, body, imgList):
        try:
            # Call an API e.g. to get the site content feed
            uri = '%s?path=%s' % (client.MakeContentFeedUri(), '/today-s-listings')

            feed = client.GetContentFeed(uri=uri)

            customBody = "<p>" + body + "</p><br>"

            for img in imgList:
                customBody += '<img style="display:block;margin-right:auto;margin-left:auto;text-align:center" src="' + img + '"><br>'

            customTitle = title + " - " + price

            entry = client.CreatePage('webpage', customTitle,
                                      html=customBody,
                                      parent=feed.entry[0])

            google_sheet.update_post(url, entry.GetAlternateLink().href)

            print('Created. View it at: %s' % entry.GetAlternateLink().href)

        except Exception:
            pass
            print("Error posting, please check google sheet for duplicates: " + url)
