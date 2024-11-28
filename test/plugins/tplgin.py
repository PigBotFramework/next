from pbf.utils import MetaData
from pbf.controller.Data import Event
from pbf.utils.Register import Command, RegexMode
from pbf.setup import logger


# 插件元数据
meta_data = MetaData(
    name="test",
    version="0.1.0",
    versionCode=10,
    description="PBF Plugin",
    author="XzyStudio",
    license="MIT",
    keywords=["pbf", "plugin", "test"],
    readme="""
    # PBF Plugin
    hi
    """
)

