import disnake
from asyncio import sleep, create_task
from disnake import Embed
from loguru import logger

from bot.data.pufflebot.user import User, PenguinIntegrations
from bot.handlers import boot
from bot.misc.constants import emojiCoin
from bot.misc.penguin import Penguin
from bot.misc.utils import getPenguinOrNoneFromUserId


@boot
async def setup(server):
    global bot
    bot = server.bot
    create_task(check_membership())
    logger.info(f'Loaded notification system')


async def check_membership():
    while True:
        await sleep(86_400)  # 24 hours
        for user in await User.query.gino.all():
            p = await getPenguinOrNoneFromUserId(user.id, cache=False)

            if p.membership_days_remain == 0:
                await notifyMembershipEnded(p)
                continue
            if 0 < p.membership_days_remain < 6 and not p.membership_expires_aware:
                await notifyMembershipSoonEnded(p)
                continue


async def notifyCoinsReceive(senderPenguin: Penguin, receiverPenguin: Penguin, coins, message=None, command=None):
    receiverId = await PenguinIntegrations.select("discord_id").where(
        PenguinIntegrations.penguin_id == receiverPenguin.id).gino.first()
    receiver = await bot.fetch_user(int(receiverId[0]))
    senderId = await User.select("id").where(User.penguin_id == senderPenguin.id).gino.first()
    sender = await bot.fetch_user(int(senderId[0]))
    user = await User.get(receiver.id)
    if not user.enabled_coins_notify:
        return

    embed = Embed(color=0xB7F360, title=f"Пингвин под ником «{senderPenguin.safe_name()}» перевел(а) Вам {coins}м")
    embed.set_thumbnail(f"https://play.cpps.app/avatar/{receiverPenguin.id}/cp?size=600")
    if message:
        embed.add_field("Сообщение", message, inline=False)
    if command == "fundraising":
        embed.add_field("Команда", "</fundraising:1133131135539494962>", inline=False)
    if command == "pay2":
        embed.add_field("Команда", "</pay2:1129711949576409188>", inline=False)
    else:
        embed.add_field("Команда", "</pay:1099629339110289445>", inline=False)
    embed.add_field("Баланс", f"{receiverPenguin.coins} {emojiCoin}", inline=False)
    embed.add_field("Пользователь", f"{sender.mention}", inline=False)
    embed.set_footer(text=f"Ваш аккаунт: {receiverPenguin.safe_name()}")
    await sendNotify(receiver, embed)


async def notifyMembershipEnded(p: Penguin):
    user = await User.query.where(User.penguin_id == p.id).gino.first()
    if not user.enabled_membership_notify:
        return

    embed = Embed(color=0xFFD947, title=f"Подписка закончилась")
    embed.set_footer(text=f"Аккаунт: {p.safe_name()}",
                     icon_url=f"https://play.cpps.app/avatar/{p.id}/cp?size=600")
    embed.set_image(url="https://cpps.app/NO%20MEMBERSHIP.png")

    await sendNotify(await bot.fetch_user(user.id), embed, view=MembershipButton())


async def notifyMembershipSoonEnded(p: Penguin):
    user = await User.query.where(User.penguin_id == p.id).gino.first()
    if not user.enabled_membership_notify:
        return

    embed = Embed(color=0xFFD947, title=f"Подписка скоро закончится",
                  description="Войдите в игру, что бы больше не получать напоминания")
    embed.add_field("До конца подписки", f"{p.membership_days_remain} дней", inline=False)
    embed.set_footer(text=f"Аккаунт: {p.safe_name()}",
                     icon_url=f"https://play.cpps.app/avatar/{p.id}/cp?size=600")

    await sendNotify(await bot.fetch_user(user.id), embed, view=MembershipButton())


async def sendNotify(user: disnake.User, embed, *, view=None):
    if (await User.get(user.id)).enabled_notify:
        await user.send(embed=embed, view=view)


class MembershipButton(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Приобрести подписку", style=disnake.ButtonStyle.link,
                       url="https://cpps.app/membership")
    async def buyMembership(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...
