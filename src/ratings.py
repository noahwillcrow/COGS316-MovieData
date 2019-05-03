import re

from bs4 import BeautifulSoup
import requests

_HEADERS = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
}

class TomatometerScoreFetcher():
    def __init__(self):
        self.name = "Tomatometer"
        self.__movie_name_regex = re.compile('[^a-zA-Z1-9_]')

    def get_score(self, movie_name):
        url_movie_name = self.__movie_name_regex.sub("", movie_name.replace(" ", "_"))
        page_url = f"https://www.rottentomatoes.com/m/{url_movie_name}"
        page_result = requests.get(page_url, headers=_HEADERS)
        if page_result.status_code != 200:
            return -1
        soup = BeautifulSoup(page_result.content, "html.parser")
        content_reviews_anchor = soup.find(href="#contentReviews")
        if content_reviews_anchor is None:
            return -1
        review_score = int(content_reviews_anchor.find(class_="mop-ratings-wrap__percentage").string.strip()[0:-1]) / 100
        return review_score

class RottenTomatoesAudience():
    def __init__(self):
        self.name = "Rotten Tomatoes Audience"
        self.__movie_name_regex = re.compile('[^a-zA-Z1-9_]')

    def get_score(self, movie_name):
        url_movie_name = self.__movie_name_regex.sub("", movie_name.replace(" ", "_"))
        page_url = f"https://www.rottentomatoes.com/m/{url_movie_name}"
        page_result = requests.get(page_url, headers=_HEADERS)
        if page_result.status_code != 200:
            return -1
        soup = BeautifulSoup(page_result.content, "html.parser")
        content_reviews_anchor = soup.find(href="#audience_reviews")
        if content_reviews_anchor is None:
            return -1
        review_score = int(next(content_reviews_anchor.find(class_="mop-ratings-wrap__percentage").strings).strip()[0:-1]) / 100
        return review_score

class MetacriticScoreFetcher():
    def __init__(self):
        self.name = "Metacritic"
        self.__movie_name_regex = re.compile('[^a-zA-Z1-9\-]')

    def get_score(self, movie_name):
        url_movie_name = self.__movie_name_regex.sub("", movie_name.replace(" ", "-")).lower()
        page_url = f"https://www.metacritic.com/movie/{url_movie_name}"
        page_result = requests.get(page_url, headers=_HEADERS)
        if page_result.status_code != 200:
            return -1
        soup = BeautifulSoup(page_result.content, "html.parser")
        score_span = soup.find(class_="metascore_w")
        if score_span is None:
            return -1
        review_score = int(score_span.string.strip()) / 100
        return review_score