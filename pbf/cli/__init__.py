import click
import start_example
import inspect
import textwrap
import os
from git import Repo
import pathlib
import art


art_txt = art.text2art("PBF CLI", font='larry3d')
_template_repo = "https://github.com/PigBotFrameworkPlugins/template"
_home_path = pathlib.Path().home()
_plugins_path = os.path.join(_home_path, ".pbf", "plugins")


def printPBF():
    # 打印`PigBotFramework`字符画
    print(click.style(art_txt, fg='green'))


@click.group(
    help=f'{art_txt}\n'
)
def cli():
    pass


@cli.command(
    help='Initialize the project in the current directory'
)
def init():
    click.secho('Initializing')
    if '.pbflock' in os.listdir():
        click.secho('.pbflock exists, exiting', fg="red")
        return
    with open('start.py', 'w') as f:
        # 读取start.py文件内容并写入
        content = inspect.getsource(start_example.content)
        # 去掉函数定义行
        lines = content.splitlines()[1:]
        # 去掉多余的缩进
        function_body = textwrap.dedent("\n".join(lines))
        f.write(function_body)
    click.secho('start.py created', fg='green')
    with open(".pbflock", 'w') as f:
        f.write('true')
    click.secho('.pbflock created', fg='green')
    click.secho("Now you can run 'pbf start' to start the server", fg='green')


@cli.command(
    help='Start the server'
)
def start():
    click.secho('Starting')
    if '.pbflock' not in os.listdir():
        click.secho('.pbflock not found, please run `pbf init` first', fg='red')
        return
    if 'start.py' not in os.listdir():
        click.secho('start.py not found, please run `pbf init` first', fg='red')
        os.remove('.pbflock')
        return
    # 后台执行start.py
    # 检测运行系统
    if os.name == 'nt':
        # Windows 使用cmd指令将进程挂起到后台
        os.system('start python start.py')
    else:
        # Linux 使用nohup
        os.system('nohup python start.py &')

    click.secho('Server started', fg='green')


@cli.command(
    help='Create a new plugin'
)
@click.argument('plugin_name')
@click.option('--plugins_path', '-p', help='The path to store plugins', default=_plugins_path)
def create_plugin(plugin_name: str, plugins_path: str):
    click.secho('Clone template ...')
    try:
        Repo.clone_from(_template_repo, os.path.join(plugins_path, plugin_name))
    except Exception as e:
        click.secho(f'Error: {e}', fg='red')
        return
    click.secho('Done.', fg='green')


@cli.command(
    help='List all plugins'
)
@click.option('--plugins_path', '-p', help='The path to store plugins', default=_plugins_path)
def list_plugin(plugins_path: str):
    plugins = os.listdir(plugins_path)
    for plugin in plugins:
        click.secho(plugin)


@cli.command(
    help='Remove a plugin'
)
@click.argument('plugin_name')
@click.option('--plugins_path', '-p', help='The path to store plugins', default=_plugins_path)
def remove_plugin(plugin_name: str, plugins_path: str):
    try:
        os.system(f'rm -rf {os.path.join(plugins_path, plugin_name)}')
    except Exception as e:
        click.secho(f'Error: {e}', fg='red')
        return
    click.secho('Done.', fg='green')


if __name__ == '__main__':
    cli()