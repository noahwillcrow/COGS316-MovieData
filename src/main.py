import csv
from datetime import datetime
import math
import sys
import uuid

from bs4 import BeautifulSoup
import ratings
import requests

_MOVIES_WEBSITE_URL_BASE = "https://www.the-numbers.com"
_MOVIES_LIST_URL_PATH = "/movie/budgets/all"
_MOVIE_RELEASE_DATE_FORMAT = "%b %d, %Y"

_NUM_MOVIES_PER_PAGE = 100

_COLUMNS = [
    {
        'name': "Name",
        'key': "name"
    },
    {
        'name': "Source type",
        'key': "source"
    },
    {
        'name': "Genre",
        'key': "genre"
    },
    {
        'name': "Production method",
        'key': "production_method"
    },
    {
        'name': "Is part of a franchise?",
        'key': "is_franchise"
    },
    {
        'name': "Production budget (in USD)",
        'key': "production_budget"
    },
    {
        'name': "Month",
        'key': "month"
    },
    {
        'name': "Year",
        'key': "year"
    },
    {
        'name': "Release day revenue",
        'key': "release_day_revenue"
    },
    {
        'name': "Number of theaters on release day",
        'key': "num_theaters"
    },
]

def get_number_value(number_string):
    return int(number_string.replace(",", ""))

def get_cash_value(cash_string):
    return get_number_value(cash_string[1:])

def get_date(date_string):
    return datetime.strptime(date_string, _MOVIE_RELEASE_DATE_FORMAT)

def load_soup(url):
    page_result = requests.get(url)
    if page_result.status_code != 200:
        raise Exception(f"Failed to load page at {url}")
    return BeautifulSoup(page_result.content, "html.parser")

def get_movies_list_soup(page_number):
    page_url = f"{_MOVIES_WEBSITE_URL_BASE}{_MOVIES_LIST_URL_PATH}"
    if page_number > 0:
        page_url = f"{_MOVIES_WEBSITE_URL_BASE}{_MOVIES_LIST_URL_PATH}/{(page_number*_NUM_MOVIES_PER_PAGE) + 1}"
    return load_soup(page_url)

def populate_movie_details_info(tab_url, movie_info):
    try:
        soup = load_soup(tab_url)

        movie_info["is_franchise"] = soup.find("a", href=lambda s: s is not None and s.find("/franchise/") > -1) is not None
        movie_info["source"] = soup.find("a", href=lambda s: s is not None and s.find("/source/") > -1).string.strip()
        movie_info["genre"] = soup.find("a", href=lambda s: s is not None and s.find("/genre/") > -1).string.strip()
        movie_info["production_method"] = soup.find("a", href=lambda s: s is not None and s.find("/production-method/") > -1).string.strip()
    except Exception as ex:
        print(f"Exception occurred: {ex}")

def populate_movie_release_day_info(tab_url, movie_info):
    try:
        soup = load_soup(tab_url)

        box_office_charts = soup.find_all(id="box_office_chart")
        if box_office_charts is None or len(box_office_charts) < 2:
            return

        table_rows = box_office_charts[1].find_all("tr")
        cells = table_rows[1].find_all("td")
        release_date = get_date(cells[0].string.strip())
        movie_info['month'] = release_date.month
        movie_info['year'] = release_date.year
        movie_info['release_day_revenue'] = get_cash_value(cells[2].string.strip())
        movie_info['num_theaters'] = get_number_value(cells[4].string.strip())
    except Exception as ex:
        print(f"Exception occurred: {ex}")

def write_page_of_movies_to_csv(page_number, ratingsFetchers, csv_writer):
    soup = get_movies_list_soup(page_number)
    table_rows = soup.find_all("tr")[1:]
    for table_row in table_rows:
        try:
            cells = table_row.find_all("td")
            movie_name = cells[2].string.strip()
            movie_url = _MOVIES_WEBSITE_URL_BASE + cells[2].a["href"]
            if movie_url.find("#") > -1:
                movie_url = movie_url[0:movie_url.find("#")]

            print(f"Processing movie: {movie_name}")

            movie_info = {}
            movie_info['name'] = movie_name
            movie_info['production_budget'] = get_cash_value(cells[3].string.strip())
            populate_movie_details_info(movie_url + "#tab=summary", movie_info)
            populate_movie_release_day_info(movie_url + "#tab=box-office", movie_info)

            row_data = [-1 if not col['key'] in movie_info else movie_info[col['key']] for col in _COLUMNS]

            for ratingsFetcher in ratingsFetchers:
                rating = ratingsFetcher.get_score(movie_name)
                row_data.append(rating)

            csv_writer.writerow(row_data)
        except Exception as ex:
            print(f"Exception occurred: {ex}")

def run(args):
    start_page = 0
    num_pages = 1
    file_name = f"movies_list_{str(uuid.uuid4())}.csv"
    file_mode = "w"
    should_add_header = True
    if len(args) >= 2:
        num_pages = int(args[1])
    if len(args) >= 3:
        start_page = int(args[2])
    if len(args) >= 4:
        file_name = args[3]
        file_mode = "a+"
        should_add_header = False

    ratingsFetchers = [
        ratings.TomatometerScoreFetcher(),
        ratings.MetacriticScoreFetcher()
    ]

    with open(file_name, mode=file_mode, newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        if should_add_header:
            print("Writing headings row")
            headings = [col['name'] for col in _COLUMNS]
            for ratingsFetcher in ratingsFetchers:
                headings.append(ratingsFetcher.name)
            csv_writer.writerow(headings)

        for page_number in range(start_page, num_pages):
            print(f"Starting on page {page_number + 1} / {num_pages}")
            write_page_of_movies_to_csv(page_number, ratingsFetchers, csv_writer)

    print("Complete")

if __name__ == "__main__":
    run(sys.argv)