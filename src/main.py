import csv
import math

from bs4 import BeautifulSoup
import ratings
import requests

_MOVIES_WEBSITE_URL_BASE = "https://www.the-numbers.com"
_MOVIES_LIST_URL_PATH = "/movie/budgets/all"

_NUM_MOVIES_PER_PAGE = 100

def get_cash_value(cash_string):
    return int(cash_string[1:].replace(",", ""))

def get_movies_list_page_content(page_number):
    page_url = f"{_MOVIES_WEBSITE_URL_BASE}{_MOVIES_LIST_URL_PATH}"
    if page_number > 0:
        page_url = f"{_MOVIES_WEBSITE_URL_BASE}{_MOVIES_LIST_URL_PATH}/{(page_number*_NUM_MOVIES_PER_PAGE) + 1}"
    page_result = requests.get(page_url)
    if page_result.status_code != 200:
        raise Exception(f"Failed to load page at {page_url}")
    return page_result.content

def get_movie(date_url):
    if date_url not in date_revenue_lists_cache:
        page_result = requests.get(date_url)
        if page_result.status_code != 200:
            raise Exception(f"Failed to load page at {date_url}")
        soup = BeautifulSoup(page_result.content, "html.parser")
        date_revenue_lists_cache[date_url] = soup.find_all("tr")[2:]
    return date_revenue_lists_cache[date_url]

def get_movie_release_day_revenue(movie_url, movie_name):
    page_result = requests.get(movie_url)
    if page_result.status_code != 200:
        raise Exception(f"Failed to load page at {movie_url}")
    soup = BeautifulSoup(page_result.content, "html.parser")
    table_rows = soup.find_all(id="box_office_chart")[1].find_all("tr")
    cells = table_rows[1].find_all("td")
    return get_cash_value(cells[2].string.strip())

def get_movies_list(num_pages, ratingsFetchers):
    movies = [None for i in range(num_pages * _NUM_MOVIES_PER_PAGE)]
    movie_index = 0

    for page_number in range(num_pages):
        movies_list_page_content = get_movies_list_page_content(page_number)
        soup = BeautifulSoup(movies_list_page_content, "html.parser")
        table_rows = soup.find_all("tr")[1:]
        for table_row in table_rows:
            cells = table_row.find_all("td")
            movie_url = _MOVIES_WEBSITE_URL_BASE + cells[2].a["href"]
            if movie_url.find("#") > -1:
                movie_url = movie_url[0:movie_url.find("#")]
            movie_url += "#tab=box-office"
            movie_name = cells[2].string.strip()
            production_budget = get_cash_value(cells[3].string.strip())
            release_day_revenue = get_movie_release_day_revenue(movie_url, movie_name)

            movie_info = [movie_name, production_budget, release_day_revenue]
            for ratingsFetcher in ratingsFetchers:
                movie_info.append(ratingsFetcher.get_score(movie_name))
            movies[movie_index] = movie_info
            movie_index += 1

    return movies

def run():
    ratingsFetchers = [
        ratings.TomatometerScoreFetcher()
        ratings.MetacriticScoreFetcher()
    ]
    headings = ["Movie Name", "Production budget", "Release day revenue"]
    for ratingsFetcher in ratingsFetchers:
        headings.append(ratingsFetcher.name)

    movies_list = get_movies_list(5, ratingsFetchers)
    with open('movies_list.csv', mode='w') as csv_file:
        file_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(headings)
        file_writer.writerows(movies_list)


if __name__ == "__main__":
    run()