import disnake
from asyncio import sleep, create_task
from disnake import Embed
from loguru import logger

from bot.data.pufflebot.user import User, PenguinIntegrations
from bot.events import event
from bot.misc.constants import emojiCoin
from bot.misc.penguin import Penguin
from bot.misc.utils import get_penguin_or_none_from_user_id


@event.on("boot")
async def setup(server):
    global bot
    bot = server.bot
    create_task(check_membership())
    logger.info(f'Loaded notification system')


async def check_membership():
    while True:
        await sleep(86_400)  # 24 hours
        for user in await User.query.gino.all():
            p = await get_penguin_or_none_from_user_id(user.id)

            if p.membership_days_remain == 0:
                await notify_membership_ended(user.id)
                continue
            if 0 < p.membership_days_remain < 6 and not p.membership_expires_aware:
                await notify_membership_soon_ended(user.id)
                continue


async def notify_coins_receive(sender_penguin: Penguin, receiver_penguin: Penguin, coins: int, message: str = None,
                               command: str = None):
    user_id, = await PenguinIntegrations.select("discord_id").where(
        PenguinIntegrations.penguin_id == receiver_penguin.id).gino.first()
    if user_id is None:
        return
    user: disnake.User = await bot.get_or_fetch_user(int(user_id))
    sender_user_id, = await User.select("id").where(User.penguin_id == sender_penguin.id).gino.first()
    lang = (await user.db).language
    if not (await user.db).enabled_coins_notify:
        return

    embed = Embed(color=0xB7F360,
                  title=bot.i18n.get("NOTIFY_COINS_RECEIVE")[lang].
                  replace("%nickname%", sender_penguin.safe_name()).replace("%coins%", str(coins)))
    embed.set_thumbnail(f"https://play.cpps.app/avatar/{receiver_penguin.id}/cp?size=600")
    if message:
        embed.add_field(bot.i18n.get("MESSAGE")[lang], message, inline=False)

    if command == "fundraising":
        command_value = "</fundraising:1133131135539494962>"
    elif command == "pay2":
        command_value = "</pay2:1129711949576409188>"
    elif command == "pay":
        command_value = "</pay:1099629339110289445>"
    else:
        command_value = "undefined"

    embed.add_field(bot.i18n.get("COMMAND")[lang], command_value, inline=False)
    embed.add_field(bot.i18n.get("BALANCE")[lang], f"{receiver_penguin.coins} {emojiCoin}", inline=False)
    embed.add_field(bot.i18n.get("USER")[lang], f"<@{sender_user_id}>", inline=False)
    embed.set_footer(text=bot.i18n.get("YOUR_PENGUIN")[lang].replace("%nickname%", receiver_penguin.safe_name()))
    await send_notify(user, embed)


async def notify_membership_ended(user_id: int):
    from bot.handlers.button import MembershipButton
    user: disnake.User = await bot.get_or_fetch_user(int(user_id))
    p = await user.penguin
    lang = (await user.db).language
    if not (await user.db).enabled_membership_notify:
        return

    embed = Embed(color=0xFFD947, title=bot.i18n.get("MEMBERSHIP_ENDED_TITLE")[lang])
    embed.set_thumbnail(f"https://play.cpps.app/avatar/{p.id}/cp?size=600")
    embed.set_footer(text=bot.i18n.get("YOUR_PENGUIN")[lang].replace("%nickname%", p.safe_name()))
    embed.set_image(url="https://cpps.app/NO%20MEMBERSHIP.png")

    await send_notify(user, embed, view=MembershipButton(lang))


async def notify_gift_coins(user: disnake.User, p: Penguin, coins: int):
    lang = (await user.db).language
    if not (await user.db).enabled_coins_notify:
        return

    embed = Embed(colour=0xB7F360, title=bot.i18n.get("NOTIFY_GIFT_COINS")[lang].replace("%coins%", str(coins)))
    embed.set_thumbnail(f"https://play.cpps.app/avatar/{p.id}/cp?size=600")
    embed.add_field(bot.i18n.get("BALANCE")[lang], f"{p.coins} {emojiCoin}", inline=False)
    embed.set_footer(text=bot.i18n.get("YOUR_PENGUIN")[lang].replace("%nickname%", p.safe_name()))
    await send_notify(user, embed)


async def notify_membership_soon_ended(user_id: int):
    from bot.handlers.button import MembershipButton
    user = await bot.get_or_fetch_user(int(user_id))
    p = await user.penguin
    lang = (await user.db).language
    if not (await user.db).enabled_membership_notify:
        return

    embed = Embed(color=0xFFD947, title=bot.i18n.get("MEMBERSHIP_SOON_ENDED_TITLE")[lang],
                  description=bot.i18n.get("MEMBERSHIP_SOON_ENDED_DESCRIPTION")[lang])
    embed.set_thumbnail(f"https://play.cpps.app/avatar/{p.id}/cp?size=600")
    embed.add_field(bot.i18n.get("UNTIL_END_OF_MEMBERSHIP")[lang],
                    f"{p.membership_days_remain} {bot.i18n.get('DAYS')[lang]}", inline=False)
    embed.set_footer(text=bot.i18n.get("YOUR_PENGUIN")[lang].replace("%nickname%", p.safe_name()))

    await send_notify(user, embed, view=MembershipButton(lang))


async def send_notify(user: disnake.User, embed, *, view=None):
    if (await user.db).enabled_notify:
        await user.send(embed=embed, view=view)
