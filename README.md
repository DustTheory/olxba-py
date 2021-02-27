# olxba-py
Python API for retrieving information from olx.ba

## Installation

* Install by simply running:

```
pip install git+https://github.com/ishakd00/olxba-py.git@v0.1
```

## Usage

### Authentication

An olx.ba account is needed for this API to work. Authenticate by passing your login info to the OlxScraper constructor like so:

```
from OlxScraper import OlxScraper

parser = OlxScraper('username', 'password')
```
### Documentation

**search**(searchText, sortOrder, sortBy, category, id, condition, page)

Provides limited search functonality. 
##### Parameters:
* `searchText` -  text you would enter into the search bar - string
* `sortOrder` - Sort ascending or descending - string 'asc' or 'desc' (default: 'desc')
* `sortBy` - By what property to sort - string 'price', 'date' or 'relevance'
* `category` - Olx lowest subcategory id, I plan to make a table for this but for now you're on your own exploring on olx.ba - integer
* `id` - Olx (?parent?) category id, still don't understand exactly how this works but it's similar to `category` and you can just leave it unset if you set `category` - integer
* `page` - Search page number - integer

#### Returns:
List of listings.

**getListingById**(listingId)
Returns instance of *OlxListing* for listing with listingId.

##### Parameters:
* `listingId` - olx.ba listing id - integer

#### Returns:
Instance of *OlxListing* 

*class* **OlxListing**
    
##### Properties:

* listingId - integer
* title - string
* dateUpdated - datetime object
* dateUploaded - datetime object
* condition - string - 'new' or 'used'
* hasShipping - boolean
* freeShupping - boolean
* otherProperties - dictionary containing all listing details
    


