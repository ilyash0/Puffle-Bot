import disnake
from disnake import Embed
from loguru import logger

from bot.data.pufflebot.users import Users
from bot.handlers import boot
from bot.misc.penguin import Penguin


@boot
async def setup(server):
    global bot
    bot = server.bot
    logger.info(f'Loaded notification system')


async def notifyCoinsReceive(senderPenguin: Penguin, receiverPenguin: Penguin, coins, message=None):
    receiverId = await Users.select("id").where(Users.penguin_id == receiverPenguin.id).gino.first()
    receiver = await bot.fetch_user(int(receiverId[0]))
    senderId = await Users.select("id").where(Users.penguin_id == senderPenguin.id).gino.first()
    sender = await bot.fetch_user(int(senderId[0]))

    embed = Embed(color=0xB7F360, title=f"{sender} перевел(а) Вам {coins}м")
    if message:
        embed.add_field("Сообщение", message, inline=False)
    embed.add_field("Баланс", receiverPenguin.coins, inline=False)
    embed.set_footer(text=f"Ваш аккаунт: {receiverPenguin.safe_name()}")
    await sendNotify(receiver, embed)


async def sendNotify(user: disnake.User, embed):
    await user.send(embed=embed)
