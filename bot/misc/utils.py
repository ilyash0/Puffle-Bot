from disnake.ext.commands import CommandError

from bot.data.clubpenguin.moderator import Logs
from bot.data.pufflebot.user import User
from bot.events import event
from bot.misc.penguin import Penguin


@event.on("boot")
async def setup(server):
    global client
    client = server.client_object


async def get_my_penguin_from_user_id(user_id: int) -> Penguin:
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
    return await get_penguin_from_penguin_id(user.penguin_id)


async def get_penguin_or_none_from_user_id(user_id: int) -> Penguin or None:
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
    return await get_penguin_from_penguin_id(user.penguin_id)


async def get_penguin_from_penguin_id(penguin_id: int) -> Penguin:
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
    p = await Penguin.get(penguin_id)
    await p.setup()
    return p


async def transfer_coins(sender: Penguin, receiver: Penguin, coins: int):
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
    CommandError
        - If the provided `coins` is not a positive integer (coins <= 0).
        - If the `sender` and `receiver` penguins have the same ID, indicating an incorrect receiver.
        - If the `sender` does not have enough coins to complete the transfer.

    Returns
    ------
    None
    """
    if coins <= 0:
        raise CommandError("INCORRECT_COINS_AMOUNT")

    if sender.id == receiver.id:
        raise CommandError("INCORRECT_RECEIVER")

    if sender.coins < coins:
        raise CommandError("NOT_ENOUGH_COINS")

    await sender.update(coins=sender.coins - coins).apply()
    await receiver.update(coins=receiver.coins + coins).apply()
    await Logs.create(penguin_id=int(sender.id), type=4,
                      text=f"Перевёл игроку {receiver.username} {int(coins)} монет. Через Discord бота", room_id=0,
                      server_id=8000)
    await Logs.create(penguin_id=int(receiver.id), type=4,
                      text=f"Получил от {sender.username} {int(coins)} монет. Через Discord бота", room_id=0,
                      server_id=8000)

    await client.send_xml({'body': {'action': 'pb-cdu', 'r': '0'}, 'penguin': {'p': str(sender.id)}})
    await client.send_xml({'body': {'action': 'pb-cdu', 'r': '0'}, 'penguin': {'p': str(receiver.id)}})
    return
