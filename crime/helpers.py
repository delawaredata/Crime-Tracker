import urllib
import urllib2
import simplejson
from django.utils.encoding import smart_str


def get_lat_lng(location):
    location = urllib.quote_plus(smart_str(location))
    url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false' % location
    response = urllib2.urlopen(url).read()
    result = simplejson.loads(response)
    if result['status'] == 'OK':
        lat = str(result['results'][0]['geometry']['location']['lat'])
        lng = str(result['results'][0]['geometry']['location']['lng'])
        formatted_address = str(result['results'][0]['formatted_address'])
        return lat, lng, formatted_address[:-5]
    else:
        return ''
