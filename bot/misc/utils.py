from disnake import ApplicationCommandInteraction

from bot.data.pufflebot.users import Users
from bot.misc.constants import loginCommand
from bot.misc.penguin import Penguin


async def getPenguinFromInter(inter: ApplicationCommandInteraction):
    user = await Users.get(inter.user.id)
    if user is None:
        await inter.send(
            f"Мы не нашли вашего пингвина. Пожалуйста воспользуйтесь командой {loginCommand}",
            ephemeral=True)
        return
    p = await Penguin.get(user.penguin_id)
    await p.setup()
    return p


async def getPenguinOrNoneFromId(user_id: int):
    user = await Users.get(user_id)
    if user is None:
        return None
    p = await Penguin.get(user.penguin_id)
    await p.setup()
    return p
