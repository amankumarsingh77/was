import aiohttp
import asyncio
import re
import json
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup
def get_ua():
    
    software_names = [SoftwareName.CHROME.value,SoftwareName.FIREFOX.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value,OperatingSystem.ANDROID.value]   
    
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    # Get Random User Agent String.
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent
class WatchAsian:
    async def request(self,url,headers:dict={},data:dict={},get="text",method="get"):
        headers["User-Agent"]=get_ua()
        headers["Accept"]="text/html" if get=="text" else "application/json"
        async with aiohttp.ClientSession(headers=headers) as session:
            if method=="get":
                async with session.get(url) as resp:
                    if resp.status == 200:
                        if get=="text":
                            return await resp.text()
                        else:
                            try:
                                data= await resp.json()
                            except Exception as e:
                                data = json.loads(await resp.text())
                            finally:
                                return data
            elif method =="post":
                async with session.post(url,data=data) as resp:
                    if resp.status == 200:
                        if get=="text":
                            return await resp.text()
                        else:
                            try:
                                data= await resp.json()
                            except Exception as e:
                                data = json.loads(await resp.text())
                            finally:
                                return data
    def parse(self,content):
        soup = BeautifulSoup(content,"html.parser")
        return soup
    def get_title(self,soup):
        h1 = soup.find("h1").text.strip()
        splitted = re.split("[\(\)]",h1)
        year = 0
        for i in splitted:
            if len(i)==4 and i.isnumeric():
                year = i
        title_season = splitted[0].strip().split("Season")
        if len(title_season)==2:
            title,season= title_season
        else:
            title=title_season[0]
            season="1"
        episode = splitted[-1]
        episode = episode.split("Episode")[-1].split("|")[0].strip()
        title = title.split("Episode")[0]
        meta = soup.find("div",{"class":"info"})
        if meta:
            for anchor in meta.find_all("a"):
                if anchor.get("href").startswith("/released-in"):
                    year = anchor.text
                    break
        return (title.strip(),year,season.strip(),episode)
    async def get_title_season_episodes(self,url):
        content = await self.request(url,get="text")
        soup = self.parse(content)
        title,year,season_number,episode_number=self.get_title(soup)
        episodes = []
        all_episodes = soup.find("ul",{"class":"all-episode"})
        if all_episodes:
            episodes_block = all_episodes.find_all("li")
            for episode_block in episodes_block:
                episode_type = episode_block.find("span",{"class":"type"}).get("class")[-1]
                if episode_type.lower() == "sub":  
                    episode = episode_block.find("h3",{"class":"title"})
                    mo = re.search(r"/[\-\.\w\d]*",episode.get("onclick"))
                    if mo:
                        episode = f"https://www.dramacool1.io{mo.group()}"
                        episodes.append(episode)
        if episodes:
            episodes.reverse()
        return (title,year,season_number,episodes)
    async def get_links(self,url):
        content = await self.request(url,headers={
            "Cookie":"dramacools=2a387tjjtruegril8m2a2paq84; auth=yPVfno%2Bjob2kzKTFvqpgl5DbjxGXVcWrdEnGZoFjfikKe6PVmHBU4%2BjvKvbxjL8Si6OMtTse5We14CXwhZA9ZQ%3D%3D",
        },get="text")
        soup = self.parse(content)
        title,year,season,episode=self.get_title(soup)
        watch_links = [link.get("data-video") if link.get("data-video").startswith("http") else f"https:{link.get('data-video')}" for link in soup.find("div",{"class":"anime_muti_link"}).find("ul").find_all("li")]
        download_links = [link.get("href") for div in soup.find_all("div",{"class":"cf-download"}) for link in div.find_all("a")]
        return (title,year,season,episode,watch_links,download_links)
    async def search(self,title,year=None):
        data = await self.request(f"https://www.dramacool1.io/search?type=series&keyword={title}",headers={"X-Requested-With":"XMLHttpRequest",},get="json")
        if data:
            if year:
                for result in data:
                    release_date = result["status"].split(":")[-1].strip()
                    if release_date.isnumeric() and year.isnumeric():
                        if int(release_date)==int(year):
                            return f"https://www.dramacool1.io{result['url']}"
            return f"https://www.dramacool1.io{data[0]['url']}"
if __name__ == '__main__':
    print(asyncio.run(WatchAsian().search("cute programmer")))