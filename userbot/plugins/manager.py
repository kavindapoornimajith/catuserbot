"""Notification Manager for @UniBorg
"""

import asyncio
import io
import userbot.plugins.sql_helper.no_log_pms_sql as no_log_pms_sql
import userbot.plugins.sql_helper.pmpermit_sql as pmpermit_sql
from telethon import events, errors, functions, types
from userbot.utils import admin_cmd


PM_WARNS = {}
PREV_REPLY_MESSAGE = {}
CACHE = {}

BAALAJI_TG_USER_BOT = "My Master hasn't approved you to PM."
TG_COMPANION_USER_BOT = "Please wait for his response and don't spam his PM."
UNIBORG_USER_BOT_WARN_ZERO = "I am currently offline. Please do not SPAM me."
UNIBORG_USER_BOT_NO_WARN = "Hi! I will answer to your message soon. Please wait for my response and don't spam my PM. Thanks"





@borg.on(admin_cmd(pattern="nccreatedch"))
async def create_dump_channel(event):
    if Config.PM_LOGGR_BOT_API_ID is None:
        result = await event.client(functions.channels.CreateChannelRequest(  # pylint:disable=E0602
            title=f"Userbot-{borg.uid}-PM_LOGGR_BOT_API_ID-data",
            about="userbot PM_LOGGR_BOT_API_ID // Do Not Touch",
            megagroup=False
        ))
        logger.info(result)
        created_chat_id = result.chats[0].id
        result = await event.client.edit_admin(  # pylint:disable=E0602
            entity=created_chat_id,
            user=Config.TG_BOT_USER_NAME_BF_HER,
            is_admin=True,
            title="Editor"
        )
        logger.info(result)
        with io.BytesIO(str.encode(str(created_chat_id))) as out_file:
            out_file.name = "PLEASE.IGNORE.dummy.file"
            await event.client.send_file(
                created_chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=f"Please set `PM_LOGGR_BOT_API_ID` to `{created_chat_id}`",
                reply_to=1
            )
        await event.delete()
    else:
        await event.edit(f"**is configured**. [please do not touch](https://t.me/c/{Config.PM_LOGGR_BOT_API_ID}/2)")


@borg.on(admin_cmd(pattern="nolog ?(.*)"))
async def set_no_log_p_m(event):
    if Config.PM_LOGGR_BOT_API_ID is not None:
        reason = event.pattern_match.group(1)
        chat = await event.get_chat()
        if event.is_private:
            if not no_log_pms_sql.is_approved(chat.id):
                no_log_pms_sql.approve(chat.id)
                await event.edit("Won't Log Messages from this chat")
                await asyncio.sleep(3)
                await event.delete()


@borg.on(admin_cmd(pattern="dellog ?(.*)"))
async def set_no_log_p_m(event):
    if Config.PM_LOGGR_BOT_API_ID is not None:
        reason = event.pattern_match.group(1)
        chat = await event.get_chat()
        if event.is_private:
            if no_log_pms_sql.is_approved(chat.id):
                no_log_pms_sql.disapprove(chat.id)
                await event.edit("Will Log Messages from this chat")
                await asyncio.sleep(3)
                await event.delete()



@borg.on(events.NewMessage(incoming=True))
async def on_new_private_message(event):
    if Config.PM_LOGGR_BOT_API_ID is None:
        return

    if not event.is_private:
        return

    message_text = event.message.message
    message_media = event.message.media
    message_id = event.message.id
    message_to_id = event.message.to_id
    chat_id = event.chat_id
    # logger.info(chat_id)

    current_message_text = message_text.lower()
    if BAALAJI_TG_USER_BOT in current_message_text or \
        TG_COMPANION_USER_BOT in current_message_text or \
        UNIBORG_USER_BOT_NO_WARN in current_message_text:
        # userbot's should not reply to other userbot's
        # https://core.telegram.org/bots/faq#why-doesn-39t-my-bot-see-messages-from-other-bots
        return

        if event.from_id in CACHE:
            sender = CACHE[event.from_id]
        else:
            sender = await bot.get_entity(event.from_id)
            CACHE[event.from_id] = sender
            
    if chat_id == borg.uid:
        # don't log Saved Messages
        return
    if sender.bot:
        # don't log bots
        return
    if sender.verified:
        # don't log verified accounts
        return


    if not no_log_pms_sql.is_approved(chat_id):
        # log pms
        await do_log_pm_action(chat_id, event, message_text, message_media)


@borg.on(events.ChatAction(blacklist_chats=Config.UB_BLACK_LIST_CHAT))
async def on_new_chat_action_message(event):
    if Config.PM_LOGGR_BOT_API_ID is None:
        return
    # logger.info(event.stringify())
    chat_id = event.chat_id
    message_id = event.action_message.id

    if event.created or event.user_added:
        added_by_users = event.action_message.action.users
        if borg.uid in added_by_users:
            added_by_user = event.action_message.from_id
            # someone added me to chat
            the_message = ""
            the_message += "#MessageActionChatAddUser\n\n"
            the_message += f"[User](tg://user?id={added_by_user}): `{added_by_user}`\n"
            the_message += f"[Private Link](https://t.me/c/{chat_id}/{message_id})\n"
            await event.client.send_message(
                entity=Config.PM_LOGGR_BOT_API_ID,
                message=the_message,
                # reply_to=,
                # parse_mode="html",
                link_preview=False,
                # file=message_media,
                silent=True
            )


@borg.on(events.Raw())
async def on_new_channel_message(event):
    if Config.PM_LOGGR_BOT_API_ID is None:
        return
    try:
        if tgbot is None:
            return
    except Exception as e:
        logger.info(str(e))
        return
    # logger.info(event.stringify())
    if isinstance(event, types.UpdateChannel):
        channel_id = event.channel_id
        message_id = 2
        # someone added me to channel
        # TODO: https://t.me/TelethonChat/153947
        the_message = ""
        the_message += "#MessageActionChatAddUser\n\n"
        # the_message += f"[User](tg://user?id={added_by_user}): `{added_by_user}`\n"
        the_message += f"[Private Link](https://t.me/c/{channel_id}/{message_id})\n"
        await borg.send_message(
            entity=Config.PM_LOGGR_BOT_API_ID,
            message=the_message,
            # reply_to=,
            # parse_mode="html",
            link_preview=False,
            # file=message_media,
            silent=True
        )





async def do_pm_permit_action(chat_id, event):
    if chat_id not in PM_WARNS:
        PM_WARNS.update({chat_id: 0})
    if PM_WARNS[chat_id] == Config.MAX_FLOOD_IN_P_M_s:
        r = await event.reply(UNIBORG_USER_BOT_WARN_ZERO)
        await asyncio.sleep(3)
        await event.client(functions.contacts.BlockRequest(chat_id))
        if chat_id in PREV_REPLY_MESSAGE:
            await PREV_REPLY_MESSAGE[chat_id].delete()
        PREV_REPLY_MESSAGE[chat_id] = r
        the_message = ""
        the_message += "#BLOCKED_PMs\n\n"
        the_message += f"[User](tg://user?id={chat_id}): {chat_id}\n"
        the_message += f"Message Count: {PM_WARNS[chat_id]}\n"
        # the_message += f"Media: {message_media}"
        await event.client.send_message(
            entity=Config.PM_LOGGR_BOT_API_ID,
            message=the_message,
            # reply_to=,
            # parse_mode="html",
            link_preview=False,
            # file=message_media,
            silent=True
        )
        return
    r = await event.reply(UNIBORG_USER_BOT_NO_WARN)
    PM_WARNS[chat_id] += 1
    if chat_id in PREV_REPLY_MESSAGE:
        await PREV_REPLY_MESSAGE[chat_id].delete()
    PREV_REPLY_MESSAGE[chat_id] = r


async def do_log_pm_action(chat_id, event, message_text, message_media):
    the_message = ""
    the_message += "#LOG_PMs\n\n"
    the_message += f"[User](tg://user?id={chat_id}): {chat_id}\n"
    the_message += f"Message: {message_text}\n"
    # the_message += f"Media: {message_media}"
    await event.client.send_message(
        entity=Config.PM_LOGGR_BOT_API_ID,
        message=the_message,
        # reply_to=,
        # parse_mode="html",
        link_preview=False,
        file=message_media,
        silent=True
    )