from disnake import ApplicationCommandInteraction

from bot.data.clubpenguin.moderator import Logs
from bot.data.pufflebot.users import Users
from bot.handlers.notification import notifyCoinsReceive
from bot.misc.constants import loginCommand
from bot.misc.penguin import Penguin


async def getPenguinFromInter(inter: ApplicationCommandInteraction):
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
    user = await Users.get(inter.user.id)
    if user is None:
        await inter.send(
            f"Мы не нашли вашего пингвина. Пожалуйста воспользуйтесь командой {loginCommand}",
            ephemeral=True)
        return
    p = await Penguin.get(user.penguin_id)
    await p.setup()
    return p


async def getPenguinOrNoneFromUserId(user_id: int):
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
    user = await Users.get(user_id)
    if user is None:
        return None
    p = await Penguin.get(user.penguin_id)
    await p.setup()
    return p


async def transferCoinsAndReturnStatus(sender: Penguin, receiver: Penguin, amount: int, message: str = None) -> dict:
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
    message : str, optional
        An optional message to include with the transfer.

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
    await notifyCoinsReceive(sender, receiver, amount, message)

    return {"code": 200, "message": f"Вы успешно передали `{amount}` монет игроку `{receiver.safe_name()}`!"}
