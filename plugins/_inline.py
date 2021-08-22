# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re
import time
from datetime import datetime
from math import ceil
from os import remove

from git import Repo
from pyUltroid.dB.core import *
from pyUltroid.misc import owner_and_sudos
from support import *
from telethon.tl.types import InputBotInlineResult, InputWebDocument

from . import *

# ================================================#
notmine = f"This bot is for {OWNER_NAME}"

TLINK = "https://telegra.ph/file/d9c9bc13647fa1d96e764.jpg"
helps = get_string("inline_1")

add_ons = udB.get("ADDONS")
if add_ons == "True" or add_ons is None:
    zhelps = get_string("inline_2")
else:
    zhelps = get_string("inline_3")

C_PIC = udB.get("INLINE_PIC")

if C_PIC:
    _file_to_replace = C_PIC
    TLINK = C_PIC
else:
    _file_to_replace = "resources/extras/inline.jpg"
# ============================================#


# --------------------BUTTONS--------------------#

_main_help_menu = [
    [
        Button.inline("🗂 Plugins", data="hrrrr"),
        Button.inline("🗃 Addons", data="frrr"),
    ],
    [
        Button.inline("👤 Owner Tools", data="ownr"),
        Button.inline("🔍 Inline Plugins", data="inlone"),
    ],
    [
        Button.url("🔧 Settings", url=f"https://t.me/{asst.me.username}?start=set"),
    ],
    [Button.inline("Close", data="close")],
]

SUP_BUTTONS = [
    [
        Button.url("Repo", url="https://github.com/TeamUltroid/Ultroid"),
        Button.url("Addons", url="https://github.com/TeamUltroid/UltroidAddons"),
    ],
    [Button.url("Support", url="t.me/UltroidSupport")],
]

# --------------------BUTTONS--------------------#


@in_pattern("")
@in_owner
async def inline_alive(o):
    if len(o.text) == 0:
        b = o.builder
        MSG = "• **Violet Userbot •**"
        uptime = time_formatter((time.time() - start_time) * 1000)
        MSG += f"\n\n• **Uptime** - `{uptime}`\n"
        MSG += f"• **OWNER** - `{OWNER_NAME}`"
        WEB0 = InputWebDocument(
            "https://telegra.ph/file/55dd0f381c70e72557cb1.jpg", 0, "image/jpg", []
        )
        RES = [
            InputBotInlineResult(
                str(o.id),
                "photo",
                send_message=await b._message(
                    text=MSG,
                    media=True,
                    buttons=SUP_BUTTONS,
                ),
                title="Violet Userbot",
                description="Kircheiss | Userbot",
                url=TLINK,
                thumb=WEB0,
                content=InputWebDocument(TLINK, 0, "image/jpg", []),
            )
        ]
        await o.answer(RES, switch_pm=f"👥 Violet Settings", switch_pm_param="start")


@in_pattern("ultd")
@in_owner
async def inline_handler(event):
    z = []
    for x in LIST.values():
        for y in x:
            z.append(y)
    result = event.builder.photo(
        file=_file_to_replace,
        link_preview=False,
        text=get_string("inline_4").format(
            OWNER_NAME,
            len(PLUGINS),
            len(ADDONS),
            len(z),
        ),
        buttons=_main_help_menu,
    )
    await event.answer([result], gallery=True)


@in_pattern("haste")
@in_owner
async def _(event):
    ok = event.text.split(" ")[1]
    link = "https://hastebin.com/"
    result = event.builder.article(
        title="Paste",
        text="Pᴀsᴛᴇᴅ Tᴏ Hᴀsᴛᴇʙɪɴ!",
        buttons=[
            [
                Button.url("HasteBin", url=f"{link}{ok}"),
                Button.url("Raw", url=f"{link}raw/{ok}"),
            ],
        ],
    )
    await event.answer([result])


@callback("ownr")
@owner
async def setting(event):
    z = []
    for x in LIST.values():
        for y in x:
            z.append(y)
    cmd = len(z)
    await event.edit(
        get_string("inline_4").format(
            OWNER_NAME,
            len(PLUGINS),
            len(ADDONS),
            cmd,
        ),
        file=_file_to_replace,
        link_preview=False,
        buttons=[
            [
                Button.inline("📶 Ping", data="pkng"),
                Button.inline("⏺ Uptime", data="upp"),
            ],
            [
                Button.inline("🔄 Restart", data="rstrt"),
                Button.inline("🔂 Update", data="doupdate"),
            ],
            [Button.inline("« Back", data="open")],
        ],
    )


@callback("doupdate")
@owner
async def _(event):
    check = await updater()
    if not check:
        return await event.answer(
            "You're already on the latest version", cache_time=0, alert=True
        )
    repo = Repo.init()
    ac_br = repo.active_branch
    changelog, tl_chnglog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    changelog_str = changelog + f"\n\nClick the below button to update!"
    if len(changelog_str) > 1024:
        await event.edit(get_string("upd_4"))
        file = open(f"ultroid_updates.txt", "w+")
        file.write(tl_chnglog)
        file.close()
        await event.edit(
            get_string("upd_5"),
            file="ultroid_updates.txt",
            buttons=[
                [Button.inline("• Update now •", data="updatenow")],
                [Button.inline("« Back", data="ownr")],
            ],
        )
        remove(f"ultroid_updates.txt")
        return
    else:
        await event.edit(
            changelog_str,
            buttons=[
                [Button.inline("Update Now", data="updatenow")],
                [Button.inline("« Back", data="ownr")],
            ],
            parse_mode="html",
        )


@callback("pkng")
async def _(event):
    start = datetime.now()
    end = datetime.now()
    ms = (end - start).microseconds
    pin = f"📊 Ping = {ms} microseconds"
    await event.answer(pin, cache_time=0, alert=True)


@callback("upp")
async def _(event):
    uptime = time_formatter((time.time() - start_time) * 1000)
    pin = f"⌛️ Uptime = {uptime}"
    await event.answer(pin, cache_time=0, alert=True)


@callback("inlone")
@owner
async def _(e):
    button = [
        [
            Button.switch_inline(
                "PlayStore apps",
                query="app telegram",
                same_peer=True,
            ),
            Button.switch_inline(
                "Modded apps",
                query="mods minecraft",
                same_peer=True,
            ),
        ],
        [
            Button.switch_inline(
                "Search on Google",
                query="Things that are naturally purple",
                same_peer=True,
            ),
            Button.switch_inline(
                "Search on Yahho",
                query="yahoo Violet color",
                same_peer=True,
            ),
        ],
        [
            Button.switch_inline(
                "Whisper",
                query="msg username wspr Hello",
                same_peer=True,
            ),
            Button.switch_inline(
                "Youtube Downloader",
                query="yt Glass Animals Youth",
                same_peer=True,
            ),
        ],
        [
            Button.switch_inline(
                "EBooks Uploader",
                query="ebooks Brazil",
                same_peer=True,
            ),
            Button.switch_inline(
                "OrangeFox🦊",
                query="ofox beryllium",
                same_peer=True,
            ),
        ],
        [
            Button.inline(
                "« Back",
                data="open",
            ),
        ],
    ]
    await e.edit(buttons=button, link_preview=False)


@callback("hrrrr")
@owner
async def on_plug_in_callback_query_handler(event):
    xhelps = helps.format(OWNER_NAME, len(PLUGINS))
    buttons = page_num(0, PLUGINS, "helpme", "def")
    await event.edit(f"{xhelps}", buttons=buttons, link_preview=False)


@callback("frrr")
@owner
async def addon(event):
    halp = zhelps.format(OWNER_NAME, len(ADDONS))
    if len(ADDONS) > 0:
        buttons = page_num(0, ADDONS, "addon", "add")
        await event.edit(f"{halp}", buttons=buttons, link_preview=False)
    else:
        await event.answer(
            f"• Type `{HNDLR}setredis ADDONS True`\n to get addons plugins",
            cache_time=0,
            alert=True,
        )


@callback("rstrt")
@owner
async def rrst(ult):
    await restart(ult)


@callback(
    re.compile(
        rb"helpme_next\((.+?)\)",
    ),
)
@owner
async def on_plug_in_callback_query_handler(event):
    current_page_number = int(event.data_match.group(1).decode("UTF-8"))
    buttons = page_num(current_page_number + 1, PLUGINS, "helpme", "def")
    await event.edit(buttons=buttons, link_preview=False)


@callback(
    re.compile(
        rb"helpme_prev\((.+?)\)",
    ),
)
@owner
async def on_plug_in_callback_query_handler(event):
    current_page_number = int(event.data_match.group(1).decode("UTF-8"))
    buttons = page_num(current_page_number - 1, PLUGINS, "helpme", "def")
    await event.edit(buttons=buttons, link_preview=False)


@callback(
    re.compile(
        rb"addon_next\((.+?)\)",
    ),
)
@owner
async def on_plug_in_callback_query_handler(event):
    current_page_number = int(event.data_match.group(1).decode("UTF-8"))
    buttons = page_num(current_page_number + 1, ADDONS, "addon", "add")
    await event.edit(buttons=buttons, link_preview=False)


@callback(
    re.compile(
        rb"addon_prev\((.+?)\)",
    ),
)
@owner
async def on_plug_in_callback_query_handler(event):
    current_page_number = int(event.data_match.group(1).decode("UTF-8"))
    buttons = page_num(current_page_number - 1, ADDONS, "addon", "add")
    await event.edit(buttons=buttons, link_preview=False)


@callback("back")
@owner
async def backr(event):
    xhelps = helps.format(OWNER_NAME, len(PLUGINS))
    current_page_number = int(upage)
    buttons = page_num(current_page_number, PLUGINS, "helpme", "def")
    await event.edit(
        f"{xhelps}",
        file=_file_to_replace,
        buttons=buttons,
        link_preview=False,
    )


@callback("buck")
@owner
async def backr(event):
    xhelps = zhelps.format(OWNER_NAME, len(ADDONS))
    current_page_number = int(upage)
    buttons = page_num(current_page_number, ADDONS, "addon", "add")
    await event.edit(
        f"{xhelps}",
        file=_file_to_replace,
        buttons=buttons,
        link_preview=False,
    )


@callback("open")
@owner
async def opner(event):
    z = []
    for x in LIST.values():
        for y in x:
            z.append(y)
    await event.edit(
        get_string("inline_4").format(
            OWNER_NAME,
            len(PLUGINS),
            len(ADDONS),
            len(z),
        ),
        buttons=_main_help_menu,
        link_preview=False,
    )


@callback("close")
@owner
async def on_plug_in_callback_query_handler(event):
    await event.edit(
        get_string("inline_5"),
        file=_file_to_replace,
        buttons=Button.inline("Open Menu ⤴️", data="open"),
    )


@callback(
    re.compile(
        b"def_plugin_(.*)",
    ),
)
@owner
async def on_plug_in_callback_query_handler(event):
    plugin_name = event.data_match.group(1).decode("UTF-8")
    help_string = f"Plugin Name - `{plugin_name}`\n"
    try:
        for i in HELP[plugin_name]:
            help_string += i
    except BaseException:
        pass
    if help_string == "":
        reply_pop_up_alert = f"{plugin_name} has no detailed help..."
    else:
        reply_pop_up_alert = help_string
    reply_pop_up_alert += "\n© @Kircheiss"
    buttons = [
        [
            Button.inline(
                "Send Plugin 📤",
                data=f"sndplug_{(event.data).decode('UTF-8')}",
            )
        ],
        [
            Button.inline("« Back", data="back"),
            Button.inline("Close", data="close"),
        ],
    ]
    try:
        if str(event.query.user_id) in owner_and_sudos():
            await event.edit(
                reply_pop_up_alert,
                buttons=buttons,
            )
        else:
            reply_pop_up_alert = notmine
            await event.answer(reply_pop_up_alert, cache_time=0)
    except BaseException:
        halps = f"Do .help {plugin_name} to get the list of commands."
        await event.edit(halps, buttons=buttons)


@callback(
    re.compile(
        b"add_plugin_(.*)",
    ),
)
@owner
async def on_plug_in_callback_query_handler(event):
    plugin_name = event.data_match.group(1).decode("UTF-8")
    help_string = ""
    try:
        for i in HELP[plugin_name]:
            help_string += i
    except BaseException:
        try:
            for u in CMD_HELP[plugin_name]:
                help_string = f"Plugin Name-{plugin_name}\n\n✘ Commands Available-\n\n"
                help_string += str(CMD_HELP[plugin_name])
        except BaseException:
            try:
                if plugin_name in LIST:
                    help_string = (
                        f"Plugin Name-{plugin_name}\n\n✘ Commands Available-\n\n"
                    )
                    for d in LIST[plugin_name]:
                        help_string += HNDLR + d
                        help_string += "\n"
            except BaseException:
                pass
    if help_string == "":
        reply_pop_up_alert = f"{plugin_name} has no detailed help..."
    else:
        reply_pop_up_alert = help_string
    reply_pop_up_alert += "\n© @Kircheiss"
    buttons = [
        [
            Button.inline(
                "« Send Plugin »",
                data=f"sndplug_{(event.data).decode('UTF-8')}",
            )
        ],
        [
            Button.inline("« Back", data="buck"),
            Button.inline("Close", data="close"),
        ],
    ]
    try:
        if str(event.query.user_id) in owner_and_sudos():
            await event.edit(
                reply_pop_up_alert,
                buttons=buttons,
            )
        else:
            reply_pop_up_alert = notmine
            await event.answer(reply_pop_up_alert, cache_time=0)
    except BaseException:
        halps = f"Do .help {plugin_name} to get the list of commands."
        await event.edit(halps, buttons=buttons)


def page_num(page_number, loaded_plugins, prefix, type):
    number_of_rows = 5
    number_of_cols = 2
    emoji = Redis("EMOJI_IN_HELP")
    if emoji:
        multi = emoji
    else:
        multi = "✘"
    helpable_plugins = []
    global upage
    upage = page_number
    for p in loaded_plugins:
        helpable_plugins.append(p)
    helpable_plugins = sorted(helpable_plugins)
    modules = [
        Button.inline(
            "{} {} {}".format(
                multi,
                x,
                multi,
            ),
            data=f"{type}_plugin_{x}",
        )
        for x in helpable_plugins
    ]
    pairs = list(zip(modules[::number_of_cols], modules[1::number_of_cols]))
    if len(modules) % number_of_cols == 1:
        pairs.append((modules[-1],))
    max_num_pages = ceil(len(pairs) / number_of_rows)
    modulo_page = page_number % max_num_pages
    if len(pairs) > number_of_rows:
        pairs = pairs[
            modulo_page * number_of_rows : number_of_rows * (modulo_page + 1)
        ] + [
            (
                Button.inline(
                    "« Previous",
                    data=f"{prefix}_prev({modulo_page})",
                ),
                Button.inline("« Back »", data="open"),
                Button.inline(
                    "Next »",
                    data=f"{prefix}_next({modulo_page})",
                ),
            ),
        ]
    else:
        pairs = pairs[
            modulo_page * number_of_rows : number_of_rows * (modulo_page + 1)
        ] + [(Button.inline("« Back »", data="open"),)]
    return pairs
