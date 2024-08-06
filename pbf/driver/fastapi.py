import json
import uvicorn
from fastapi import FastAPI, Header, Request

from ..utils import Utils
from ..utils import scheduler

p = Utils.print()

description = '''
> PigBotFramework is built on FastApi, all APIs are listed below and provide query parameters
'''
tags_metadata = [
    {
        "name": "上报接口",
        "description": "OneBot(v11)标准上报接口",
        "externalDocs": {
            "description": "OneBot Docs",
            "url": "https://onebot.dev/",
        },
    },
    {
        "name": "操作接口",
        "description": "操作接口",
    },
    {
        "name": "其他接口",
        "description": "其他接口",
    },
]
app = FastAPI(
    title="PigBotFramework API",
    description=description,
    openapi_tags=tags_metadata,
    version="5.0.0",
    contact={
        "name": "xzyStudio",
        "url": "https://xzynb.top",
        "email": "gingmzmzx@gmail.com",
    },
)


@app.on_event('shutdown')
def app_on_shutdown():
    try:
        scheduler.shutdown(wait=False)
        p('Scheduler shutdowned.')
    except Exception:
        pass
