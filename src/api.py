import instabot


class Instabot:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __runAnalysis(self) -> dict:
        opt_result = None
        try:
            opt_result = instabot.run(self.username, self.password)
        except Exception as e:
            opt_result = "ERROR!: {}".format(e)
        return opt_result

    def getAnalysis(self) -> dict:
        return self.__runAnalysis
