import asyncio
from loguru import logger

from bot.data.clubpenguin.moderator import Logs
from bot.data.pufflebot.user import User
from bot.misc.penguin import Penguin

penguins_by_id = {}


async def getMyPenguinFromUserId(user_id: int) -> Penguin:
    """
    Retrieves a penguin object from the database based on the discord user ID.

    Parameters
    ----------
    user_id: int
        The user's unique identifier in the database.

    Returns
    ----------
    Penguin
        The penguin object associated with the provided user ID.

    Raises
    ------
    KeyError
        If the penguin is not found, this function raises a KeyError with the message "MY_PENGUIN_NOT_FOUND."
    """
    user = await User.get(user_id)
    if user is None:
        raise KeyError("MY_PENGUIN_NOT_FOUND")
    return await getPenguinFromPenguinId(user.penguin_id)


async def getPenguinOrNoneFromUserId(user_id: int) -> Penguin or None:
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


async def transferCoins(sender: Penguin, receiver: Penguin, coins: int):
    """
    Transfer coins from one penguin to another and return a status dictionary.

    Parameters
    ----------
    sender: Penguin
        The penguin object representing the sender of the coins.
    receiver: Penguin
        The penguin object representing the receiver of the coins.
    coins: int
        The number of coins to be transferred. It must be a positive integer.

    Raises
    ------
    ValueError
        - If the provided `coins` is not a positive integer (coins <= 0).
        - If the `sender` and `receiver` penguins have the same ID, indicating an incorrect receiver.
        - If the `sender` does not have enough coins to complete the transfer.

    Returns
    ------
    None
    """
    if coins <= 0:
        raise ValueError("INCORRECT_COINS_AMOUNT")

    if sender.id == receiver.id:
        raise ValueError("INCORRECT_RECEIVER")

    if sender.coins < coins:
        raise ValueError("NOT_ENOUGH_COINS")

    await sender.update(coins=sender.coins - coins).apply()
    await receiver.update(coins=receiver.coins + coins).apply()
    await Logs.create(penguin_id=int(sender.id), type=4,
                      text=f"Перевёл игроку {receiver.username} {int(coins)} монет. Через Discord бота", room_id=0,
                      server_id=8000)
    await Logs.create(penguin_id=int(receiver.id), type=4,
                      text=f"Получил от {sender.username} {int(coins)} монет. Через Discord бота", room_id=0,
                      server_id=8000)

    await send_xml("cdu", sender.id, -coins)
    await send_xml("cdu", receiver.id, coins)
    return


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
