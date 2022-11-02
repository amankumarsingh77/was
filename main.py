from typing import Optional
from fastapi import FastAPI
from watchAsian import WatchAsian
from dramafansubs import DFS
from gogoanime import GogoAnime
import os
from urllib.parse import urlparse
app = FastAPI()


async def get_gogoanime(url):
    return await GogoAnime().get_links(url)


async def get_dramacool(url):
    return await WatchAsian().get_links(url)


async def get_gogoanime_episodes(url):
    return await GogoAnime().get_title_season_episodes(url)


async def get_dramacool_episodes(url):
    return await WatchAsian().get_title_season_episodes(url)

_SUPPORTED = ['dramacool', "gogoanime", ]

_FUNCTIONS = {
    "dramacool_links": get_dramacool,
    "gogoanime_links": get_gogoanime,
    "dramacool_episodes": get_dramacool_episodes,
    "gogoanime_episodes": get_gogoanime_episodes,
}


@app.get("/")
async def home(url: Optional[str] = None):
    if url:
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        for dn in _SUPPORTED:
            if dn in netloc:
                title, year, season, episode, watch_links, download_links = await _FUNCTIONS[dn + "_links"](url)
                return {"status": "200", "title": title, "year": year, "season": season, "episode": episode, "sources": watch_links, "download_sources": download_links}
    return {"msg": "hi"}


@app.get("/episodes/")
async def episode(url: Optional[str] = None):
    if url:
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        for dn in _SUPPORTED:
            if dn in netloc:
                title, year, season, episodes = await _FUNCTIONS[dn + "_episodes"](url)
                return {"status": "200", "title": title, "year": year, "season": season, "sources": episodes}
    return {"msg": "hi"}


@app.get("/search/")
async def search(q: Optional[str] = None, year: Optional[str] = None, anime: Optional[bool] = False):
    if q:
        if anime:
            url = await GogoAnime().search(q, year)
        else:
            url = await WatchAsian().search(q, year)
        if url:
            return {"status": "200", "url": url}
    return {"msg": "hi"}


@app.get("/dramafansubs/")
async def get_dramafansubs_sources(keyword: str, season: int, episode: int, year: Optional[str] = None,):
    sources = await DFS().get_sources(keyword=keyword, year=year, season=season, episode=episode)
    return {"status": "200", "sources": sources}
if __name__ == "__main__":
    os.system(
        "gunicorn -k uvicorn.workers.UvicornH11Worker main:app --bind 127.0.0.1:8004  --daemon")
