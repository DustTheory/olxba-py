from pyquery import PyQuery as pq
import requests
import urllib
import datetime

class OlxListing:
    def __init__(self, listingDetails):
        self.listingId = int(listingDetails['OLX ID'])

        if('Cijena' in listingDetails):
            self.price = parseOlxPrice(listingDetails['Cijena'])
        elif ('Cijena - Hitna prodaja [?]' in listingDetails):
            self.price = parseOlxPrice(listingDetails['Cijena - Hitna prodaja [?]'])
        
        self.title = listingDetails['Naslov']
        self.dateUpdated = parseOlxDate(listingDetails['Obnovljen'])
        self.dateUploaded = parseOlxDate(listingDetails['Datum objave'])
        self.condition = {'korišteno': "used", "novo": "new"}[listingDetails['Stanje'].lower()]
        self.hasShipping = bool(listingDetails['OLX brza dostava'])
        self.freeShipping = bool(listingDetails['Besplatna dostava'])

        self.otherProperties = {**listingDetails}

class OlxScraper:
    def __init__(self, username, password):
        self.session = requests.session()
        self.authenticate(username, password)

    def authenticate(self, username, password):
        login_data = {
            'username': username, 
            'password': password,
            'zapamtime': 'on',
            'csrf_token': 'xgXEOeWD99wHds09RC2qXUpqLeyU4puVSbQ1kSz5'
        }
        self.session.post('https://www.olx.ba/auth/login', data=login_data)

    def getListingById(self, listingId):
        listingPage = self.getListingPageById(listingId)
        return self.extractListingDataFromPage(listingPage)

    def getListingPageById(self, listingId):
        html = self.session.get('https://www.olx.ba/artikal/41965423/'+str(listingId))
        return pq(html.content)

    def extractListingDataFromPage(self, listingPage):
        listingDetails = dict()

        listingDetails['Objavio'] = listingPage('.username').text()
        listingDetails['OLX Radnja'] = listingPage('.povjerenje_medalje').hasClass('radnja')
        listingDetails['Naslov'] = listingPage('h3').text().strip()

        for listingProperty in listingPage('.op').items():
            if(len(listingProperty.children()) == 1):
                listingProperty = listingProperty('a')
            propertyName = listingProperty('p:nth-child(1)').text().strip()
            propertyValue = listingProperty('p:nth-child(2)').text().strip()
            if(propertyName == 'Obnovljen'):
                propertyValue = listingProperty.attr('data-content')
            listingDetails[propertyName] = propertyValue

        for listingProperty in listingPage('.df').items():
            propertyName = listingProperty('.df1').text().strip()

            if(propertyName == 'Obnovljen'):
                continue
            propertyValue = listingProperty('.df2').text().strip()
            listingDetails[propertyName] = propertyValue  
            if(listingDetails[propertyName] == ''):
                listingDetails[propertyName] = True
            
        for propertyGroupTitle in listingPage('.brpr').items():
            propertyName = propertyGroupTitle.clone().children().remove().end().text().strip()

            if(propertyName in ['Stanje artikla', 'Zamjena']):
                listingDetails[propertyName] = propertyGroupTitle.next().text()
            elif(propertyName == 'OLX brza dostava'):
                listingDetails[propertyName] = True

        listingDetails['Besplatna dostava'] = 'besplatna' in listingPage('.dostava-box .dostava-info div').text()
        return OlxListing(listingDetails)
    
    def extractSearchDataFromPage(self, searchPage):
        searchData = []
        for listing in searchPage("#rezultatipretrage").children().items():
            if(not listing.attr('id')): # filter out ads
                continue
            if(not listing.attr('id').startswith('art_')): # filter out ads
                continue

            searchData.append({
                "listingId": listing.attr('id')[4:],
                "price": parseOlxPrice(listing('.cijena .datum span').text().strip()),
                "dateUpdated": parseOlxDate(listing('.cijena .datum .kada').attr('data-cijelidatum')),
                "condition": {"NOVO": "new", "KORIŠTENO": "used"}[listing('.cijena .stanje').text()],
                "title": listing(".na").text(),
                "description": listing(".pna").text(),
                "storeSeller": bool(listing(".pikradnja")),
                "hasShipping": bool(listing(".fa-truck")),
                "freeShipping": bool(listing(".pretraga-besplatnadostava")),
                "urgent": bool(listing('.hitno'))
            })
        return searchData
            

    def search(self, searchText="", sortOrder="", sortBy="", category="", id="", condition=0, page=None):
        params = {
            "vrstapregleda": "tabela",
            "trazilica": searchText,
            "sort_order": sortOrder,
            "sort_po": {"date": "datum", "price": "cijena", "relevance": None}[sortBy],
            "id": id,
            "kategorija": category,
            "stanje": {"new": 1, "used": 2}[condition] if condition else condition,
            "stranica": page
        }
        baseUrl = 'https://www.olx.ba/pretraga?'
        url = baseUrl + urllib.parse.urlencode(params)
        searchPage = pq(self.session.get(url).content)
        return self.extractSearchDataFromPage(searchPage)

def parseOlxDate(olxDate):
    date, time = olxDate.split('u')
    day, month, year = [int(value) for value in date.split('.')[:3]]
    hour, minute = [int(value) for value in time.split(':')]
    return datetime.datetime(year, month, day, hour, minute)

def parseOlxPrice(olxPrice=""):
    if(olxPrice.count('KM') != 1):
        return "Po dogovoru"
    return float(olxPrice.split('KM')[0].replace('.', '').replace(',', '.'))