"""
    pyIDM

    multi-connections internet download manager, based on "pyCuRL/curl", "youtube_dl", and "PySimpleGUI"

    :copyright: (c) 2019-2020 by Mahmoud Elshahat.
    :license: GNU LGPLv3, see LICENSE for more details.
"""

import os
import json

from . import config
from . import downloaditem
from .utils import log, handle_exceptions, update_object


def get_sett_folder():
    home_folder = os.path.expanduser('~')

    if config.operating_system == 'Windows':
        roaming = os.getenv('APPDATA')  # return APPDATA\Roaming\ under windows
        _sett_folder = os.path.join(roaming, f'.{config.APP_NAME}')

    elif config.operating_system == 'Linux':
        _sett_folder = f'{home_folder}/.config/{config.APP_NAME}/'

    elif config.operating_system == 'Darwin':
        _sett_folder = f'{home_folder}/Library/Application Support/{config.APP_NAME}/'

    else:
        _sett_folder = config.current_directory

    if not os.path.exists(_sett_folder):
        try:
            os.mkdir(_sett_folder)
        except Exception as e:
            _sett_folder = config.current_directory
            print('setting folder error:', e)

    return _sett_folder


sett_folder = get_sett_folder()


def load_d_list():
    """create and return a list of 'DownloadItem objects' based on data extracted from 'downloads.cfg' file"""
    d_list = []
    try:
        log('Load previous download items from', sett_folder)
        file = os.path.join(sett_folder, 'downloads.cfg')

        with open(file, 'r') as f:
            # expecting a list of dictionaries
            data = json.load(f)

        # converting list of dictionaries to list of DownloadItem() objects
        for dict_ in data:
            d = update_object(downloaditem.DownloadItem(), dict_)
            if d:  # if update_object() returned an updated object not None
                d_list.append(d)

        # clean d_list
        for d in d_list:
            status = config.Status.completed if d.progress >= 100 else config.Status.cancelled
            d.status = status

            d.time_left = '---'
            d.speed = '---'
            d.live_connections = 0

    except FileNotFoundError:
        log('downloads.cfg file not found')
    except Exception as e:
        handle_exceptions(f'load_d_list: {e}')
    finally:
        if not isinstance(d_list, list):
            d_list = []
        return d_list


def save_d_list(d_list):
    try:
        data = []
        for d in d_list:
            d.q = None
            data.append(d.__dict__)  # append object attributes dictionary to data list

        file = os.path.join(sett_folder, 'downloads.cfg')

        with open(file, 'w') as f:
            try:
                json.dump(data, f)
            except:
                pass
        log('list saved')
    except Exception as e:
        handle_exceptions(e)


def load_setting():
    setting = {}
    try:
        log('Load Application setting from', sett_folder)
        file = os.path.join(sett_folder, 'setting.cfg')
        with open(file, 'r') as f:
            setting = json.load(f)

    except FileNotFoundError:
        log('setting.cfg not found')
    except Exception as e:
        handle_exceptions(e)
    finally:
        if not isinstance(setting, dict):
            setting = {}

        # download folder
        folder = setting.get('folder', None)
        if folder and os.path.isdir(folder):
            config.download_folder = folder
        else:
            config.download_folder = os.path.join(os.path.expanduser("~"), 'Downloads')

        # clipboard monitor
        config.monitor_clipboard = setting.get('monitor', True)

        # max concurrent downloads
        config.concurrent_downloads = setting.get('concurrent_downloads', config.DEFAULT_CONCURRENT_CONNECTIONS)

        # download window
        config.show_download_window = setting.get('show_download_window', True)

        # theme
        config.current_theme = setting.get('theme', config.DEFAULT_THEME)

        # check_for_update_on_startup
        config.check_for_update_on_startup = setting.get('check_for_update_on_startup', True)

        # ffmpeg folder, will be loaded if it has been set by user otherwise will use setting folder as a fallback
        config.ffmpeg_installation_folder = setting.get('ffmpeg_installation_folder', sett_folder)


def save_setting():
    setting = dict()
    setting['download_folder'] = config.download_folder
    setting['monitor'] = config.monitor_clipboard
    setting['max_concurrent_downloads'] = config.max_concurrent_downloads
    setting['show_download_window'] = config.show_download_window
    setting['theme'] = config.current_theme
    setting['check_for_update_on_startup'] = config.check_for_update_on_startup
    setting['ffmpeg_installation_folder'] = config.ffmpeg_installation_folder

    try:
        file = os.path.join(sett_folder, 'setting.cfg')
        with open(file, 'w') as f:
            json.dump(setting, f)
            log('setting saved')
    except Exception as e:
        handle_exceptions(e)