import asyncio
from disnake import ApplicationCommandInteraction
from loguru import logger

from bot.data.clubpenguin.moderator import Logs
from bot.data.pufflebot.user import User
from bot.misc.constants import loginCommand
from bot.misc.penguin import Penguin

penguins_by_id = {}


async def getPenguinFromInter(inter: ApplicationCommandInteraction) -> Penguin:
    """
    Retrieves a penguin object from the database based on the discord user ID.
    **If the penguin is not found, the function sends a response to the interaction**

    Parameters
    ----------
    inter: ApplicationCommandInteraction
        The interaction object representing the user's command.

    Returns
    ----------
    Penguin
        The penguin object retrieved from the database.
    """
    user = await User.get(inter.user.id)
    if user is None:
        return await inter.send(
            f"Мы не нашли вашего пингвина. Пожалуйста воспользуйтесь командой {loginCommand}",
            ephemeral=True)
    return await getPenguinFromPenguinId(user.penguin_id)


async def getPenguinOrNoneFromUserId(user_id: int) -> Penguin:
    """
    Get a penguin object from a user ID.

    Parameters
    ----------
    user_id: int
        The ID of the discord user to get the penguin object for.

    Returns
    -------
    Optional[Penguin]
        The penguin object, or `None` if the user is not found.
    """
    user = await User.get(user_id)
    if user is None:
        return None
    return await getPenguinFromPenguinId(user.penguin_id)


async def getPenguinFromPenguinId(penguin_id: int) -> Penguin:
    """
    Get a penguin object from a penguin ID.

    Parameters
    ----------
    penguin_id: int
        The ID of the discord user to get the penguin object for.

    Returns
    -------
    Optional[Penguin]
        The penguin object, or `None` if the user is not found.
    """
    # if cache and penguin_id in penguins_by_id:
    #     return penguins_by_id[penguin_id]

    p = await Penguin.get(penguin_id)
    await p.setup()
    penguins_by_id[penguin_id] = p
    return p


async def transferCoinsAndReturnStatus(sender: Penguin, receiver: Penguin, amount: int) -> dict:
    """
    Transfer coins between two penguins and return a status dictionary.

    Parameters
    ----------
    sender: Penguin
        The penguin object representing the sender of the coins.
    receiver: Penguin
        The penguin object representing the receiver of the coins.
    amount: int
        The number of coins to transfer.

    Returns
    ----------
    dict
        A dictionary containing the status code and message.
    """
    if amount <= 0:
        return {"code": 400, "message": "Пожалуйста введите правильное число монет"}

    if sender.id == receiver.id:
        return {"code": 400, "message": "Вы не можете передать монеты самому себе!"}

    if sender.coins < amount:
        return {"code": 400, "message": "У вас недостаточно монет для перевода"}

    await sender.update(coins=sender.coins - amount).apply()
    await receiver.update(coins=receiver.coins + amount).apply()
    await Logs.create(penguin_id=int(sender.id), type=4,
                      text=f"Перевёл игроку {receiver.username} {int(amount)} монет. Через Discord бота", room_id=0,
                      server_id=8000)
    await Logs.create(penguin_id=int(receiver.id), type=4,
                      text=f"Получил от {sender.username} {int(amount)} монет. Через Discord бота", room_id=0,
                      server_id=8000)

    await send_xml("cdu", sender.id, -amount)
    await send_xml("cdu", receiver.id, amount)

    return {"code": 200, "message": f"Вы успешно передали `{amount}` монет игроку `{receiver.safe_name()}`!"}


async def send_xml(name: str, penguinId: int = None, data=None) -> None:
    try:
        reader, writer = await asyncio.open_connection('localhost', 9879)
    except ConnectionRefusedError:
        logger.error("The remote computer refused the network connection")
        return
    logger.info("Server ('0.0.0.0', 9879) connected")

    if penguinId is None:
        ...
    data = f"<msg t='sys'><body action='pb-{name}' r='0'><penguin p='{penguinId}' />" \
           f"<amount {type(data).__name__}='{data}' /></body></msg>"
    if not writer.is_closing():
        logger.debug(f'Outgoing data: {data}')
        writer.write(data.encode('utf-8') + b'\x00')
    await writer.drain()

    response = await reader.read(100)
    logger.debug(f'Received data: {response.decode()}')

    writer.close()
    await writer.wait_closed()
    logger.info("Server ('0.0.0.0', 9879) disconnected")
