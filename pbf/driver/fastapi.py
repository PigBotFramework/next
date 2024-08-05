import json
import time
import traceback
from typing import Union
import requests
import uvicorn
import yaml
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


@app.post("/event", tags=['上报接口'])
async def post_data(request: Request, X_Signature: Union[str, None] = Header(default=None)):
    """
    描述：**机器人事件POST上报接口**
    身份验证：可通过`GET`参数`pswd`验证，或**通过header中的`X_Signature`验证身份**（OneBot标准）
    上报数据：在Request请求体中以json格式
    """
    try:
        # sha1校验防伪上报
        params = request.query_params
        botPswd = utils.getPswd(params.get("uuid"))
        if botPswd == params.get("pswd"):
            sig = botPswd
            received_sig = botPswd
        else:
            sig = utils.encryption(await request.body(), botPswd)
            received_sig = X_Signature[len('sha1='):] if X_Signature else False
        if sig == received_sig:
            se = await request.json()
            p(f'Recv: {se.get("sender", {}).get("nickname")}({se.get("user_id")}): {se.get("raw_message")}')
            # botIns.CrashReport(se, params.get("uuid"))
            Handler.requestInit(se, params.get("uuid"))
        else:
            return {"code": 403}
    except Exception as e:
        p(f'Crashed: {e}\n{traceback.format_exc()}')


@app.get("/get", tags=['上报接口'])
async def get_data(uuid: str, pswd: str, params: str):
    """
    描述：**机器人事件GET上报接口**
    身份验证：需提供`UUID`和`pswd`，**不可通过`X_Signature`验证身份**（不是OneBot规定的上报接口，可用于其他情况的上报）
    上报数据：**`params`参数为`json_encode()`且`urlencode()`后的上报数据**
    """
    if utils.getPswd(uuid) == pswd:
        Handler.requestInit(json.loads(params), uuid)
        return json.loads(params)
    else:
        return {"code": 403}


@app.post("/testSpeed", tags=['其他接口'])
@app.get("/testSpeed", tags=['其他接口'])
@limiter.limit("12/minute")
async def webtestSpeed(request: Request, X_Forwarded_For: Union[str, None] = Header(default=None)):
    """
    描述：测试指令执行速度和延迟
    频率限制：**12次/分钟**
    测试方法：模拟执行`菜单`指令
    """
    timeStart = time.time()
    message = "菜单 noreply"
    Handler.requestInit({'post_type': 'message', 'message_type': 'group', 'self_id': 3558267090, 'sub_type': 'normal',
                         'group_id': 763432519, 'message': message,
                         'sender': {'age': 0, 'area': '', 'card': '', 'level': '', 'nickname': '', 'role': 'owner',
                                    'sex': 'unknown', 'title': '', 'user_id': 66600000}, 'user_id': 66600000, 'font': 0,
                         'raw_message': message}, "123456789")
    timeEnd = time.time()
    report = {"code": 200, "startTime": timeStart, "endTime": timeEnd, "cost": timeEnd - timeStart}
    return report


@app.post("/status", tags=['其他接口'])
@app.get("/status", tags=['其他接口'])
async def webstatus():
    """
    描述：获取处理器状态
    返回值：`{"code":200}`
    """
    return json.dumps({"code": 200}, ensure_ascii=False)


@app.get("/overview", tags=['GOCQ接口'])
@app.post("/overview", tags=['GOCQ接口'])
async def weboverview(uuid: str):
    """
    描述：获取机器人GOCQ数据概览
    参数：`UUID` 机器人实例uuid
    返回值：data[] 具体内容可以请求后查看
    """
    try:
        botSettings = BotSettingsModel(uuid=uuid)

        # 尝试请求gocq获取gocq信息
        try:
            gocq = Handler.CallApi("get_version_info", {}, ob=botSettings, timeout=5).get("data")
            if gocq.get('app_name') != "go-cqhttp":
                return {'code': 502}
        except Exception as e:
            print(e)
            return {'code': 502}

        data = {'code': 200, 'go-cqhttp': gocq, 'time': time.time()}
        # 获取各项数据
        # 1. 群聊列表
        groupList = Handler.CallApi('get_group_list', {}, ob=botSettings).get('data')
        data['groupCount'] = len(groupList)
        # 2. 好友列表
        friendList = Handler.CallApi('get_friend_list', {}, ob=botSettings).get('data')
        data['friendCount'] = len(friendList)
        # 3. 网络信息
        network = Handler.CallApi('get_status', {}, ob=botSettings).get('data')
        data['network'] = network.get('stat')

        return data
    except Exception:
        return traceback.format_exc()


@app.get("/getFriendAndGroupList", tags=['GOCQ接口'])
async def webgetFriendAndGroupList(pswd: str, uuid: str):
    """
    描述：获取机器人好友和群聊列表
    参数：`pswd:str` 密钥    `uuid:str` 实例uuid
    返回值：`{"friendList":..., "groupList":...}`
    """
    try:
        if pswd == utils.getPswd(uuid):
            groupList = Handler.CallApi('get_group_list', {}, uuid).get('data')
            friendList = Handler.CallApi('get_friend_list', {}, uuid).get('data')
            return {'friendList': friendList, 'groupList': groupList}
        else:
            return 'Password error.'
    except Exception:
        return traceback.format_exc()


@app.get("/getFriendList", tags=['GOCQ接口'])
async def webgetFriendList(pswd: str, uuid: str):
    """获取机器人好友列表"""
    if pswd == utils.getPswd(uuid):
        return Handler.CallApi('get_friend_list', {}, uuid).get('data')
    else:
        return 'Password error.'


@app.get("/kickUser", tags=['GOCQ接口'])
async def webkickUser(pswd: str, uuid: str, gid: int, uid: int):
    """踢出某人"""
    if pswd == utils.getPswd(uuid):
        data = Handler.CallApi('set_group_kick', {'group_id': gid, 'user_id': uid}, uuid)
        return 'OK.' if data['status'] == 'ok' else 'failed.'
    else:
        return 'Password error.'


@app.get("/banUser", tags=['GOCQ接口'])
async def webBanUser(pswd: str, uuid: str, uid: int, gid: int, duration: int):
    """禁言某人"""
    if pswd == utils.getPswd(uuid):
        Handler.CallApi('set_group_ban', {'group_id': gid, 'user_id': uid, 'duration': duration}, uuid)
        return 'OK.'
    else:
        return 'Password error.'


@app.get("/delete_msg", tags=['GOCQ接口'])
async def webDeleteMsg(pswd: str, uuid: str, message_id: str):
    """撤回消息"""
    if pswd == utils.getPswd(uuid):
        Handler.CallApi('delete_msg', {'message_id': message_id}, uuid)
        return 'OK.'
    else:
        return 'Password error.'


@app.get("/getMessage", tags=['GOCQ接口'])
async def webGetMessage(uuid: str, message_id: int):
    """获取消息"""
    try:
        return Handler.CallApi('get_msg', {'message_id': message_id}, uuid)
    except Exception:
        return traceback.format_exc()


@app.get("/getForwardMessage", tags=['GOCQ接口'])
async def webGetForwardMessage(uuid: str, message_id: str):
    """获取合并转发消息"""
    try:
        return Handler.CallApi('get_forward_msg', {'message_id': message_id}, uuid)
    except Exception:
        return traceback.format_exc()


@app.get("/getGroupHistory", tags=['GOCQ接口'])
async def webGetGroupHistory(uuid: str, group_id: int, message_seq: int = 0):
    """获取群聊聊天记录"""
    try:
        return Handler.CallApi('get_group_msg_history', {'group_id': group_id},
                               uuid) if message_seq == 0 else Handler.CallApi('get_group_msg_history',
                                                                              {'group_id': group_id,
                                                                               "message_seq": message_seq}, uuid)
    except Exception:
        return traceback.format_exc()


@app.get("/sendMessage", tags=['GOCQ接口'])
@app.post("/sendMessage", tags=['GOCQ接口'])
async def webSendMessage(pswd: str, uuid: str, uid: int, gid: int, message: str):
    """发送消息"""
    if pswd == utils.getPswd(uuid):
        Handler.send(uuid, uid, message, gid)
        return 'OK.'
    else:
        return 'Password error.'


@app.get("/callApi", tags=['GOCQ接口'])
@app.post("/callApi", tags=['GOCQ接口'])
async def webCallApi(uuid: str, name: str, pswd: str, params={}):
    """发送消息"""
    return Handler.CallApi(name, json.loads(params), uuid) if pswd == utils.getPswd(uuid) else 'Password error.'


@app.get("/getGroupList", tags=['GOCQ接口'])
async def getGroupList(uuid: str):
    """获取某机器人群聊列表"""
    return Handler.CallApi('get_group_list', {}, uuid)


@app.get("/getGroupDe", tags=['GOCQ接口'])
@limiter.limit("1/minute")
async def webgetGroupDe(uuid: str, request: Request):
    """
    获取某机器人群聊列表加最新一条消息
    频率限制6次每分钟
    """
    try:
        dataList = Handler.CallApi('get_group_list', {}, uuid)['data']
        for i in dataList:
            messages = Handler.CallApi('get_group_msg_history', {'group_id': i.get("group_id")}, uuid).get("data").get(
                "messages")
            message = messages[-1].get("message")
            i['message'] = message
        return dataList
    except Exception as e:
        return e


@app.get("/MCServer", tags=['其他接口'])
async def MCServer(msg: str, uuid: str, qn: int):
    """MC服务器消息同步"""
    if msg != '' and '[Server] <' not in msg:
        Handler.send(uuid, None, str(msg), qn)

    return '200 OK.'


@app.get('/getPluginsData', tags=['其他接口'])
async def webgetPluginsData():
    """刷新插件数据"""
    return Cache.get('pluginsData', [])


@app.get('/getPluginByName', tags=['其他接口'])
async def webgetPluginByName(name: str):
    """刷新插件数据"""
    cpl = Cache.get('commandPluginsList', {}).get(name)
    pmbn = Cache.get('pluginsMappedByName', {}).get(name)
    return {'pluginData': pmbn, 'cmds': cpl}


@app.get('/getGroupMemberList', tags=['GOCQ接口'])
async def webGetGroupMemberList(uuid: str, gid: int):
    """获取群聊成员列表"""
    return Handler.CallApi('get_group_member_list', {'group_id': gid}, uuid)


@app.get('/getGOCQConfig', tags=['其他接口', 'GOCQ接口'])
async def webgetGOCQConfig(uin: int, host: str, port: int, uuid: str, secret: str, password: str = "null",
                           url: str = "https://pbfpost.xzynb.top/?uuid={0}"):
    '''生成GOCQ配置'''
    try:
        gocqConfig = json.loads(
            '{"account": {"uin": 123, "password": null, "encrypt": false, "status": 0, "relogin": {"delay": 3, "interval": 3, "max-times": 0}, "use-sso-address": true, "allow-temp-session": false}, "heartbeat": {"interval": -1}, "message": {"post-format": "string", "ignore-invalid-cqcode": false, "force-fragment": false, "fix-url": false, "proxy-rewrite": "", "report-self-message": false, "remove-reply-at": false, "extra-reply-data": false, "skip-mime-scan": false}, "output": {"log-level": "trace", "log-aging": 1, "log-force-new": true, "log-colorful": false, "debug": false}, "default-middlewares": {"access-token": "", "filter": "", "rate-limit": {"enabled": false, "frequency": 1, "bucket": 1}}, "database": {"leveldb": {"enable": true}, "cache": {"image": "data/image.db", "video": "data/video.db"}}, "servers": [{"http": {"host": "1.1.1.1", "port": 2222, "timeout": 10, "long-polling": {"enabled": false, "max-queue-size": 2000}, "middlewares": {"access-token": "", "filter": "", "rate-limit": {"enabled": false, "frequency": 1, "bucket": 1}}, "post": [{"url": "http://127.0.0.1:8000/", "secret": "123456", "max-retries": 0, "retries-interval": 0}]}}]}')
        gocqConfig['account']['password'] = password
        gocqConfig['account']['uin'] = uin
        gocqConfig['servers'][0]['http']['host'] = host
        gocqConfig['servers'][0]['http']['port'] = port
        gocqConfig['servers'][0]['http']['post'][0]['url'] = url.format(uuid)
        gocqConfig['servers'][0]['http']['post'][0]['secret'] = secret
        gocqConfig['default-middlewares']['access-token'] = secret
        gocqConfig['servers'][0]['http']['middlewares']['access-token'] = secret
        filename = 'config-{0}.yml'.format(uuid)
        file = open("./resources/createimg/{0}".format(filename), 'w+', encoding='utf-8')
        yaml.dump(gocqConfig, file)
        file.close()
        return json.dumps(filename, ensure_ascii=False)
    except Exception as e:
        return e


@app.get("/reloadPlugins", tags=['其他接口'])
async def webreloadPlugins():
    '''刷新插件及指令列表'''
    return Handler.reloadPlugins()


def serve(port: int):
    p('Loading plugins...')
    Handler.reloadPlugins(True)
    p('Plugins loaded.')

    uts.scheduler.start()
    p('Scheduler started.')

    p(f'Running on {port}')
    uvicorn.run(app="pbf.driver.Fastapi:app", host='0.0.0.0', port=int(port), reload=True)


Handler.reloadPlugins()