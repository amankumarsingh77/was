from typing import Optional
from fastapi import FastAPI
from watchAsian import WatchAsian
import os
app = FastAPI()


@app.get("/")
async def home(url:Optional[str]=None):
    if url and "watchasian" in url:
        title,year,season,episode,links = await WatchAsian().get_links(url)
        return {"status":"200","title":title,"year":year,"season":season,"episode":episode,"sources":links}
    return {"msg":"hi"}
@app.get("/episodes/")
async def episode(url:Optional[str]=None):
    if url and "watchasian" in url:
        title,year,season,episodes = await WatchAsian().get_title_season_episodes(url)
        return {"status":"200","title":title,"year":year,"season":season,"sources":episodes}
    return {"msg":"hi"}
@app.get("/search/")
async def search(q:Optional[str]=None,year:Optional[str]=None):
    if q:
        url = await WatchAsian().search(q,year)
        if url:
            return {"status":"200","url":url}
    return {"msg":"hi"}
if __name__ == "__main__":
    os.system("uvicorn main:app --host 127.0.0.1 --port 8004")