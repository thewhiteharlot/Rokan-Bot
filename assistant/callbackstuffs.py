# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re
import urllib
from glob import glob
from os import remove
from random import choices

from telegraph import Telegraph
from telegraph import upload_file as upl

from . import *

# --------------------------------------------------------------------#
telegraph = Telegraph()
r = telegraph.create_account(short_name="Ultroid")
auth_url = r["auth_url"]
# --------------------------------------------------------------------#


TOKEN_FILE = "resources/auths/auth_token.txt"


@callback(
    re.compile(
        "ebk_(.*)",
    ),
)
async def eupload(event):
    match = event.pattern_match.group(1).decode("utf-8")
    await event.answer("Uploading..")
    try:
        await event.edit(
            file=f"https://www.gutenberg.org/files/{match}/{match}-pdf.pdf"
        )
    except BaseException:
        book = "Ultroid-Book.epub"
        urllib.request.urlretrieve(
            "https://www.gutenberg.org/ebooks/132.epub.images", book
        )
        fn, media, _ = await asst._file_to_media(
            book, thumb="resources/extras/ultroid.jpg"
        )
        await event.edit(file=media)
        remove(book)


@callback(
    re.compile(
        "sndplug_(.*)",
    ),
)
async def send(eve):
    name = (eve.data_match.group(1)).decode("UTF-8")
    thumb = ""
    for m in choices(sorted(glob("resources/extras/*.jpg"))):
        thumb += m
    if name.startswith("def"):
        plug_name = name.replace(f"def_plugin_", "")
        plugin = f"plugins/{plug_name}.py"
        buttons = [
            [
                Button.inline(
                    "« Paste »",
                    data=f"pasta-{plugin}",
                )
            ],
            [
                Button.inline("« Back", data="back"),
                Button.inline("Close", data="close"),
            ],
        ]
    else:
        plug_name = name.replace(f"add_plugin_", "")
        plugin = f"addons/{plug_name}.py"
        buttons = [
            [
                Button.inline(
                    "« Paste »",
                    data=f"pasta-{plugin}",
                )
            ],
            [
                Button.inline("« Back", data="buck"),
                Button.inline("Close", data="close"),
            ],
        ]
    await eve.edit(file=plugin, thumb=thumb, buttons=buttons)


@callback("updatenow")
@owner
async def update(eve):
    repo = Repo()
    ac_br = repo.active_branch
    ups_rem = repo.remote("upstream")
    if Var.HEROKU_API:
        import heroku3

        try:
            heroku = heroku3.from_key(Var.HEROKU_API)
            heroku_app = None
            heroku_applications = heroku.apps()
        except BaseException:
            return await eve.edit("`Wrong HEROKU_API.`")
        for app in heroku_applications:
            if app.name == Var.HEROKU_APP_NAME:
                heroku_app = app
        if not heroku_app:
            await eve.edit("`Wrong HEROKU_APP_NAME.`")
            repo.__del__()
            return
        await eve.edit(
            "`Userbot dyno build in progress, please wait for it to complete.`"
        )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + Var.HEROKU_API + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eve.edit(f"`Here is the error log:\n{error}`")
            repo.__del__()
            return
        await eve.edit("`Successfully Updated!\nRestarting, please wait...`")
    else:
        await eve.edit(
            "`Userbot dyno build in progress, please wait for it to complete.`"
        )
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await updateme_requirements()
        await eve.edit(
            "`Successfully Updated!\nBot is restarting... Wait for a second!`"
        )
        execl(sys.executable, sys.executable, "-m", "pyUltroid")


@callback("changes")
@owner
async def changes(okk):
    repo = Repo.init()
    ac_br = repo.active_branch
    changelog, tl_chnglog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    changelog_str = changelog + f"\n\nClick the below button to update!"
    if len(changelog_str) > 1024:
        await okk.edit(get_string("upd_4"))
        await asyncio.sleep(2)
        with open(f"ultroid_updates.txt", "w+") as file:
            file.write(tl_chnglog)
        await okk.edit(
            get_string("upd_5"),
            file="ultroid_updates.txt",
            buttons=Button.inline("Update Now ⏬", data="updatenow"),
        )
        remove(f"ultroid_updates.txt")
        return
    else:
        await okk.edit(
            changelog_str,
            buttons=Button.inline("Update Now ⏬", data="updatenow"),
            parse_mode="html",
        )


@callback(
    re.compile(
        "pasta-(.*)",
    ),
)
@owner
async def _(e):
    ok = (e.data_match.group(1)).decode("UTF-8")
    with open(ok, "r") as hmm:
        _, key = get_paste(hmm.read())
    if _ == "dog":
        link = "https://del.dog/" + key
        raw = "https://del.dog/raw/" + key
    else:
        link = "https://nekobin.com/" + key
        raw = "https://nekobin.com/raw/" + key
    if ok.startswith("plugins"):
        buttons = [
            Button.inline("« Back", data="back"),
            Button.inline("Close", data="close"),
        ]
    else:
        buttons = [
            Button.inline("« Back", data="buck"),
            Button.inline("Close", data="close"),
        ]
    await e.edit(
        f"<strong>Pasted\n     👉<a href={link}>[Link]</a>\n     👉<a href={raw}>[Raw Link]</a></strong>",
        buttons=buttons,
        link_preview=False,
        parse_mode="html",
    )


@callback("authorise")
@owner
async def _(e):
    if not e.is_private:
        return
    if not udB.get("GDRIVE_CLIENT_ID"):
        return await e.edit(
            "Client ID and Secret is Empty.\nFill it First.",
            buttons=Button.inline("Back", data="gdrive"),
        )
    storage = await create_token_file(TOKEN_FILE, e)
    authorize(TOKEN_FILE, storage)
    f = open(TOKEN_FILE)
    token_file_data = f.read()
    udB.set("GDRIVE_TOKEN", token_file_data)
    await e.reply(
        "`Success!\nYou are all set to use Google Drive with Violet Userbot.`",
        buttons=Button.inline("Main Menu", data="setter"),
    )


@callback("folderid")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Send your FOLDER ID\n\n"
        + "For FOLDER ID:\n"
        + "1. Open Google Drive App.\n"
        + "2. Create Folder.\n"
        + "3. Make that folder public.\n"
        + "4. Copy link of that folder.\n"
        + "5. Send all characters which is after id= .",
    )
    async with asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_FOLDER_ID", repl.text)
        await repl.reply(
            "Success Now You Can Authorise.",
            buttons=get_back_button("gdrive"),
        )


@callback("clientsec")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit("Send your CLIENT SECRET")
    async with asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_CLIENT_SECRET", repl.text)
        await repl.reply(
            "Success!\nNow You Can Authorise or add FOLDER ID.",
            buttons=get_back_button("gdrive"),
        )


@callback("clientid")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit("Send your CLIENT ID ending with .com")
    async with asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        if not repl.text.endswith(".com"):
            return await repl.reply("`Wrong CLIENT ID`")
        udB.set("GDRIVE_CLIENT_ID", repl.text)
        await repl.reply(
            "Success now set CLIENT SECRET",
            buttons=get_back_button("gdrive"),
        )


@callback("gdrive")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Go [here](https://console.developers.google.com/flows/enableapi?apiid=drive) and get your CLIENT ID and CLIENT SECRET",
        buttons=[
            [
                Button.inline("Client ID", data="clientid"),
                Button.inline("Client Secret", data="clientsec"),
            ],
            [
                Button.inline("Folder ID", data="folderid"),
                Button.inline("Authorise", data="authorise"),
            ],
            [Button.inline("« Back", data="otvars")],
        ],
        link_preview=False,
    )


@callback("otvars")
@owner
async def otvaar(event):
    await event.edit(
        "Other Variables to set for @TheUltroid:",
        buttons=[
            [
                Button.inline("📡 Tag Logger", data="taglog"),
                Button.inline("🪓 FBan", data="sfban"),
            ],
            [
                Button.inline("📟 Sudo Mode", data="sudo"),
                Button.inline("⚖️ Handler", data="hhndlr"),
            ],
            [
                Button.inline("🛍 Extra Plugins", data="plg"),
                Button.inline("📲 Addons", data="eaddon"),
            ],
            [
                Button.inline("😃 Emoji in Help", data="emoj"),
                Button.inline("🔩 Set GDrive", data="gdrive"),
            ],
            [Button.inline("🖼 Inline Pic", data="inli_pic")],
            [Button.inline("« Back", data="setter")],
        ],
    )


@callback("emoj")
@owner
async def emoji(event):
    await event.delete()
    pru = event.sender_id
    var = "EMOJI_IN_HELP"
    name = f"Emoji in `{HNDLR}help` menu"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("Send emoji u want to set 🙃.\n\nUse /cancel to cancel.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message(
                "Incorrect Emoji",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}\n",
                buttons=get_back_button("otvars"),
            )


@callback("plg")
@owner
async def pluginch(event):
    await event.delete()
    pru = event.sender_id
    var = "PLUGIN_CHANNEL"
    name = "Plugin Channel"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Send id or username of a channel from where u want to install all plugins\n\nOur Channel~ @ultroidplugins\n\nUse /cancel to cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message(
                "Incorrect channel",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n After setting everything, do `.restart`".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("otvars"),
            )


@callback("hhndlr")
@owner
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "HNDLR"
    name = "Handler/ Trigger"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Send The Symbol Which u want as Handler/Trigger to use bot\nUr Current Handler is [ `{HNDLR}` ]\n\n use /cancel to cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        elif len(themssg) > 1:
            return await conv.send_message(
                "Incorrect Handler",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            return await conv.send_message(
                "This cannot be used as handler",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("otvars"),
            )


@callback("taglog")
@owner
async def tagloggrr(e):
    await e.edit(
        "Choose Options",
        buttons=[
            [Button.inline("SET TAG LOG", data="settag")],
            [Button.inline("DELETE TAG LOG", data="deltag")],
            [Button.inline("« Back", data="otvars")],
        ],
    )


@callback("deltag")
@owner
async def delfuk(e):
    udB.delete("TAG_LOG")
    await e.answer("Done!!! Tag Log Off")


@callback("settag")
@owner
async def taglogerr(event):
    await event.delete()
    pru = event.sender_id
    var = "TAG_LOG"
    name = "Tag Log Group"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Make a group, add your assistant and make it admin.\nGet the `{hndlr}id` of that group and send it here for tag logs.\n\nUse /cancel to cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("taglog"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("taglog"),
            )


@callback("eaddon")
@owner
async def pmset(event):
    await event.edit(
        "ADDONS~ Extra Plugins:",
        buttons=[
            [Button.inline("Addons  On ✅", data="edon")],
            [Button.inline("Addons  Off ❌", data="edof")],
            [Button.inline("« Back", data="otvars")],
        ],
    )


@callback("edon")
@owner
async def eddon(event):
    var = "ADDONS"
    await setit(event, var, "True")
    await event.edit(
        "Done! ADDONS has been turned on!!\n\nAfter setting everything, do `.restart`",
        buttons=get_back_button("eaddon"),
    )


@callback("edof")
@owner
async def eddof(event):
    var = "ADDONS"
    await setit(event, var, "False")
    await event.edit(
        "Done! ADDONS has been turned off!!\n\nAfter setting everything, do `.restart`",
        buttons=get_back_button("eaddon"),
    )


@callback("sudo")
@owner
async def pmset(event):
    await event.edit(
        f"SUDO MODE ~ This will allow sudo users to use your bot. To know more use `{HNDLR}help sudo`",
        buttons=[
            [Button.inline("Sudo Mode  On ✅", data="onsudo")],
            [Button.inline("Sudo Mode  Off ❌", data="ofsudo")],
            [Button.inline("« Back", data="otvars")],
        ],
    )


@callback("onsudo")
@owner
async def eddon(event):
    var = "SUDO"
    await setit(event, var, "True")
    await event.edit(
        "SUDO MODE has been turned on!\n\nAfter setting everything, do `.restart`",
        buttons=get_back_button("sudo"),
    )


@callback("ofsudo")
@owner
async def eddof(event):
    var = "SUDO"
    await setit(event, var, "False")
    await event.edit(
        "SUDO MODE has been turned off!\n\nAfter setting everything, do `.restart`",
        buttons=get_back_button("sudo"),
    )


@callback("sfban")
@owner
async def sfban(event):
    await event.edit(
        "FBan Settings:",
        buttons=[
            [Button.inline("FBan Group 🆔", data="sfgrp")],
            [Button.inline("Exclude Feds 🚫", data="sfexf")],
            [Button.inline("« Back", data="otvars")],
        ],
    )


@callback("sfgrp")
@owner
async def sfgrp(event):
    await event.delete()
    name = "FBan Group ID"
    var = "FBAN_GROUP_ID"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Make a group, add @MissRose_Bot, send `{hndlr}id`, copy that and send it here.\nUse /cancel to go back.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("sfban"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("sfban"),
            )


@callback("sfexf")
@owner
async def sfexf(event):
    await event.delete()
    name = "Excluded Feds"
    var = "EXCLUDE_FED"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Send the Fed IDs you want to exclude in the ban. Split by a space.\neg`id1 id2 id3`\nSet is as `None` if you dont want any.\nUse /cancel to go back.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("sfban"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}",
                buttons=get_back_button("sfban"),
            )


@callback("alvcstm")
@owner
async def alvcs(event):
    await event.edit(
        f"Customise your `{HNDLR}alive`. Choose from the below options -",
        buttons=[
            [Button.inline("📝 Alive Text", data="alvtx")],
            [Button.inline("🏞 Alive Media", data="alvmed")],
            [Button.inline("❌ Delete Alive Media", data="delmed")],
            [Button.inline("« Back", data="setter")],
        ],
    )


@callback("alvtx")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_TEXT"
    name = "Alive Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Text**\nEnter the new alive text.\n\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("alvcstm"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nAfter setting everything, do `.restart`".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("alvcstm"),
            )


@callback("alvmed")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_PIC"
    name = "Alive Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Media**\nSend me a pic/gif/bot api id of sticker to set as alive media.\n\nUse /cancel to terminate the operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation cancelled!!",
                    buttons=get_back_button("alvcstm"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "alvpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("alvcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} has been set.",
            buttons=get_back_button("alvcstm"),
        )


@callback("delmed")
@owner
async def dell(event):
    try:
        udB.delete("ALIVE_PIC")
        return await event.edit("Done!", buttons=get_back_button("alvcstm"))
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=get_back_button("alvcstm"),
        )


@callback("pmcstm")
@owner
async def alvcs(event):
    await event.edit(
        "Customise your PMPERMIT Settings -",
        buttons=[
            [
                Button.inline("🖋 PM Text", data="pmtxt"),
                Button.inline("🌄 PM Media", data="pmmed"),
            ],
            [
                Button.inline("✅ Auto Approve", data="apauto"),
                Button.inline("📬 PMLOGGER", data="pml"),
            ],
            [
                Button.inline("🧮 Set Warns", data="swarn"),
                Button.inline("❌ Delete PM Media", data="delpmmed"),
            ],
            [Button.inline("↕️ PMPermit Type", data="pmtype")],
            [Button.inline("« Back", data="ppmset")],
        ],
    )


@callback("pmtype")
@owner
async def pmtyp(event):
    await event.edit(
        "Select the type of PMPermit needed.",
        buttons=[
            [Button.inline("Inline 🧩", data="inpm_in")],
            [Button.inline("Normal", data="inpm_no")],
            [Button.inline("« Back", data="pmcstm")],
        ],
    )


@callback("inpm_in")
@owner
async def inl_on(event):
    var = "INLINE_PM"
    await setit(event, var, "True")
    await event.edit(
        f"Done!! PMPermit type has been set to inline!",
        buttons=[[Button.inline("« Back", data="pmtype")]],
    )


@callback("inpm_no")
@owner
async def inl_on(event):
    var = "INLINE_PM"
    await setit(event, var, "False")
    await event.edit(
        f"Done!! PMPermit type has been set to normal!",
        buttons=[[Button.inline("« Back", data="pmtype")]],
    )


@callback("pmtxt")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "PM_TEXT"
    name = "PM Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Text**\nEnter the new PMPermit text.\n\nYou can use `{name}` `{fullname}` `{count}` `{mention}` `{username}` to get this from user Too\n\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("pmcstm"),
            )
        else:
            if len(themssg) > 4090:
                return await conv.send_message(
                    "Message too long!\nGive a shorter message please!",
                    buttons=get_back_button("pmcstm"),
                )
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nAfter setting everything, do `.restart`".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("pmcstm"),
            )


@callback("swarn")
@owner
async def name(event):
    m = range(1, 10)
    tultd = [Button.inline(f"{x}", data=f"wrns_{x}") for x in m]
    lst = list(zip(tultd[::3], tultd[1::3], tultd[2::3]))
    lst.append([Button.inline("« Back", data="pmcstm")])
    await event.edit(
        "Select the number of warnings for a user before getting blocked in PMs.",
        buttons=lst,
    )


@callback(re.compile(b"wrns_(.*)"))
@owner
async def set_wrns(event):
    value = int(event.data_match.group(1).decode("UTF-8"))
    dn = udB.set("PMWARNS", value)
    if dn:
        await event.edit(
            f"PM Warns Set to {value}.\nNew users will have {value} chances in PMs before getting banned.",
            buttons=get_back_button("pmcstm"),
        )
    else:
        await event.edit(
            f"Something went wrong, please check your {hndlr}logs!",
            buttons=get_back_button("pmcstm"),
        )


@callback("pmmed")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "PMPIC"
    name = "PM Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Media**\nSend me a pic/gif/ or link  to set as pmpermit media.\n\nUse /cancel to terminate the operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation cancelled!!",
                    buttons=get_back_button("pmcstm"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "pmpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("pmcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} has been set.",
            buttons=get_back_button("pmcstm"),
        )


@callback("delpmmed")
@owner
async def dell(event):
    try:
        udB.delete("PMPIC")
        return await event.edit("Done!", buttons=get_back_button("pmcstm"))
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=[[Button.inline("« Settings", data="setter")]],
        )


@callback("apauto")
@owner
async def apauto(event):
    await event.edit(
        "This'll auto approve on outgoing messages",
        buttons=[
            [Button.inline("Auto Approve ON ✅", data="apon")],
            [Button.inline("Auto Approve OFF ❌", data="apof")],
            [Button.inline("« Back", data="pmcstm")],
        ],
    )


@callback("apon")
@owner
async def apon(event):
    var = "AUTOAPPROVE"
    await setit(event, var, "True")
    await event.edit(
        f"Done!! AUTOAPPROVE  Started!!",
        buttons=[[Button.inline("« Back", data="apauto")]],
    )


@callback("apof")
@owner
async def apof(event):
    try:
        udB.delete("AUTOAPPROVE")
        return await event.edit(
            "Done! AUTOAPPROVE Stopped!!",
            buttons=[[Button.inline("« Back", data="apauto")]],
        )
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=[[Button.inline("« Settings", data="setter")]],
        )


@callback("pml")
@owner
async def alvcs(event):
    await event.edit(
        "PMLOGGER This Will Forward Ur Pm to Ur Private Group -",
        buttons=[
            [Button.inline("PMLOGGER ON", data="pmlog")],
            [Button.inline("PMLOGGER OFF", data="pmlogof")],
            [Button.inline("« Back", data="pmcstm")],
        ],
    )


@callback("pmlog")
@owner
async def pmlog(event):
    var = "PMLOG"
    await setit(event, var, "True")
    await event.edit(
        f"Done!! PMLOGGER  Started!!",
        buttons=[[Button.inline("« Back", data="pml")]],
    )


@callback("pmlogof")
@owner
async def pmlogof(event):
    try:
        udB.delete("PMLOG")
        return await event.edit(
            "Done! PMLOGGER Stopped!!",
            buttons=[[Button.inline("« Back", data="pml")]],
        )
    except BaseException:
        return await event.edit(
            "Something went wrong...",
            buttons=[[Button.inline("« Settings", data="setter")]],
        )


@callback("ppmset")
@owner
async def pmset(event):
    await event.edit(
        "PMPermit Settings:",
        buttons=[
            [Button.inline("Turn PMPermit On ✅", data="pmon")],
            [Button.inline("Turn PMPermit Off ❌", data="pmoff")],
            [Button.inline("Customize PMPermit ✏️", data="pmcstm")],
            [Button.inline("« Back", data="setter")],
        ],
    )


@callback("pmon")
@owner
async def pmonn(event):
    var = "PMSETTING"
    await setit(event, var, "True")
    await event.edit(
        f"Done! PMPermit has been turned on!",
        buttons=[[Button.inline("« Back", data="ppmset")]],
    )


@callback("pmoff")
@owner
async def pmofff(event):
    var = "PMSETTING"
    await setit(event, var, "False")
    await event.edit(
        f"Done! PMPermit has been turned off!",
        buttons=[[Button.inline("« Back", data="ppmset")]],
    )


@callback("chatbot")
@owner
async def chbot(event):
    await event.edit(
        f"You can use your Assistant Bot to chat with people!.\n[More info](https://t.me/UltroidUpdates/2)",
        buttons=[
            [Button.inline("Chat Bot  On ✅", data="onchbot")],
            [Button.inline("Chat Bot  Off ❌", data="ofchbot")],
            [Button.inline("Bot Welcome", data="bwel")],
            [Button.inline("« Back", data="setter")],
        ],
        link_preview=False,
    )


@callback("bwel")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "STARTMSG"
    name = "Bot Welcome Message:"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**BOT WELCOME MSG**\nEnter the message which you want to show when someone start your assistant Bot.\nYou Can use `{me}` , `{mention}` Parameters Too\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("chatbot"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("chatbot"),
            )


@callback("onchbot")
@owner
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "True")
    await event.edit(
        "Done! Now you can chat with people via your bot.",
        buttons=[Button.inline("« Back", data="chatbot")],
    )


@callback("ofchbot")
@owner
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "False")
    await event.edit(
        "Done! Chat People Via This Bot Stopped.",
        buttons=[Button.inline("« Back", data="chatbot")],
    )


@callback("vcb")
@owner
async def vcb(event):
    await event.edit(
        f"From this feature you can play songs on voice chat.\n\n[moreinfo](https://t.me/UltroidUpdates/4)",
        buttons=[
            [Button.inline("VC Session", data="vcs")],
            [Button.inline("« Back", data="setter")],
        ],
        link_preview=False,
    )


@callback("vcs")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "VC_SESSION"
    name = "VC SESSION"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Vc session**\nEnter the New session u generated for vc bot.\n\nUse /cancel to terminate the operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("vcb"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nAfter setting everything, do `.restart`".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("vcb"),
            )


@callback("inli_pic")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "INLINE_PIC"
    name = "Inline Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Inline Media**\nSend me a pic/gif/ or link  to set as inline media.\n\nUse /cancel to terminate the operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation cancelled!!",
                    buttons=get_back_button("setter"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "inlpic")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("setter"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} has been set.",
            buttons=get_back_button("setter"),
        )
