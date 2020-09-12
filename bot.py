import inspect
import json
import os
import sys
import traceback
from datetime import datetime

import requests
import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id

import dialog
import logger


class my_err(Exception):
    pass


def get_script_dir(follow_symlinks: bool = True) -> str:
    # https://clck.ru/P8NUA
    if getattr(sys, 'frozen', False):  # type: ignore
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def report(bot_api, m):
    bot_api.messages.send(
        random_id=get_random_id(),
        peer_id=200411727,
        message=m
    )


def fast_input(event, bot_api):
    if not os.path.exists(os.path.join(get_script_dir(), "control", "input")):
        with open(os.path.join(get_script_dir(), "control", "input"), 'w',
                  encoding="utf-8") as f:
            pass

    with open(os.path.join(get_script_dir(), "control", "input"), 'r',
              encoding="utf-8") as f:
        text = "".join(f.readlines())

    with open(os.path.join(get_script_dir(), "control", "input"), 'w',
              encoding="utf-8") as f:
        f.write("")

    if len(text) > 0 and not text.isspace():
        bot_api.messages.send(
            random_id=get_random_id(),
            peer_id=event.obj.peer_id,
            message=text
        )


def auth_pars(auth):
    token, group_id = auth.split("Z")
    return token, group_id


def main():
    try:
        with open(os.path.join(get_script_dir(), "sec.json"), 'r', encoding="utf-8") as f:
            auth = json.load(f)

        token, group_id = auth_pars(auth)

    except FileNotFoundError:
        token, group_id = auth_pars(input("?: "))

    bot_session = vk_api.VkApi(token=token)

    bot_api = bot_session.get_api()
    longpoll = vk_api.bot_longpoll.VkBotLongPoll(bot_session, group_id)

    while True:
        try:
            print("ok")

            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    last_message = logger.vk_to_json(bot_api, event)

                    if not os.path.exists(os.path.join(get_script_dir(),
                                                       "control")):
                        os.mkdir(os.path.join(get_script_dir(), "control"))

                    with open(os.path.join(get_script_dir(), "control",
                                           "output"), 'a',
                              encoding="utf-8") as f:
                        f.write(last_message)

                    if event.from_chat:
                        fast_input(event=event, bot_api=bot_api)

                        dialog.hellbye(bot_api, event)

        except requests.exceptions.ReadTimeout as e:
            print(e)
            print(traceback.format_exc())
            continue
        except Exception as e:
            value = datetime.fromtimestamp(event.obj["date"] + 25200)
            date = value.strftime("%Y-%m-%d %H:%M:%S")
            error = f"{traceback.format_exc()}\n" + \
                f"Stopped with: {e} \nin {str(date)}"

            logger.set_error(error)

            value = datetime.fromtimestamp(event.obj["date"])
            date = value.strftime("%Y-%m-%d %H:%M:%S")
            error = f"{traceback.format_exc()}\n" + \
                f"Stopped with: {e} \nin {str(date)}"

            report(bot_api, error)

            raise my_err(error)


if __name__ == "__main__":
    try:
        print("\tSTART")
        main()
    except KeyboardInterrupt:
        sys.exit
    except my_err as e:
        print(e)
    finally:
        print("\n\tSTOP")
