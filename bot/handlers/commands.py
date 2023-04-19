from datetime import datetime
from random import sample
from loguru import logger
import discord
from discord import app_commands
from discord.ext import commands
from bot.data import db
from bot.data.moderator import Logs
from bot.penguin import Penguin
from bot.data.penguin import PenguinIntegrations
from bot.handlers.buttons import Question

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="%", intents=intents)
messageListener = []


@bot.event
async def on_ready():
    logger.info("Bot ready")
    await bot.tree.sync()


@bot.event
async def on_message(message: discord.Message):
    if len(messageListener) == 0:
        return

    for i, listener in enumerate(messageListener):
        if message.author.id == listener['authorId'] and message.channel.id == listener['channel']:
            function = listener['function']
            messageListener.pop(i)
            await function(message)


# noinspection PyUnresolvedReferences
@bot.tree.command(name="ilyash", description=":D")
async def ilyash(interaction: discord.Interaction):
    await interaction.response.send_message(content=f"Теперь вы пешка иляша!")


@bot.tree.command(name="card", description="Показывает полезную информацию о твоём аккаунте")
async def card(interaction: discord.Interaction):
    user = interaction.user
    p: Penguin = await getPenguinFromInteraction(interaction)

    embed = discord.Embed(title="Карточка пингвина",
                          description=f"Знакомьтесь, этот пингвин принадлежит {user.mention}",
                          color=discord.Color.from_rgb(3, 91, 209))
    embed.set_thumbnail(url=f"https://play.cpps.app/avatar/{p.id}/cp?size=600")
    embed.add_field(name="ID", value=p.id)
    embed.add_field(name="Имя", value=p.safe_name())
    embed.add_field(name="Монеты", value=p.coins)
    embed.add_field(name="Марки", value=len(p.stamps) + CountEpfAwards(p.inventory))
    embed.add_field(name="Возраст пингвина", value=f"{(datetime.now() - p.registration_date).days} дней")
    embed.add_field(name="Сотрудник", value="Да" if p.moderator else "Нет")
    # noinspection PyUnresolvedReferences
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="login", description="Привязать свой Discord аккаунт к пингвину")
@app_commands.describe(penguin="Имя вашего пингвина")
async def login(interaction: discord.Interaction, penguin: str):
    user = interaction.user
    penguinId = await Penguin.select('id').where(Penguin.username == penguin.lower()).gino.first()
    penguinId = int(penguinId[0])
    p: Penguin = await Penguin.get(penguinId)

    symbols = "QWERTYUIOPASDFGHJKLZXCVBNM0123456789"
    authCode = "".join(sample(symbols, 8))

    await p.add_inbox(302, details=authCode)

    async def authApprove(message):
        if message.content.upper() == authCode:
            await message.channel.send('Аккаунты успешно привязаны!')
            await PenguinIntegrations.create(penguin_id=p.id, discord_id=str(user.id))
            return

        await message.channel.send('Не верный код авторизации, попробуйте снова')

    messageListener.append({"function": authApprove, "authorId": user.id, "channel": interaction.channel_id})

    # noinspection PyUnresolvedReferences
    await interaction.response.send_message(
        content=f"На ваш аккаунт была отправлена открытка с кодом *(если нет - перезайдите в игру)*. \n"
                f"Напишите одноразовый код в этот канал")


@bot.tree.command(name="logout", description="Отвязать свой Discord аккаунт от своего пингвина")
async def logout(interaction: discord.Interaction):
    p: Penguin = await getPenguinFromInteraction(interaction)

    def run():
        await PenguinIntegrations.delete.where(PenguinIntegrations.penguin_id == p.id).gino.status()

        # noinspection PyUnresolvedReferences
        await interaction.response.edit_message(content=f"Ваш аккаунт `{p.safe_name()}` успешно отвязан")

    view = Question(interaction.user.id, run)
    # noinspection PyUnresolvedReferences
    await interaction.response.send_message(content=f"Вы уверены, что хотите отвязать аккаунт `{p.safe_name()}`?",
                                            view=view)


@bot.tree.command(name="guiderole", description="Получить роль экскурсовода")
async def guideRole(interaction: discord.Interaction):
    p: Penguin = await getPenguinFromInteraction(interaction)
    roleID = interaction.guild.get_role(860201914334576650)

    if 428 in p.inventory:
        if roleID not in interaction.user.roles:
            await interaction.user.add_roles(roleID)
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(
                content=f"Вы получили роль {roleID}! Теперь вы можете писать в канале <#860201914334576650>")
        else:
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(content=f"У вас уже есть роль {roleID}")
    else:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message(content=f"Мы не нашли у вас шапку экскурсовода")


@bot.tree.command(name="pay", description="Перевести свои монеты другому игроку")
@app_commands.describe(receiver="Получатель (его ник в игре)")
@app_commands.describe(amount="Количество монет")
async def pay(interaction: discord.Interaction, receiver: str, amount: int):
    p: Penguin = await getPenguinFromInteraction(interaction)

    receiver.lower()
    receiverId = await Penguin.select('id').where(Penguin.username == receiver).gino.first()
    receiverId = int(receiverId[0])
    r: Penguin = await Penguin.get(receiverId)

    if amount <= 0:
        # noinspection PyUnresolvedReferences
        return await interaction.response.send_message(
            content='Пожалуйста введите правильное число монет')

    if p.id == r.id:
        # noinspection PyUnresolvedReferences
        return await interaction.response.send_message(
            content="Вы не можете передать монеты самому себе!")

    if p.coins < amount:
        # noinspection PyUnresolvedReferences
        return await interaction.response.send_message(
            content='У вас недостаточно монет для перевода')

    await p.update(coins=p.coins - amount).apply()
    await r.update(coins=r.coins + amount).apply()
    await Logs.create(penguin_id=int(r.id), type=4,
                      text=f"Получил от {p.username} {int(amount)} монет. Через Discord бота", room_id=0,
                      server_id=8000)
    await Logs.create(penguin_id=int(p.id), type=4,
                      text=f"Перевёл игроку {r.username} {int(amount)} монет. Через Discord бота", room_id=0,
                      server_id=8000)

    # noinspection PyUnresolvedReferences
    await interaction.response.send_message(
        content=f"Вы успешно передали `{amount}` монет игроку `{receiver}`!")


async def getPenguinFromInteraction(interaction):
    penguin_id = await db.select([PenguinIntegrations.penguin_id]).where(
        (PenguinIntegrations.discord_id == str(interaction.user.id))).gino.scalar()
    if penguin_id is None:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message(
            content=f"Мы не нашли вашего пингвина. Пожалуйста воспользуйтесь командой `/login`", ephemeral=True)
    p = await Penguin().get(penguin_id)
    await p.setup()
    return p


def CountEpfAwards(inventory):
    result: int = 0
    AWARD_STAMP_IDS = list(range(801, 807)) + list(range(808, 812)) + list(range(813, 821)) + [822, 823, 8007, 8008]

    for stamp in AWARD_STAMP_IDS:
        if stamp in inventory:
            result += 1
    return result
