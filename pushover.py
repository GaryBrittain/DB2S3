import urllib, urllib2, json
import time

def message (message):
  po_url = "https://api.pushover.net/1/messages.json"
  token = ""
  user = ""

  parameters = {
    'token': token,
    'user': user,
    'timestamp' : int(time.time()),
    'priority': '-1',
    'sound': 'mechanical',
    'title': 'DB2S3',
    'message': message
  }

  req = urllib2.Request(po_url, data=urllib.urlencode(parameters))
  stats = urllib2.urlopen(req)
  data = json.load(stats)

  if data['status'] != 1:
    return 0
  else:
    return 1
