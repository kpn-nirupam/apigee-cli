import configparser
import json
import os
import shutil
import stat
import sys
from os import path
from pathlib import Path

import click

from apigee import (APIGEE_CLI_PLUGINS_CONFIG_FILE,
                    APIGEE_CLI_PLUGINS_DIRECTORY, APIGEE_CLI_PLUGINS_PATH,
                    console)
from apigee.silent import common_silent_options
from apigee.utils import is_dir, make_dirs, run_func_on_dir_files, touch
from apigee.verbose import common_verbose_options

is_git_installed = False
plugins_command_help = '[Experimental] Simple plugins manager for distributing commands.'

try:
    import git
    from git import Git, Repo

    is_git_installed = True
except ImportError:
    plugins_command_help = (
        '[Unavailable - Git not found] Simple plugins manager for distributing commands.'
    )



def exit_if_git_not_installed():
    if not is_git_installed:
        sys.exit(0)


@click.group(help=plugins_command_help)
def plugins():
    pass


def init():
    make_dirs(APIGEE_CLI_PLUGINS_DIRECTORY)
    touch(APIGEE_CLI_PLUGINS_PATH)
    touch(APIGEE_CLI_PLUGINS_CONFIG_FILE)


def load_config(config_file=APIGEE_CLI_PLUGINS_CONFIG_FILE):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    return config


def save_config(plugins_file, config_file, section='sources'):
    init()
    config = load_config()
    if not config._sections:
        return


def clone_all(section='sources'):
    init()
    config = load_config()
    if not config._sections:
        return
    sources = dict(config._sections[section])
    for name, uri in sources.items():
        dest = Path(APIGEE_CLI_PLUGINS_DIRECTORY) / name
        if is_dir(dest):
            continue
        try:
            console.echo(f'Installing {name}... ', end='', flush=True)
            Repo.clone_from(uri, dest)
            console.echo('Done')
        except Exception as e:
            console.echo(e)


def pull_all():
    def _func(path):
        if not is_dir(path):
            return
        console.echo(f'Updating {Path(path).stem}... ', end='', flush=True)
        repo = Repo(path)
        if repo.bare:
            return
        try:
            repo.remotes['origin'].pull()
            console.echo('Done')
        except Exception as e:
            console.echo(e)

    return run_func_on_dir_files(APIGEE_CLI_PLUGINS_DIRECTORY, _func, glob='[!.][!__]*')


@plugins.command(help='Edit config file manually.')
@common_silent_options
@common_verbose_options
@click.option(
    '-a/-A',
    '--apply-changes/--no-apply-changes',
    default=False,
    help='Install plugins from new sources after exiting the editor.',
    show_default=True,
)
def configure(silent, verbose, apply_changes):
    exit_if_git_not_installed()
    init()
    click.edit(filename=APIGEE_CLI_PLUGINS_CONFIG_FILE)
    if apply_changes:
        clone_all()
        prune_all()
    else:
        console.echo('\n  Run `apigee plugins update` to apply any changes,')
        console.echo('    or rerun `apigee plugins configure` with `-a`')
        console.echo('    to apply changes automatically.\n')


def install():
    pass


@plugins.command(help='Update or install plugins.')
@common_silent_options
@common_verbose_options
def update(silent, verbose, section='sources'):
    exit_if_git_not_installed()
    clone_all()
    pull_all()


def show():
    pass


def info():
    pass


def chmod_directory(directory, mode):
    """https://stackoverflow.com/a/58878271"""
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            os.chmod(path.join(root, dir), mode)
        for file in files:
            os.chmod(path.join(root, file), mode)


def prune_all(section='sources'):
    init()
    config = load_config()
    if not config._sections:
        return
    sources = dict(config._sections[section])

    def _func(path):
        if not is_dir(path):
            return
        name = Path(path).stem
        if name in sources.keys():
            return
        console.echo(f'Removing {name}... ', end='', flush=True)
        plugin_directory = Path(APIGEE_CLI_PLUGINS_DIRECTORY) / name
        try:
            chmod_directory(str(Path(plugin_directory) / '.git'), stat.S_IRWXU)
            shutil.rmtree(plugin_directory)
            console.echo('Done')
        except Exception as e:
            console.echo(e)

    return run_func_on_dir_files(APIGEE_CLI_PLUGINS_DIRECTORY, _func, glob='[!.][!__]*')


@plugins.command(help='Prune plugins with removed sources.')
@common_silent_options
@common_verbose_options
def prune(silent, verbose, section='sources'):
    exit_if_git_not_installed()
    prune_all()


def uninstall():
    pass


def clean():
    pass
