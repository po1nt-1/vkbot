import inspect
import os
import sys
import traceback
from datetime import datetime
from io import BytesIO

import requests
import vk_api
from vk_api.utils import get_random_id

KNOWN_CHATS = [
    2000000001,
    2000000002,
    2000000003
]


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


def send_photo(bot_api, id, x):
    try:
        img = requests.get(f"https://this{x}doesnotexist.com/").content
        f = BytesIO(img)

        uploader = vk_api.upload.VkUpload(bot_api)
        response = uploader.photo_messages(f)[0]

        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']

        bot_api.messages.send(
            random_id=get_random_id(),
            peer_id=id,
            attachment=f'photo{owner_id}_{photo_id}_{access_key}'
        )

    except vk_api.exceptions.ApiError as e:
        error = f"{traceback.format_exc()}\n" + \
            f"Stopped with: {e}"

        set_error(error)

        try:
            bot_api.messages.send(
                random_id=get_random_id(),
                peer_id=200411727,
                message=error
            )
        except vk_api.exceptions.ApiError:
            pass


def send_m(bot_api, id, m):
    try:
        bot_api.messages.send(
            random_id=get_random_id(),
            peer_id=id,
            message=m
        )
    except vk_api.exceptions.ApiError as e:
        error = f"{traceback.format_exc()}\n" + \
            f"Stopped with: {e}"

        set_error(error)

        try:
            bot_api.messages.send(
                random_id=get_random_id(),
                peer_id=200411727,
                message=error
            )
        except vk_api.exceptions.ApiError:
            pass


def vk_to_json(bot_api, raw):
    raw = raw.obj

    uxt = datetime.fromtimestamp(raw["date"] + 25200)
    data = f'date: {str(uxt.strftime("%Y-%m-%d %H:%M:%S"))}\n'
    data += f'from: https://vk.com/id{int(raw["from_id"])}\n'
    data += f'text: {str(raw["text"])}\n'

    peer_id = int(raw["peer_id"])

    if peer_id == 200411727:
        peer_id = "me"
    elif peer_id >= 2000000000 and not (peer_id in KNOWN_CHATS):
        m = f"unknown chat: '{peer_id}': \n"
        try:
            title = bot_api.messages.getConversationsById(
                peer_ids=peer_id)["items"][0]["chat_settings"]["title"]
            m += "group name: " + title
            peer_id = title
        except IndexError:
            send_m(bot_api, peer_id, "I need admin rights, please!")

        send_m(bot_api, 200411727, m)
    elif peer_id < 2000000000:
        m = f"unknown user: '{peer_id}': \n"
        m += f"https://vk.com/id{peer_id}"

        send_m(bot_api, 200411727, m)

    data += f'peer: {peer_id}\n'

    if len(raw["attachments"]) != 0:
        raw_att = raw["attachments"]

        att = '{'

        for i in range(len(raw_att)):
            iraw = raw_att[i]

            att += f'{iraw["type"]}: ' + f'{iraw[iraw["type"]]}, '

        att = att[:-2]

        data += f'attachments: {str(att)}' + '}\n'

    data += '-' * 30 + '\n'

    return data
