from bot.data.pufflebot.users import Users
from bot.misc.penguin import Penguin


async def getPenguinFromInter(inter):
    user = await Users.get(inter.user.id)
    if user is None:
        await inter.response.send_message(
            content=f"Мы не нашли вашего пингвина. Пожалуйста воспользуйтесь командой </login:1099629339110289442>",
            ephemeral=True)
        return
    p = await Penguin.get(user.penguin_id)
    await p.setup()
    return p


async def getPenguinOrNoneFromInter(inter):
    user = await Users.get(inter.user.id)
    if user is None:
        return None
    p = await Penguin.get(user.penguin_id)
    await p.setup()
    return p
