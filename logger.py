import inspect
import os
import sys
from datetime import datetime

from bot import report


def get_script_dir(follow_symlinks: bool = True) -> str:
    # https://clck.ru/P8NUA
    if getattr(sys, 'frozen', False):  # type: ignore
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def set_error(e):
    with open(os.path.join(get_script_dir(), "control", "output"), 'a',
              encoding="utf-8") as f:
        data = str(e) + '\n' + '-' * 30 + '\n'
        f.write(data)


def vk_to_json(bot_api, raw):
    raw = raw.obj

    uxt = datetime.fromtimestamp(raw["date"] + 25200)
    data = f'date: {str(uxt.strftime("%Y-%m-%d %H:%M:%S"))}\n'
    data += f'from: https://vk.com/id{int(raw["from_id"])}\n'
    data += f'text: {str(raw["text"])}\n'

    peer_id = int(raw["peer_id"])
    if peer_id == 200411727:
        peer_id = "me"
    elif peer_id == 2000000001:
        peer_id = "лаборатория"
    elif peer_id == 2000000002:
        peer_id = "Amatorria's people"
    elif peer_id == 2000000003:
        peer_id = "приличное название"

    else:
        m = f"unknown peer_id: {peer_id}: \n"
        m += f"https://vk.com/club{peer_id} or\n"
        m += f"https://vk.com/id{peer_id}"
        report(bot_api, m)

    data += f'peer: {peer_id}\n'

    if len(raw["attachments"]) != 0:
        raw_att = raw["attachments"]

        att = '{'

        types = []
        for i in range(len(raw_att)):
            iraw = raw_att[i]

            if iraw["type"] == "link":
                att += f'{iraw["type"]}: {iraw["poll"]}, '
            else:
                att += f'{iraw["type"]}: ' + f'{iraw[iraw["type"]]}, '

        att = att[:-2]

        data += f'attachments: {str(att)}' + '}\n'

    data += '-' * 30 + '\n'

    return data
