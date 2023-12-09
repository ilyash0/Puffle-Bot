import sys
import traceback

import disnake
from disnake import ModalInteraction
from loguru import logger


class Modal(disnake.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ...

    async def on_error(self, error: Exception, inter: ModalInteraction) -> None:
        try:
            logger.error(f"User error: {error.args[0]}")
            await inter.send(f"{inter.bot.i18n.get(error.args[0])[str(inter.locale)]}", ephemeral=True)
            return
        except (KeyError, TypeError, AttributeError):
            logger.error(f"Ignoring exception in modal {self.title}", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__)
            await inter.send(f"Unknown error", ephemeral=True)


class FundraisingModal(Modal):
    def __init__(self, function, title, inter):
        self.function = function
        self.title = title

        components = [
            disnake.ui.TextInput(label=inter.bot.i18n.get("TRANSFER_COINS")[str(inter.locale)],
                                 placeholder=inter.bot.i18n.get("ENTER_AMOUNT")[str(inter.locale)],
                                 custom_id="payInput", required=True)]

        super().__init__(title=self.title, components=components, custom_id="fundraising")

    async def callback(self, inter: disnake.ModalInteraction):
        coins = inter.text_values["payInput"]
        try:
            coins = int(coins)
        except ValueError:
            return await inter.send(inter.bot.i18n.get("INCORRECT_COINS_AMOUNT")[str(inter.locale)], ephemeral=True)

        await self.function(inter, int(coins))
