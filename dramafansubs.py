from watchAsian import WatchAsian
import asyncio
from urllib.parse import urlparse,unquote,parse_qs
import re
"""
    Currently, Supports Single Season Only
"""


class DFS(WatchAsian):
    _HOST = "https://dramafansubs.net"

    async def search(self, keyword, year=None):
        resp = await self.request("{host}/wp-json/dooplay/search/?keyword={keyword}&nonce=0a06ecafad".format(host=self._HOST, keyword=keyword), get='json')
        if not resp.get("error"):
            dramas = list(resp.values())
            dramas.sort(key=lambda a: int(a["extra"]["date"]), reverse=True)
            if not year:
                return dramas[0]["url"]
            try:
                return filter(lambda a: int(a['extra']['date']) == int(year), dramas).__next__()["url"]
            except StopIteration:
                return

    def get_title(self, soup):
        try:
            title, season_episode = soup.find(
                "h1", {"class": "epih1"}
            ).text.split(":")
            season, episode = season_episode.strip().split("x")
            year = soup.find("span", {"class": "date"}).text.split(", ")[-1]
        except AttributeError:
            data = soup.find("div", {"class": "data"})
            title = data.find("h1").text
            year = data.find("span", {"class": "date"}).text.split(", ")[-1]
            episode = None
            season = 1
        return (title, year, season, episode)

    async def get_title_season_episodes(self, url):
        content = await self.request(url, get="text")
        soup = self.parse(content)
        (title, year, season, episode) = self.get_title(soup)
        episodes = []
        for episode in soup.find("ul", {"class": "episodios"}).find_all("li"):
            episodes.append(episode.find("a").get("href"))
        return (title, year, season, episodes)
    async def get_links(self,url):
        content = await self.request(url, get="text")
        soup = self.parse(content)
        (title,year,season,episode) = self.get_title(soup)
        watch_links = []
        download_links = []
        for link in soup.find_all("iframe",{"class":"metaframe rptss"}):
            link = unquote(link.get("src"))
            parsedURL = urlparse(link)
            if  parsedURL.netloc == urlparse(self._HOST).netloc:
                link = parse_qs(parsedURL.query)["source"][0]
                download_links.append(link)
            watch_links.append(link)
        return (title, year, season, episode, watch_links, download_links)

if __name__ == '__main__':
    df = DFS()
    print(asyncio.run(df.get_links("https://dramafansubs.net/episodio/curtain-call-episodio-1/")))
