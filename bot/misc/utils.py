from bot.data import db
from bot.data.penguin import PenguinIntegrations
from bot.misc.penguin import Penguin


async def getPenguinFromInteraction(interaction):
    penguin_id = await db.select([PenguinIntegrations.penguin_id]).where(
        ((PenguinIntegrations.discord_id == str(interaction.user.id)) &
         (PenguinIntegrations.current == True))).gino.scalar()
    if penguin_id is None:
        await interaction.response.send_message(
            content=f"Мы не нашли вашего пингвина. Пожалуйста воспользуйтесь командой `/login`", ephemeral=True)
    p = await Penguin().get(penguin_id)
    await p.setup()
    return p


async def getPenguinOrNoneFromInteraction(interaction):
    penguin_id = await db.select([PenguinIntegrations.penguin_id]).where(
        ((PenguinIntegrations.discord_id == str(interaction.user.id)) &
         (PenguinIntegrations.current == True))).gino.scalar()
    p = await Penguin().get(penguin_id)
    await p.setup()
    return p
