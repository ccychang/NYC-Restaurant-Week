import requests
import csv
import time
from bs4 import BeautifulSoup
import random


def get_restaurant_data():
    """
    If we look at the 200 some requests that are shot off when we go to http://www.nycgo.com/restaurant-week/#?view=list,
    and filter by XHR requests, we can see that there is a json file retrieved that contains all of the restaurant
    information, despite the fact that the site appears to fetch information as you scroll down.
    Take the file, and convert it to a list of lists, where each inner list contains all the information
    we want about a given restaurant.
    """
    fieldnames = ['title', 'cuisine', 'city', 'address']
    data = requests.get('http://www.nycgo.com/index.php/restaurantweek/json-venues').json()
    return [[restaurant.get(fieldname) for fieldname in fieldnames] for restaurant in data]


def add_yelp_reviews(restaurant_data):
    """
    Using the restaurant information, grab a rating for each restaurant from Yelp.
    The Yelp API requires me to enter a website in order to use their API.
    Obviously this project does not have one. We'll use BeautifulSoup instead!
    """

    for index, restaurant in enumerate(restaurant_data):
        time.sleep(random.randint(5, 10))
        print(('processing... title: {title} | city: {city}'.format(title=restaurant[0],
                                                                    city=restaurant[2])))
        # Requests will do url encoding for us
        soup = BeautifulSoup(requests.get('http://www.yelp.com/search?find_desc={title}&find_loc={city}&ns=1'
                                     .format(title=restaurant[0],
                                             city=restaurant[2]))
                                     .text)

        # Grab us the first search result. Sure there's room for error, but I can't actually go to all the good
        # restaurants anyway.
        search_result_node = soup.find_all(attrs={"data-key": "1"})

        # Sometimes the Yelp search fails to find anything if their data differs slightly from ours
        # and their search engine is unable to resolve the differences (eg., a slightly different name format)
        if not search_result_node:
            print('Failed to find search result')
            continue

        # So hacky... I'm sure there's way to chain searches somehow, but a ResultSet class won't let me :(
        # This gives us the <i> element that contains our rating. They have a special image for each one.
        rating_node = BeautifulSoup(str(search_result_node)).find_all('i')

        # I imagine this won't happen since every restaurant should have reviews on yelp (maybe???). Be safe.
        if not rating_node:
            continue
        rating_node = rating_node[0]

        # Also hacky, but it works great! The rating is the first part of the title attribute. It can never be more than
        # 3 characters... 1 char for the one's place, the decimal separator, and one char for the tenth's place
        rating = float(rating_node['title'][0:3].strip())

        # This might seem a little tricky... "How does the restaurant_data list change?', one might ask
        # Each restaurant entry in restaurant_data is a reference, and when these references change, so does the data we
        # access through restaurant_list. If you're from c, think pointers.
        restaurant.append(rating)

    return restaurant_data


def write_data_to_csv(restaurant_data):
    """
    Prints our restaurant information to a CSV we can open in Excel.
    """
    with open('data.csv', 'w') as csvfile:
        restaurant_writer = csv.writer(csvfile)
        restaurant_writer.writerow(['title', 'cuisine', 'city', 'address', 'rating'])
        restaurant_writer.writerows(restaurant_data)

if __name__ == '__main__':
    restaurant_data = get_restaurant_data()
    restaurant_data = add_yelp_reviews(restaurant_data)
    write_data_to_csv(restaurant_data)