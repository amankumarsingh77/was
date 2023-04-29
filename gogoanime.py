from watchAsian import WatchAsian
import asyncio
from urllib.parse import urlparse
import re


class GogoAnime(WatchAsian):
    _HOST = "https://gogoanime.cl"

    async def get_links(self, url):
        content = await self.request(url, headers={
            "Cookie": "gogoanime=2alh847a1luvi0v4dang397uq3;auth=j307tFbn1PHY6qpe2qLhYBqSIa2Y3hnDb4EBIrw/1NpM0TXAoYuoYKZHCfhpZ7TcmaCEMDfdxBb1gp+YOPmbQw=="
        })
        soup = self.parse(content)
        title, year, season, episode = self.get_title(soup)
        watch_links = []
        for li in soup.find("div", {"class": "anime_muti_link"}).find("ul").find_all("li"):
            data_provider = "".join(li.get("class", "vidcdn")).lower()
            data_video = li.find("a").get("data-video")
            watch_link = data_video if data_video.startswith(
                "http") else "https:"+data_video
            watch_link = self._replace_host(data_provider, watch_link)
            watch_links.append(watch_link)
        download_links = [
            link.get("href") for div in soup.find_all("div", {"class": "cf-download"}) for link in div.find_all("a")
        ]
        return (title, year, season, episode, watch_links, download_links)

    async def get_title_season_episodes(self, url):
        content = await self.request(url, get="text")
        soup = self.parse(content)
        title, year, season_number, episode_number = self.get_title(soup)
        anime_info = soup.find("div", {"class": "anime-info"})
        if anime_info:
            url = f"https://{urlparse(url).netloc}{anime_info.find('a').get('href')}"
            content = await self.request(url, get="text")
            soup = self.parse(content)
        year = soup.find("div",
                         {
                             "class": "anime_info_body_bg"
                         }
                         ).find_all("p")[-3].text.split(": ")[-1]
        movie_id = soup.find("input", {"id": "movie_id"}).get("value")
        episode_content = await self.request(f"https://ajax.gogo-load.com/ajax/load-list-episode?ep_start=0&ep_end=99999&id={movie_id}")
        episode_soup = self.parse(episode_content)
        episodes = []
        for episode in episode_soup.find_all("a"):
            episodes.append("{host}{path}".format(
                host=self._HOST, path=episode.get('href').strip()))
        episodes.reverse()
        return (title, year, season_number, episodes)

    async def search(self, keyword, year=None):
        content = await self.request("{host}/search.html?keyword={keyword}".format(host=self._HOST, keyword=keyword))
        soup = self.parse(content)
        animes = soup.find("ul", {"class": "items"}) or []
        for anime in animes.find_all("li"):
            if year is None:
                break
            released = re.search(r"[\d]{4}", anime.find(
                "p", {"class": 'released'}).text)
            if int(released.group()) == int(year):
                break
        try:
            "Unbound Local Error Occur When there's no anime"
            return "{host}{path}".format(host=self._HOST, path=anime.find("a").get("href").strip())
        except UnboundLocalError:
            return


if __name__ == "__main__":
    gogo = GogoAnime()
    print(asyncio.run(gogo.get_title_season_episodes(
        "https://gogoanime.dk/millenniums-of-warring-states-episode-14")))
