import re

from bs4 import BeautifulSoup
import requests

class TomatometerScoreFetcher():
    def __init__(self):
        self.name = "Tomatometer"
        self.__movie_name_regex = re.compile('[^a-zA-Z1-9_]')

    def get_score(self, movie_name):
        url_movie_name = self.__movie_name_regex.sub("", movie_name.replace(" ", "_"))
        page_url = f"https://www.rottentomatoes.com/m/{url_movie_name}"
        page_result = requests.get(page_url)
        if page_result.status_code != 200:
            return -1
        soup = BeautifulSoup(page_result.content, "html.parser")
        content_reviews_anchor = soup.find(href="#contentReviews")
        if content_reviews_anchor is None:
            return -1
        review_score = int(content_reviews_anchor.find(class_="mop-ratings-wrap__percentage").string.strip()[0:-1]) / 100
        return review_score

class MetacriticScoreFetcher():
    def __init__(self):
        self.name = "Metacritic"
        self.__movie_name_regex = re.compile('[^a-zA-Z1-9\-]')

    def get_score(self, movie_name):
        url_movie_name = self.__movie_name_regex.sub("", movie_name.replace(" ", "-"))
        page_url = f"https://www.metacritic.com/movie/m/{url_movie_name}"
        page_result = requests.get(page_url)
        if page_result.status_code != 200:
            return -1
        soup = BeautifulSoup(page_result.content, "html.parser")
        score_span = soup.find(class_="metascore_w larger movie positive")
        if score_span is None:
            return -1
        review_score = int(score_span.string.strip()) / 100
        return review_score