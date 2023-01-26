#from functools import cache

import requests
from bs4 import BeautifulSoup

film_info_file = r"C:/PF_Files/Projects/Python_Movie/dataset/moviedata_finished.tsv"
user_info_file = r"C:/PF_Files/Projects/Python_Movie/dataset/data_final.csv"


# Film类
class Film:

    # 创建Film对象，包括若干字段
    def __init__(self, titleId, primaryTitle, titleType, startYear, genres, actor, directors, writers, averageRating,
                 numVotes):
        self.titleId = titleId
        self.primaryTitle = primaryTitle
        self.titleType = titleType
        # 讲startYear转换为整数
        try:
            self.startYear = int(startYear)
        except ValueError:
            self.startYear = 0
        # 将genres、actor转换为set
        self.genres = set(genres.split(","))
        self.actor = set(actor.split(","))
        self.directors = directors
        self.writers = writers
        self.averageRating = float(averageRating)
        self.numVotes = numVotes

    def satisfy(self, genres: set, actors: set, age: tuple):
        """
        给定条件，判断当前Film是否满足
        :param genres:
        :param actors:
        :param age:
        :return:
        """
        if not genres:
            genres = self.genres
        if not actors:
            actors = self.actor

        if actors & self.actor and genres & self.genres and (age[0] <= self.startYear <= age[1] or self.startYear == 0):
            return True
        return False

    @staticmethod
    #@cache
    def get_actor_name(nm_id="nm0443482"):
        """
        给定actor id，返回real name
        :param nm_id:
        :return:
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}

        url = f"https://www.imdb.com/name/{nm_id}/"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        name = soup.select_one(".itemprop")
        return name.text

    # 格式化输出
    def __str__(self):
        actor_names = []
        for actor in self.actor:
            actor_names.append(self.get_actor_name(actor))

        return f"{self.titleId} {self.primaryTitle}({self.startYear}) {self.averageRating} {actor_names}"


class User:
    def __init__(self, user_id, film_id: str = None):
        self.userId = user_id
        # film存储当前用户看过的电影
        self.film = {
            film_id: True
        }

    def add_film(self, film_id):
        """
        添加film_id为当前用户看过
        :param film_id:
        :return:
        """
        self.film[film_id] = True

    def have_seen(self, film_id):
        """
        判断电影是否看过
        :param film_id:
        :return:
        """
        return self.film.get(film_id, False)


class Recommendation:
    def __init__(self):
        # 加载电影和用户信息
        self.film_info: list = self.load_film_info()
        self.user_info: dict = self.load_user_info()

    def recommend_with_conditions(self, uid: str, film_genres: set, film_actors: set, film_age: tuple, num: int = 3):
        """
        按条件推荐
        :param uid: 用户
        :param film_genres: genres条件
        :param film_actors:
        :param film_age:
        :param num: 推荐数量
        :return:
        """
        result = []
        for film in self.film_info:
            # 判断当前电影是否满足条件
            if not self.user_info.get(uid, User(uid)).have_seen(film.titleId) \
                    and film.satisfy(film_genres, film_actors, film_age):
                result.append(film)
                if len(result) == num:
                    break
        return result

    def recommend_without_conditions(self, uid: str, num: int = 3):
        """
        无条件推荐
        :param uid:
        :param num:
        :return:
        """
        result = []
        for film in self.film_info:
            if not self.user_info.get(uid, User(uid)).have_seen(film.titleId):
                result.append(film)
                if len(result) == num:
                    break
        return result

    @staticmethod
    def load_film_info():
        film_info = []
        with open(film_info_file, "r", encoding="utf-8") as file:
            file.readline()
            while line := file.readline():
                line = line.strip("\n").split("\t")
                try:
                    film_info.append(Film(*line))
                except ValueError:
                    print(line)
                    print(len(line))
        film_info.sort(key=lambda f: f.averageRating, reverse=True)
        return film_info

    @staticmethod
    def load_user_info():
        user_info = dict()
        with open(user_info_file, "r", encoding="utf-8") as file:
            file.readline()
            while line := file.readline():
                line = line.strip("\n").split(",")
                uid = line[1]
                fid = line[2]
                if user_info.get(uid) is None:
                    user_info[uid] = User(uid, fid)
                else:
                    user_info[uid].add_film(fid)

        return user_info


if __name__ == "__main__":
    recommender = Recommendation()
    res = recommender.recommend_without_conditions("1")
    for i in res:
        print(i)

    res1 = recommender.recommend_with_conditions("8", set(), set(), (1900, 1980), num=10)
    for i in res1:
        print(i)

    user_id = "23"
    film_type = {"Animation", "Comedy"}
    film_actor = {"nm1588970"}
    film_age = (1980, 2000)
    res2 = recommender.recommend_with_conditions(user_id, film_type, film_actor, film_age, num=10)

    for i in res2:
        print(i)

    print(res1 == res2)

    for u, v in recommender.user_info.items():
        v: User
        print(v.userId, v.film.keys())
