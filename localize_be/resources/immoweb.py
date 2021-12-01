"""
Wrapper for Immoweb scraping
"""
import re
import requests
import random
import time
import json

from bs4 import BeautifulSoup
from dagster import resource
from fake_useragent import UserAgent

BASE = "https://www.immoweb.be/fr"
SEARCH = "https://www.immoweb.be/fr/recherche?propertyTypes=HOUSE&minSurface=150&maxSurface=350&minLandSurface=600&maxLandSurface=5000&postalCodes=BE-1315,BE-1357,BE-1360,BE-1367,BE-1370,BE-1457,BE-5030,BE-5031,BE-5080,BE-5310&transactionTypes=FOR_SALE&minPrice=200000&priceType=PRICE&minBedroomCount=3&countries=BE&maxPrice=460000&orderBy=newest"
HOME = "https://www.immoweb.be/fr/annonce/maison/a-vendre/{}/{}/{}"
MAX_SEARCH_PAGES = 1


class ImmowebAPI:
    def __init__(self, get_delay_range=(10, 25)):
        self.get_delay_range = get_delay_range
        self.session = requests.Session()
        ua = UserAgent()
        self.session.headers['User-Agent'] = ua.random

    def search_homes(self):
        for page in range(1, MAX_SEARCH_PAGES + 1):
            url = SEARCH
            if page > 1:
                url += '&page={}'.format(page)
            search = self._download(url)
            # the data is in a JSON
            results = search.find('iw-search').attrs[':results']
            results = json.loads(results)
            for home in results:
                yield {
                    "id": int(home["id"]),
                    "city": home["property"]["location"]["locality"],
                    "postal_code": home["property"]["location"]["postalCode"],
                    "price": home["price"]["mainValue"],
                }

    def get_home(self, id, locality, postal_code):
        # https://www.immoweb.be/fr/annonce/maison/a-louer/mont-st-guibert/1435/8736394?searchId=5ecb8fc950a33
        print('Getting home', id)
        url = HOME.format(
            re.sub('[^a-z]', '-', locality.lower()),
            postal_code,
            id)
        soup = self._download(url)
        data = soup.find('script', string=re.compile("^\\s*window.classified = "))
        if not data:
            raise Exception("Could not find classified in document")
        data = data.contents[0]
        data = re.sub('^\\s*window.classified = ', '', data)
        data = re.sub(';\\s*$', '', data)
        # the data is in a JSON in "classified"
        ad = json.loads(data)
        prop_data = ad['property']
        location = prop_data['location']
        return {
            'Code #': ad['id'],
            'Postal code': prop_data['location']['postalCode'],
            'Price': ad['price']['mainValue'],
            'City': locality,
            'Street': '{} {}'.format(location['street'], location['number']) if location['street'] else '',
            'SqMeter': prop_data['netHabitableSurface'],
            'Land': prop_data['land']['surface'],
            'Lat': location['latitude'],
            'Lng': location['longitude'],
            'Bedrooms': prop_data['bedroomCount'],
            'Attic': 'Yes' if prop_data['hasAttic'] else 'No',
            'Basement': 'Yes' if prop_data['hasBasement'] else 'No',
            'Garage': 'Yes' if prop_data['parkingCountIndoor'] else 'No',
            'Pool': 'Yes' if prop_data['hasSwimmingPool'] else 'No',
            'Office': 'Yes' if ((prop_data.get('specificities') or {}).get('office') or {}).get('surface') else 'No',
            'Energy': (ad['transaction']['certificates'] or {}).get('epcScore'),
            'Image.Url': ad['media']['pictures'][0]['mediumUrl'],
            'Link.Url': url
        }

    def _download(self, url):
        time.sleep(random.randrange(*self.get_delay_range))
        r = self.session.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        return soup


@resource
def immoweb(init_context):
    return ImmowebAPI()
