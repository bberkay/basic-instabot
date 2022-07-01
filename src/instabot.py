import requests
import json
import random
import copy


import utils
import constant


class Instabot:
    def __init__(self, username, password):
        self.user_agent = self.createUserAgent()
        self.session = requests.Session()
        self.sub_json = {}
        self.headers = None
        self.cookies = None
        self.username = username
        self.password = password

    ####################### BOT #######################
    def login(self) -> bool:
        payload = {
            'username': self.username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{self.getNow()}:{self.password}'
        }

        self.headers = {
            "user-agent": self.user_agent,
            "X-Requested-With": "XMLHttpRequest",
            "referer": constant.BASE_URL
        }

        r = self.session.get(constant.BASE_URL, headers=self.headers)
        self.headers.update({"X-CSRFToken": r.cookies["csrftoken"]})

        login = self.session.post(
            constant.sub_url["operation"]["login"], data=payload, headers=self.headers)
        self.cookies = login.cookies
        json_data = json.loads(login.text)

        if json_data["status"] == "fail":
            raise Exception("ERROR -----> [Failed to login]")
        elif json_data["status"] == "ok" and login.status_code == 200:
            try:
                if isinstance(json_data["errors"], dict):
                    raise Exception(
                        "ERROR -----> [Please try again after 5 - 10 minutes]")
            except:
                return True
        elif json_data["message"] == "checkpoint_required":
            raise Exception(
                "ERROR -----> [Failed to login please active 2FA(two-factor authentication) your account]")

    def logout(self) -> bool:
        logout_post = {"csrfmiddlewaretoken": self.cookies["csrftoken"]}
        logout = self.session.post(
            constant.sub_url["operation"]["logout"], data=logout_post)

        if logout.status_code == 200:
            return True
        else:
            raise Exception("ERROR -----> [Failed to logout]")

    def getProfile(self) -> dict:

        # Get Data
        url = constant.API_URL + "/users/web_profile_info/?username=" + self.username
        try:
            user_json = self.session.get(url, data={"username": self.username}, headers=self.headers, cookies={
                                         "csrftoken": self.cookies["csrftoken"]})
            self.sub_json["user"] = user_json.json()["data"]["user"]
        except:
            raise Exception(
                "ERROR -----> [Profile data could not be accessed]")

        # Filter Data
        user_data = {}
        user_data.update({"instagram_id": self.sub_json["user"]["id"]})
        user_data.update({"username": self.username})
        user_data.update({"password": self.password})

        try:
            for k, v in constant.SELECTORS_JSON["user_data"].items():
                res = utils.findSelectorInJson(
                    copy.deepcopy(self.sub_json["user"]), v)
                user_data.update({k: res})
        except:
            raise Exception(
                "ERROR -----> [Profile data could not be filtered]")

        return user_data

    def getFollows(self) -> dict:
        # Get Data
        follows_list = {
            "followers": [],
            "following": [],
            "following_tags": []
        }

        try:
            for k, v in self.sub_url["data"].items():
                follows_list[k] = json.loads(self.session.get(v, headers=self.headers, data={
                                             "__a": "1"}, cookies=self.cookies).text)
        except:
            raise Exception(
                "ERROR -----> [Follows data could not be accessed]")

        # Filter Data
        try:
            for i in follows_list:
                v = utils.findSelectorInJson(copy.deepcopy(
                    follows_list[i]), constant.SELECTORS_JSON["user_follows"]["user"])
                follows_list[i] = v
        except:
            raise Exception(
                "ERROR -----> [Follows data could not be filtered]")

        return follows_list

    def getPosts(self, ig_id: str, limit: int) -> list:
        # Get Data
        try:
            url = constant.BASE_URL + \
                '/graphql/query/?query_hash=003056d32c2554def87228bc3fd9668a&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A{}%7D'.format(
                    ig_id, limit)
            user_posts = json.loads(self.session.get(url, headers=self.headers).text)[
                "data"]["user"]["edge_owner_to_timeline_media"]["edges"]

            posts_json = []
            for i in user_posts:
                url = constant.BASE_URL + \
                    "/p/{}".format(i["node"]["shortcode"])
                self.session.get(url, headers=self.headers, cookies={
                                 "csrftoken": self.cookies["csrftoken"]})
                url = constant.API_URL + \
                    "/media/{}/info/".format(i["node"]["id"])
                post_json = self.session.get(url, headers=self.headers, cookies={
                                             "csrftoken": self.cookies["csrftoken"]})
                posts_json.append(json.loads(post_json.content))
        except:
            raise Exception("ERROR -----> [Post data could not be accesssed]")

        # Filter Data
        try:
            user_posts = []
            post = {}
            for i in posts_json:
                for k, v in constant.SELECTORS_JSON["user_posts"].items():
                    res = utils.findSelectorInJson(
                        copy.deepcopy(i), "[items][0]" + v)
                    post.update({k: res})
                user_posts.append(post.copy())
        except:
            raise Exception("ERROR -----> [Post data could not be filtered]")

        return user_posts

    def getStories(self, ig_id: str) -> list:
        # Get Data
        try:
            url = self.API_URL + "/feed/user/{}/story/".format(ig_id)
            response = self.session.get(
                url, headers=self.headers, cookies=self.cookies)
            stories = json.loads(response.text)
        except:
            raise Exception("ERROR -----> [Story data could not be accesssed]")

        # Filter Data
        try:
            user_stories = []
            story = {}
            for i in stories:
                for k, v in constant.SELECTORS_JSON["user_stories"].items():
                    res = utils.findSelectorInJson(
                        copy.deepcopy(i), "[reel]" + v)
                    story.update({k: res})
                user_stories.append(story.copy())
        except:
            raise Exception("ERROR -----> [Story data could not be filtered]")

        return user_stories

    def getMedia(self, ig_id: str, limit: int) -> dict:
        media = {}
        media.update({"posts": self.getPosts(ig_id, limit)})
        media.update({"stories": self.getStories(ig_id)})
        return media


    ####################### RUN #######################
    def run(self) -> dict:
        analysis = {}
        analysis.update(self.getProfile())
        analysis.update(self.getFollows())
        analysis.update(self.getMedia(
            analysis["instagram_id"], analysis["post_count"]))
        return analysis


    ####################### UTILS ######################
    def createUserAgent(self) -> str:
        random_ua = random.randint(
            0, len(constant.USER_AGENTS_JSON["instagram-ua"])-1)
        user_agent = constant.USER_AGENTS_JSON["instagram-ua"][str(random_ua)]
        return user_agent
