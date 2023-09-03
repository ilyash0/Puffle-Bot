import asyncio
from disnake import ApplicationCommandInteraction
from loguru import logger

from bot.data.clubpenguin.moderator import Logs
from bot.data.pufflebot.user import User
from bot.misc.constants import loginCommand
from bot.misc.penguin import Penguin

penguins_by_id = {}


async def getPenguinFromInter(inter: ApplicationCommandInteraction, *, cache=True) -> Penguin:
    """
    Retrieves a penguin object from the database based on the discord user ID.
    **If the penguin is not found, the function sends a response to the interaction**

    Parameters
    ----------
    inter: ApplicationCommandInteraction
        The interaction object representing the user's command.
    cache : bool, optional
        Whether to cache the penguin object, by default True

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
    return await getPenguinFromPenguinId(user.penguin_id, cache=cache)


async def getPenguinOrNoneFromUserId(user_id: int, *, cache=True) -> Penguin:
    """
    Get a penguin object from a user ID.

    Parameters
    ----------
    user_id: int
        The ID of the discord user to get the penguin object for.
    cache : bool, optional
        Whether to cache the penguin object, by default True

    Returns
    -------
    Optional[Penguin]
        The penguin object, or `None` if the user is not found.
    """
    user = await User.get(user_id)
    if user is None:
        return None
    return await getPenguinFromPenguinId(user.penguin_id, cache=cache)


async def getPenguinFromPenguinId(penguin_id: int, *, cache=True) -> Penguin:
    """
    Get a penguin object from a penguin ID.

    Parameters
    ----------
    penguin_id: int
        The ID of the discord user to get the penguin object for.
    cache : bool, optional
        Whether to cache the penguin object, by default True

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
    await Logs.create(penguin_id=int(receiver.id), type=4,
                      text=f"Получил от {sender.username} {int(amount)} монет. Через Discord бота", room_id=0,
                      server_id=8000)
    await Logs.create(penguin_id=int(sender.id), type=4,
                      text=f"Перевёл игроку {receiver.username} {int(amount)} монет. Через Discord бота", room_id=0,
                      server_id=8000)

    # await send_xt("cdu", [sender.id, amount])

    return {"code": 200, "message": f"Вы успешно передали `{amount}` монет игроку `{receiver.safe_name()}`!"}


async def send_xt(name: str, data: list) -> None:
    reader, writer = await asyncio.open_connection('0.0.0.0', 9880)
    logger.info("Server ('0.0.0.0', 9880) connected")

    data = ''.join([f'{item}%' for item in data])
    data = f"%xt%s%pb#{name}%-1%{data}"
    if not writer.is_closing():
        logger.debug(f'Outgoing data: {data}')
        writer.write(data.encode('utf-8') + b'\x00')
    await writer.drain()

    response = await reader.read(100)
    print(response.decode())

    writer.close()
    await writer.wait_closed()
