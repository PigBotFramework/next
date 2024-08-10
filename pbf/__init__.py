"""
# PigBotFramework文档
这是 PigBotFramework（后简称PBF） Next 的文档。 <br>
由此文档，您可以查阅到PBF Next的接口定义。 <br>
接下来的内容将带您运行PBF服务器以及创建一个简单插件。



## 运行PBF服务器
### Step 1: 前置准备
- 安装Python3.8及以上版本
- 通过pip安装`PigBotFramework`模块
    ```shell
    pip install PigBotFramework
    ```
- 创建一个新的目录`/app`，用于存放PBF的配置文件和插件

### Step 2: 创建主文件
在`/app`目录下创建一个`main.py`文件，并写入以下内容
```python
# Step 1: import config and modify it
from pbf import config

config.logs_level = "DEBUG"
# modify more config here

# Step 2: import setup and setup PBF
from pbf import setup
setup.setup()

# Step 3: import driver and start it
if __name__ == "__main__":
    from pbf.driver import Fastapi

    Fastapi.start()
```
接下来，我将为您逐行解释这段代码
- Step 1: 导入PBF的配置模块，并修改配置
    - `from pbf import config`：导入PBF的配置模块
    - `config.logs_level = "DEBUG"`：将日志等级设置为`DEBUG`
    - 您还可以在这部分设置更多的配置，详见[具体配置](/pbf/docs/config.html)
- Step 2: 初始化PBF
    - `from pbf import setup`：导入PBF的初始化模块
    - `setup.setup()`：初始化PBF
- Step 3: 导入驱动并启动
    - `from pbf.driver import Fastapi`：导入Fastapi驱动
    - `Fastapi.start()`：启动Fastapi驱动

**注意：在导入pbf.setup以及.driver.*之前，您必须先导入pbf.config并修改配置，否则之后修改的配置将会无法生效**

### Step 3: 运行主文件
运行刚刚编辑的`main.py`文件，服务器就会启动
- 默认的Fastapi驱动会监听在`http://localhost:8000`上
- PBF默认会从`~/.pbf/plugins`目录下加载插件
- 日志文件默认会输出到`~/.pbf/logs`目录下



## 创建一个简单插件
### Step 1: 创建插件
1. 在`/app`目录下创建一个`plugins`目录，用于存放插件
2. 在`~/.pbf/plugins`目录下创建一个`foo.py`文件，这就是我们要完成的新插件

### Step 2: 创建元数据
我们需要创建一个`meta_data`变量，来声明插件的元数据
```python
from pbf.utils import MetaData
# 插件元数据
meta_data = MetaData(
    name="test",
    version="0.1.0",
    versionCode=10,
    description="PBF Plugin",
    author="xzystudio",
    license="MIT",
    keywords=["pbf", "plugin"],
    readme=\"\"\"
    # PBF Plugin
    hi
    \"\"\"
)
```
MetaData的参数如下：
- `name` (str)：插件名称
- `version` (str)：插件版本
- `versionCode` (int)：插件版本号
- `description` (str)：插件描述
- `author` (str)：插件作者
- `license` (str)：插件许可证
- `keywords` (List[str])：插件关键字
- `readme` (str)：插件README

### Step 3: 创建`_enter`
有的时候，我们需要让插件在被装载时执行某些操作，这时我们需要定义`_enter`函数
```python
from pbf.setup import logger
# 在PBF启动时、插件被装载时调用
def _enter():  # 如不需要可以删除
    logger.info("Test PBF Plugin loaded")
```
这里我们从`pbf.setup`中导入了`logger`，此后我们都可以使用`logger`来输出日志。 <br>
当然，如果您不需要`_enter`，也完全可以不定义他。

### Step 4: 创建接口
有的时候，我们需要在插件之间进行互通，这时我们可以定义一些开放给其他插件使用的接口
```python
# 插件开放给其他插件调用的接口
class Api:  # 如不需要可以删除
    @staticmethod
    def foo():  # 可以在其他插件中通过 `pbf.pluginsManager.require("this_plugin_name").foo()` 调用
        return "bar"
```
这里我们定义了一个`Api`类，开放的接口都需要在这个类中定义。 <br>
需要注意的是，这里的接口都是静态方法。 <br>
我们在其他插件中可以通过`pbf.pluginsManager.require("this_plugin_name(foo)").foo()`来调用这个接口。 <br>
当然，如果您不需要开放接口，也完全可以不定义他。

### Step 5: 创建监听器
插件的主体功能就是处理某些事件。这里有五类事件：`Command`, `Message`, `Notice`, `Request`, `Meta`。 <br>
我们使用`pbf.Register`装饰器来注册监听器：
```python
from pbf.utils.Register import Command, Message, Notice, Request, Meta
from pbf.controller.Data import Event
# 注册指令，匹配消息文本开头的"test"
@Command(name="test", description="test command")
def testCommand(event: Event):
    logger.info(f"test command was called: {event}")
    # do something
    logger.info(
        Msg("恭喜！\n当你收到这条消息，意味着您的第一个插件成功运行！", event=event).send())
    # 这是发送一条消息，Msg类是基于Client类的封装，具体使用请见文档
```
这里我们定义了一个`test`指令，当用户发送`test`开头的文本时，这个指令就会被调用。 <br>
您可以注意到`event`对象，这个对象里面包含了这个事件的所有信息。您可以在[这里](/pbf/controller/Data.html#Event)了解到更多信息。 <br>
`Command`以及`Message`, `Notice`, `Request`, `Meta`封装自`pbf.utils.Register`，接受参数如下：
- `name` (str)：指令名称
- `description` (str)：指令描述
- `permission` (str)：指令权限
- `usage` (str)：指令使用方法
- `alias` (List[str])：指令别名 默认为空
- `hidden` (bool)：是否隐藏指令 默认为False
- `enabled` (bool)：是否启用指令 默认为True

同样的，我们还可以创建`Message`, `Notice`, `Request`, `Meta`监听器：
```python
@Message(name="message handler")  # 注册消息处理器，会处理所有消息
def messageHandler(event: Event):
    logger.info(f"message handler was called: {event}")
    # do something


@Notice(name="notice handler")  # 注册通知处理器，会处理所有通知
def noticeHandler(event: Event):
    logger.info(f"notice handler was called: {event}")
    # do something


@Request(name="request handler")  # 注册请求处理器，会处理所有请求
def requestHandler(event: Event):
    logger.info(f"request handler was called: {event}")
    # do something


@Meta(name="meta handler")  # 注册元数据处理器，会处理所有元数据
def metaHandler(event: Event):
    logger.info(f"meta handler was called: {event}")
    # do something
```

### Step 6: 重新加载插件
如果您的PBF服务器已启动，您可以访问`{your_server_address}/plugins/load_all`来重新加载插件

### Step 7: 测试插件
对机器人发送`test`，如果您收到回复，恭喜您，您的插件已经成功运行了

### Step 8: 其他
- 通常情况下，我们的插件并不是以单文件方式呈现，因此我们可以在`~/.pbf/plugins`目录下创建一个包，在这个包里面编写插件（目录结构如下）
    ```
    /.pbf
    └── plugins
        └── foo
            ├── __init__.py  # 你的插件主体
            ├── README.md
            └── LICENSE
    └── logs
    ```
- 我们有一个插件模板，您可以在[PigBotFrameworkPlugins/template](https://github.com/PigBotFrameworkPlugins/template)找到。



## 更多内容
关于插件及PBF开发的更多内容，请查阅 [docs](/pbf/docs.html)
"""


# Version
version = "5.0.0"
version_code = 500
version_name = "5.0.0"
