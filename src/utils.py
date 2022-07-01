from datetime import datetime


def getNow() -> int:
    now = int(datetime.now().timestamp())
    return now


class Filter:
    def __init__(self, json_data, selector_data):
        self.json_data = json_data
        self.selector_data = selector_data

    def __strToSelector(key: str, multiple_key: bool = False) -> list:
        replaces = {
            "[": "@#@",
            "]": "@#@",
            "@#@@#@": "@#@"
        }

        for k, v in replaces.items():
            key = key.replace(k, v)
        key = list(filter(None, key.split("@#@")))
        if multiple_key == True:
            for i in key:
                if "&" in i:
                    key.remove(i)
                    return i.split("&")
        return key

    def findSelectorInJson(self, arr: dict | list, search: str) -> list | dict | str:
        """
            @examples:
            arr[dict]   -> {"comments":[{"user_id":111111, "text":"comment 1", "date":12.12.12}, {"user_id":111222, "text":"comment 2", "date":11.12.12}]}
            search[str] -> "[comments][x][user_id&text]"
            return[any] -> [{"user_id":111111, "text":"comment 1"}, {"user_id":111222, "text":"comment 2"}]
        """
        # Control
        if isinstance(search, str):
            search = self.__strToSelector(search)

        if len(search) == 0:
            return arr

        if isinstance(arr, list):
            try:
                if isinstance(arr[0], list):
                    new_arr = []
                    for i in arr:
                        new_arr.append(i[0])
                    arr = new_arr
            except:
                arr = arr

        # Search
        for i in search:
            search.remove(i)
            i = int(i) if isinstance(i, str) and i.isnumeric() else i

            if isinstance(i, str) and "&" in i:
                key = self.__strToSelector(i, True)
                if isinstance(arr, list):
                    for i in arr:
                        for k, v in i.copy().items():
                            if k not in key:
                                del i[k]
                elif isinstance(arr, dict):
                    for k, v in arr.copy().items():
                        if k not in key:
                            del arr[k]
                return arr

            elif isinstance(arr, list) and i == "x":
                arr_list = []
                for j in arr:
                    if len(search) > 0:
                        if "&" in search[0]:
                            arr_list.append(
                                self.findSelectorInJson(j, search[0]))
                        else:
                            arr_list.append(j[search[0]])
                    else:
                        arr_list.append(j)
                if len(search) > 0:
                    search.remove(search[0])
                return self.findSelectorInJson(arr_list, search)

            elif isinstance(arr, dict) or isinstance(arr, list) and isinstance(i, int) or isinstance(i, str):
                try:
                    return self.findSelectorInJson(arr[i], search)
                except (KeyError, TypeError):
                    return "None"
