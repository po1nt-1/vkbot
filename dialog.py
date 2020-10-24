import inspect
import json
import os
import random
import sys

import logger


def get_script_dir(follow_symlinks: bool = True) -> str:
    # https://clck.ru/P8NUA
    if getattr(sys, 'frozen', False):  # type: ignore
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def delsym(word, syms):
    for sym in syms:
        word = word.replace(sym, " ")

    return word


def hellbye(bot_api, event):
    seq = [True] + [False] * 4

    if not os.path.exists(os.path.join(get_script_dir(), "dict.json")):
        with open(os.path.join(get_script_dir(), "dict.json"), 'w',
                  encoding="utf-8") as f:
            pass
    with open(os.path.join(get_script_dir(), "dict.json"), 'r',
              encoding="utf-8") as f:
        dictionary = json.load(f)

    response = delsym(event.obj.text.lower(), dictionary["syms"])

    flag = False

    for elem in dictionary["q_hells"]:
        if elem in response:
            a_hell = random.choice(dictionary["a_hells"])
            if random.choice(seq):
                a_hell = a_hell.capitalize()
            if random.choice(seq):
                a_hell += "!"
            elif random.choice(seq):
                a_hell += " :)"
            elif random.choice(seq):
                a_hell += " :("

            logger.send_m(bot_api, event.obj.peer_id, a_hell)
            flag = True
            break

    if flag is False:
        for elem in dictionary["q_byes"]:
            if elem in response:
                a_bye = random.choice(dictionary["a_byes"])
                if random.choice(seq):
                    a_bye = a_bye.capitalize()
                if random.choice(seq):
                    a_bye += "!"
                elif random.choice(seq):
                    a_bye += " :)"
                elif random.choice(seq):
                    a_bye += " :("

                logger.send_m(bot_api, event.obj.peer_id, a_bye)
                break

    for elem in dictionary["q_hows"]:
        if elem in response:
            a_how = random.choice(dictionary["a_hows"])
            if random.choice(seq):
                a_how = a_how.capitalize()
            if random.choice(seq):
                a_how += "!"
            elif random.choice(seq):
                a_how += " :)"
            elif random.choice(seq):
                a_how += " :("

            logger.send_m(bot_api, event.obj.peer_id, a_how)
            break

    for elem in dictionary["q_ip"]:
        if elem in response:
            logger.send_m(bot_api, event.obj.peer_id, dictionary["a_ip"])
            break

    if "мя" in response or "meo" in response or "мау" in response:
        logger.send_photo(bot_api, event.obj.peer_id, 'cat')
