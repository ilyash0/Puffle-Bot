import disnake
from disnake import ApplicationCommandInteraction, Embed
from disnake.ext.commands import Cog, slash_command
from loguru import logger

from bot.data.pufflebot.fundraising import Fundraising
from bot.handlers.button import FundraisingButtons
from bot.handlers.censure import is_message_valid
from bot.misc.penguin import Penguin
from bot.misc.utils import getMyPenguinFromUserId


class FundraisingCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} fundraising app commands")

    @slash_command()
    async def fundraising(self, inter: ApplicationCommandInteraction):
        ...

    @fundraising.sub_command(name="open")
    async def fundraising_open(self, inter: ApplicationCommandInteraction, title: str, goal: int = None):
        """
        Start a fundraising {{FR_OPEN}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        title: str
            Title for fundraising {{TITLE}}
        goal:  Optional[int]
            Number of coins {{COINS}}
        """
        # TODO: notifications about the collection of goal amount.
        # TODO: show a beautiful picture.
        if not is_message_valid(title):
            return await inter.send(self.bot.i18n.get("KEEP_RULES")[inter.locale.value], ephemeral=True)

        p: Penguin = await getMyPenguinFromUserId(inter.author.id)
        currentFundraising = await Fundraising.query.where(Fundraising.penguin_id == p.id).gino.first()
        if currentFundraising:
            try:
                channel = await self.bot.fetch_channel(currentFundraising.channel_id)
                message = await channel.fetch_message(currentFundraising.message_id)
                return await inter.send(
                    self.bot.i18n.get("FR_ALREADY_STARTED")[inter.locale.value].replace("%url%", message.jump_url),
                    ephemeral=True)
            except disnake.errors.NotFound:
                await currentFundraising.delete()
            except disnake.errors.Forbidden:
                return await inter.send(self.bot.i18n.get("FR_ALREADY_STARTED_ALT")[inter.locale.value], ephemeral=True)

        embed = Embed(color=0x2B2D31, title=title)
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
        embed.add_field(self.bot.i18n.get("COINS_COLLECTED")[inter.locale.value],
                        f"0{f' / {goal:,}' if goal else ''}".replace(',', ' '))
        embed.set_footer(text=self.bot.i18n.get("SPONSORS")[inter.locale.value].replace("%num%", "0"))
        message: disnake.Message = await inter.channel.send(embed=embed)

        fundraising = await Fundraising.create(server_id=inter.guild_id, channel_id=inter.channel_id,
                                               message_id=message.id, penguin_id=p.id, goal=goal)
        await message.edit(view=FundraisingButtons(fundraising, message, p, 0, inter))
        await inter.send(self.bot.i18n.get("FR_BEGUN")[inter.locale.value], ephemeral=True)

    @fundraising.sub_command(name="close")
    async def fundraising_close(self, inter: ApplicationCommandInteraction):
        """
        Stop a fundraising {{FR_CLOSE}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        """
        p: Penguin = await getMyPenguinFromUserId(inter.author.id)
        fundraising = await Fundraising.query.where(Fundraising.penguin_id == p.id).gino.first()
        try:
            if not fundraising:
                return await inter.send(self.bot.i18n.get("FR_NOT_STARTED")[inter.locale.value], ephemeral=True)

            await fundraising.delete()
            channel = await self.bot.fetch_channel(fundraising.channel_id)
            message = await channel.fetch_message(fundraising.message_id)
            await message.edit(self.bot.i18n.get("CLOSED")[inter.locale.value], view=None)
        except disnake.NotFound:
            pass
        except disnake.errors.Forbidden:
            return await inter.send(self.bot.i18n.get("BOT_DOESNT_HAVE_PERMISSION")[inter.locale.value], ephemeral=True)
        await inter.send(self.bot.i18n.get("SUCCESS")[inter.locale.value], ephemeral=True)


def setup(bot):
    bot.add_cog(FundraisingCommands(bot))
