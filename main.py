from typing import Optional
from fastapi import FastAPI
from watchAsian import WatchAsian
app = FastAPI()


@app.get("/")
async def home(url:Optional[str]=None):
    if url and "watchasian" in url:
        title,season,episode,links = await WatchAsian().get_links(url)
        return {"status":"200","sources":links}
    return {"msg":"hi"}
@app.get("/episodes")
async def home(url:Optional[str]=None):
    if url and "watchasian" in url:
        title,season,episodes = await WatchAsian().get_title_season_episodes(url)
        return {"status":"200","sources":episodes}
    return {"msg":"hi"}
