import asyncio
import aiohttp
from urllib.parse import urlparse, unquote, parse_qs
import json
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup
"""
    Currently, Supports Single Season Only
"""


def get_ua():

    software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
    operating_systems = [OperatingSystem.WINDOWS.value,
                         OperatingSystem.LINUX.value, OperatingSystem.ANDROID.value]

    user_agent_rotator = UserAgent(
        software_names=software_names, operating_systems=operating_systems, limit=100)

    # Get Random User Agent String.
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


class DFS:
    _HOST = "https://apk.dfbplay.com/api"
    _SEARCH = _HOST + "/search/{keyword}/4F5A9C3D9A86FA54EACEDDD635185/977c71e0-c95e-4396-a93f-123cb08bdbce/"
    _SERIE = _HOST + "/season/by/serie/{id}/4F5A9C3D9A86FA54EACEDDD635185/977c71e0-c95e-4396-a93f-123cb08bdbce/"
    _PROXY = "http://smykbabu-rotate:kiy81fvox1h3@p.webshare.io:80"
    async def request(self, url, headers: dict = {}, data: dict = {}, get="text", method="get"):
        headers["User-Agent"] = get_ua()
        headers["Accept"] = "text/html" if get == "text" else "application/json"
        async with aiohttp.ClientSession(headers=headers) as session:
            if method == "get":
                async with session.get(url,proxy=self._PROXY) as resp:
                    if resp.status == 200:
                        if get == "text":
                            return await resp.text()
                        else:
                            try:
                                data = await resp.json()
                            except Exception as e:
                                data = json.loads(await resp.text())
                            finally:
                                return data
    async def search(self, keyword, year=None):
        resp = await self.request(self._SEARCH.format(keyword=keyword), get='json')
        dramas = resp["posters"]
        if not dramas:
            return 
        if year:
            try:
                return self._SERIE.format(id=filter(lambda a:a["year"] == int(year),dramas).__next__()["id"])
            except StopIteration:
                pass
        dramas.sort(key=lambda a:a["year"],reverse=True)
        return self._SERIE.format(id=dramas[0]["id"])

    async def get_sources(self,*, keyword, season, episode, year = None,):
        watch_links = []
        try:
            serie = await self.search(keyword, year )
            if serie:
                data = await self.request(serie, get="json")
                season = filter(lambda a: int(a["title"].lower().split()[-1].strip()) == int(season),data).__next__()
                episodes = season["episodes"]
                if len(episodes) == episode:
                    episode = episodes[-1]
                else:
                    episode = filter(lambda a: int(a["title"].lower().split()[-1].strip()) == int(episode), episodes).__next__()
                for source in episode["sources"]:
                    if source["type"].lower() == "mp4":
                        watch_links.append(source["url"])
        except StopIteration or KeyError:
            pass
        return watch_links

if __name__ == '__main__':
    df = DFS()
    print(asyncio.run(df.get_sources(keyword="love in contract",season=1,episode=1)))
