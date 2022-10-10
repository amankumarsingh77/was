from typing import Optional
from fastapi import FastAPI
from watchAsian import WatchAsian
from gogoanime import GogoAnime
import os
from urllib.parse import urlparse
app = FastAPI()


@app.get("/")
async def home(url:Optional[str]=None):
    if url:
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        if "dramacool" in netloc or "gogoanime" in netloc:
            title,year,season,episode,watch_links,download_links = await WatchAsian().get_links(url) if "dramacool" in netloc else await GogoAnime().get_links(url)
            return {"status":"200","title":title,"year":year,"season":season,"episode":episode,"sources":watch_links,"download_sources":download_links}
    return {"msg":"hi"}

    
@app.get("/episodes/")
async def episode(url:Optional[str]=None):
    if url:
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        if "dramacool" in netloc or "gogoanime" in netloc:
            title,year,season,episodes = await WatchAsian().get_title_season_episodes(url) if "dramacool" in netloc else await GogoAnime().get_title_season_episodes(url)
            return {"status":"200","title":title,"year":year,"season":season,"sources":episodes}
    return {"msg":"hi"}
@app.get("/search/")
async def search(q:Optional[str]=None,year:Optional[str]=None,anime:Optional[bool]=False):
    if q:
        if anime:
            url = await GogoAnime().search(q,year)
        else:
            url = await WatchAsian().search(q,year)
        if url:
            return {"status":"200","url":url}
    return {"msg":"hi"}
if __name__ == "__main__":
    os.system("gunicorn -k uvicorn.workers.UvicornH11Worker main:app --bind 127.0.0.1:8004  --daemon")