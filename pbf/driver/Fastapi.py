import json
from typing import Union
import traceback
import uvicorn
import hmac
from fastapi import FastAPI, Header, Request

from ..utils import scheduler
from .. import logger, pluginsManager
from ..controller.Handler import Handler
from ..config import ob_access_token
from ..controller.Data import Event
from ..controller.Client import Client

fastapi_host = "localhost"
fastapi_port = 8000
fastapi_debug = True

description = '''
> PigBotFramework is built on FastApi, all APIs are listed below and provide query parameters
'''
tags_metadata = [
    {
        "name": "上报接口",
        "description": "OneBot(v11/v12)标准上报接口",
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
    """
    关闭时执行的逻辑
    :return: None
    """
    try:
        scheduler.shutdown(wait=False)
        logger.info('Scheduler shutdowned.')
    except Exception:
        pass


async def check_signature(request: Request, access_token: str, X_Signature: Union[str, None],
                    Authorization: Union[str, None]):
    """
    校验签名
    :param request: Request
    :param access_token: access_token
    :param X_Signature: X-Signature in header
    :param Authorization: Authorization in header
    :return: bool
    """
    # sha1校验防伪上报
    if X_Signature is not None:
        sig = hmac.new(ob_access_token.encode('utf-8'), await request.body(), 'sha1').hexdigest()
        received_sig = X_Signature[len('sha1='):]
        if sig == received_sig:
            return True

    # Authorization校验
    if Authorization == f'Bearer {ob_access_token}':
        return True

    # access_token校验
    if access_token == ob_access_token:
        return True

    return False


@app.post("/", tags=['上报接口'])
async def report(request: Request, access_token: str = None, X_Signature: Union[str, None] = Header(default=None),
           Authorization: Union[str, None] = Header(default=None)):
    """
    上报接口
    :param request: Request 上报数据
    :param access_token: str (可选)access_token
    :param X_Signature: str in header (可选)X-Signature
    :param Authorization: str in header (可选)Authorization
    :return: dict {"status": "ok"/"error", "message": str}
    """
    try:
        if not await check_signature(request, access_token, X_Signature, Authorization):
            return {'status': 'error', 'message': 'Unauthorized'}

        data = await request.json()
        logger.info(f"Received data: {data}")
        Handler(json.dumps(data)).handle()
        return {'status': 'ok'}
    except Exception as e:
        logger.error(f'Crashed: {e}\n{traceback.format_exc()}')
        return {'status': 'error', 'message': f'Internal Server Error: {e}'}


@app.post("/call_api", tags=['操作接口'])
async def call_api(request: Request, access_token: str = None, X_Signature: Union[str, None] = Header(default=None),
                   Authorization: Union[str, None] = Header(default=None)):
    """
    调用OneBot实现的API
    :param request: Request 请求数据
    :param access_token: str (可选)access_token
    :param X_Signature: str in header (可选)X-Signature
    :param Authorization: str in header (可选)Authorization
    :return: dict 请求结果
    """
    if not await check_signature(request, access_token, X_Signature, Authorization):
        return {'status': 'error', 'message': 'Unauthorized'}

    data = await request.json()
    event: Event = Handler(json.dumps(data)).classify()
    client = Client(event)
    return client.request(data.get("action"), data.get("data"), data.get("echo"))


@app.get("/status", tags=['其他接口'])
async def ping():
    """
    Ping!
    :return: dict {"status": "ok"}
    """
    return {'status': 'ok'}


@app.get("/plugins/get_all", tags=['其他接口'])
async def get_all_plugins():
    """
    获取所有插件
    :return: list 插件列表
    """
    return pluginsManager.getAllPlugins()


@app.get("/plugins/enable", tags=['其他接口'])
async def enable_plugin(plugin: str):
    """
    启用插件
    :param plugin: str 插件名
    :return: dict {"status": "ok"}
    """
    pluginsManager.enable(plugin)
    return {'status': 'ok'}


@app.get("/plugins/disable", tags=['其他接口'])
async def disable_plugin(plugin: str):
    """
    禁用插件
    :param plugin: str 插件名
    :return: dict {"status": "ok"}
    """
    pluginsManager.disable(plugin)
    return {'status': 'ok'}


@app.get("/plugins/load_all", tags=['其他接口'])
async def load_all_plugins():
    """
    装载所有插件
    :return: dict {"status": "ok"}
    """
    pluginsManager.loadPlugins()
    return {'status': 'ok'}


def start():
    """
    启动FastAPI服务
    :return: None
    """
    uvicorn.run(app="pbf.driver.Fastapi:app", host=fastapi_host, port=fastapi_port, reload=fastapi_debug)
