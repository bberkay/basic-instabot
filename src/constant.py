import json
import os

BASE_PATH = os.getcwd()
BASE_URL = "https://www.instagram.com"
API_URL = "https://i.instagram.com/api/v1"

SELECTORS_JSON = json.load(
    open(BASE_PATH + "\\json\\selectors.json", encoding="utf8"))
USER_AGENTS_JSON = json.load(
    open(BASE_PATH + "\\json\\useragents.json", encoding="utf8"))

sub_url = {
    "operation": {
        "login": BASE_URL + "/accounts/login/ajax/",
        "logout": BASE_URL + "/accounts/logout/"
    },
    "data": {
        "followers": BASE_URL + "/accounts/access_tool/accounts_following_you?__a=1",
        "following": BASE_URL + "/accounts/access_tool/accounts_you_follow?__a=1",
        "following_tags": BASE_URL + "/accounts/access_tool/hashtags_you_follow?__a=1"
    }
}
