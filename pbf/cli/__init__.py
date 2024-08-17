import json
import click
import os
import pathlib
import art

art_txt = art.text2art("PBF CLI", font='larry3d')
_template_repo = "https://github.com/PigBotFrameworkPlugins/"
_home_path = pathlib.Path().home()
_plugins_path = os.path.join(_home_path, ".pbf", "plugins")
_start_template_version = "0.1.0"
_start_template = """
# Step 1: import config and modify it
from pbf import config

config.logs_level = "DEBUG"
# Modify more configurations here

# Step 2: import setup and setup
from pbf import setup

setup.setup(__name__)

# Step 3: import driver and start it
if __name__ == "__main__":
    from pbf.driver import Fastapi

    Fastapi.start()
"""


def printPBF():
    # 打印`PigBotFramework`字符画
    print(click.style(art_txt, fg='green'))


def installPlugin(plugin_id: str, plugin_name: str, plugins_path: str):
    try:
        from git import Repo
        Repo.clone_from(f"{_template_repo}{plugin_id}", os.path.join(plugins_path, plugin_name))
    except Exception as e:
        click.secho(f'Error: {e}', fg='red')
        return

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
    with open('start.py', 'w', encoding="utf-8") as f:
        f.write(_start_template)
    click.secho('start.py created', fg='green')
    with open(".pbflock", 'w', encoding="utf-8") as f:
        f.write(json.dumps({
            "version": _start_template_version
        }))
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
    installPlugin('template', plugin_name, plugins_path)
    click.secho('Done.', fg='green')

@cli.command(
    help='Install a plugin from GitHub/PigBotFrameworkPlugins/'
)
@click.argument('plugin_id')
@click.option('--plugins_path', '-p', help='The path to store plugins', default=_plugins_path)
def install_plugin(plugin_id: str, plugins_path: str):
    click.secho('Installing plugin ...')
    installPlugin(plugin_id, plugin_id, plugins_path)
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
