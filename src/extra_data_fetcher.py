import pandas as pd

from ratings import RottenTomatoesAudience

ratings_fetcher = RottenTomatoesAudience()

data = pd.read_csv("../full_movie_list.csv")

_NAME = "Name"
_SOURCE_TYPE = "Source type"
_GENRE = "Genre"
_PROD_METHOD = "Production method"
_IS_FRANCHISE = "Is part of a franchise?"
_PROD_BUDGET = "Production budget (in USD)"
_MONTH = "Month"
_YEAR = "Year"
_REL_DAY_REVENUE = "Release day revenue"
_REL_DAY_NUM_THEATERS = "Number of theaters on release day"
_REL_DAY_REVENUE_RATIO = "Release day revenue / production budget"
_TOMATOMETER = "Tomatometer"
_ROT_TOM_AUDIENCE = "Rotten Tomatoes Audience"
_METACRITIC = "Metacritic"

data[_REL_DAY_REVENUE_RATIO] = data[_REL_DAY_REVENUE] / data[_PROD_BUDGET]

rot_tom_audience_values = []
for row in data.iterrows():
    if row[1][_TOMATOMETER] > -1:
        rot_tom_audience_values.append(ratings_fetcher.get_score(row[1][_NAME]))
    else:
        rot_tom_audience_values.append(-1)
    print(len(rot_tom_audience_values))

data[_ROT_TOM_AUDIENCE] = pd.Series(rot_tom_audience_values)

data.to_csv("../full_movie_list_2.csv", index=False)