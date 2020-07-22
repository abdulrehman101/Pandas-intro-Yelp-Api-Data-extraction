import io, time, json
import requests
from bs4 import BeautifulSoup

def retrieve_html(url):
    """
    Return the raw HTML at the specified URL.

    Args:
        url (string): 

    Returns:
        status_code (integer):
        raw_html (string): the raw HTML content of the response, properly encoded according to the HTTP headers.
    """
    req = requests.get(url)
    return((req.status_code, req.text))

def location_search_params(api_key, location, **kwargs):
    """
    Construct url, headers and url_params. Reference API docs (link above) to use the arguments
    """
    # What is the url endpoint for search?
    url = 'https://api.yelp.com/v3/businesses/search'
    # How is Authentication performed?
    Bearer='Bearer '+api_key
    headers = {'Authorization' : Bearer}
    # SPACES in url is problematic. How should you handle location containing spaces?
    location = location.replace(" ","+")
    url_params = {'location':location}
    # Include keyword arguments in url_params
    for key,value in kwargs.items():
        url_params[key] = value 
    
    return url, headers, url_params


def paginated_restaurant_search_requests(api_key, location, total):
    """
    Returns a list of tuples (url, headers, url_params) for paginated search of all restaurants
    Args:
        api_key (string): Your Yelp API Key for Authentication
        location (string): Business Location
        total (int): Total number of items to be fetched
    Returns:
        results (list): list of tuple (url, headers, url_params)
    """
    # HINT: Use total, offset and limit for pagination
    # You can reuse function location_search_params(...)
    tuple_list = []
    retrieved = 0
    while retrieved < total:
        url,header,param = location_search_params(api_key, location, limit=20, categories = "restaurants", offset=retrieved)
        tuple_list.append((url,header,param))
        retrieved += 20
    return tuple_list  
    
def parse_api_response(data):
    """
    Parse Yelp API results to extract restaurant URLs.
    
    Args:
        data (string): String of properly formatted JSON.

    Returns:
        (list): list of URLs as strings from the input JSON.
    """
    data = json.loads(data)
    all_business = list(data["businesses"])
    return list(map(lambda x:x['url'],all_business))

def parse_page(html):
    """
    Parse the reviews on a single page of a restaurant.
    
    Args:
        html (string): String of HTML corresponding to a Yelp restaurant

    Returns:
        tuple(list, string): a tuple of two elements
            first element: list of dictionaries corresponding to the extracted review information
            second element: URL for the next page of reviews (or None if it is the last page)
    """
    soup = BeautifulSoup(html,'html.parser')
    url_next = soup.find('link',rel='next')
    if url_next:
        url_next = url_next.get('href')
    else:
        url_next = None

    reviews = soup.find_all('div', itemprop="review")
    reviews_list = []
    # HINT: print reviews to see what http tag to extract
    reviews_list = []
    reviews_dict = {}
    # HINT: print reviews to see what http tag to extract
    for r in reviews:
        reviews_dict['author'] = r.find('meta', itemprop = "author")['content']
        reviews_dict['rating'] = float(r.find('meta', itemprop = "ratingValue")['content'])
        reviews_dict['date'] = r.find('meta', itemprop = "datePublished")['content']
        reviews_dict['description'] = r.find('p', itemprop = "description").text
        reviews_list.append(reviews_dict)
        reviews_dict = {}
    return reviews_list, url_next

def extract_reviews(url, html_fetcher):
    """
    Retrieve ALL of the reviews for a single restaurant on Yelp.

    Parameters:
        url (string): Yelp URL corresponding to the restaurant of interest.
        html_fetcher (function): A function that takes url and returns html status code and content
        

    Returns:
        reviews (list): list of dictionaries containing extracted review information
    """
    dict_return = []
    #code, html = html_fethcher(url_next)
    page = html_fetcher(url)[1]
    reviews_list, url_next = parse_page(page)
    for x in reviews_list:
        dict_return.append(x)
    while url_next != None:
        page = html_fetcher(url_next)[1]
        reviews_list, url_next = parse_page(page)
        for x in reviews_list:
            dict_return.append(x)
    return dict_return


    #[YOUR CODE HERE]
    #code, html = html_fetcher(url) # function implemented in Q0 should work
    #[YOUR CODE HERE]
