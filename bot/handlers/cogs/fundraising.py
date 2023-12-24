import disnake
from disnake import AppCommandInter, Embed
from disnake.ext.commands import Cog, slash_command
from loguru import logger

from bot.data.pufflebot.fundraising import Fundraising
from bot.handlers.button import FundraisingButtons
from bot.handlers.censure import is_message_valid
from bot.misc.penguin import Penguin


class FundraisingCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} fundraising app commands")

    @slash_command()
    async def fundraising(self, inter: AppCommandInter):
        ...

    @fundraising.sub_command(name="open")
    async def fundraising_open(self, inter: AppCommandInter, title: str, coins: int = None):
        """
        Start a fundraising {{FR_OPEN}}

        Parameters
        ----------
        inter: AppCommandInter
        title: str
            Title for fundraising {{TITLE}}
        coins:  Optional[int]
            Number of coins {{COINS}}
        """
        # TODO: notifications about the collection of goal amount.
        # TODO: replace the embed with a picture.
        lang: str = str(inter.avail_lang)
        if not is_message_valid(title):
            return await inter.send(self.bot.i18n.get("KEEP_RULES")[lang], ephemeral=True)

        p: Penguin = await inter.user.penguin
        current_fundraising = await Fundraising.query.where(Fundraising.penguin_id == p.id).gino.first()
        if current_fundraising:
            try:
                channel = await self.bot.fetch_channel(current_fundraising.channel_id)
                message = await channel.fetch_message(current_fundraising.message_id)
                return await inter.send(
                    self.bot.i18n.get("FR_ALREADY_STARTED")[lang].replace("%url%", message.jump_url),
                    ephemeral=True)
            except disnake.errors.NotFound:
                await current_fundraising.delete()
            except disnake.errors.Forbidden:
                return await inter.send(self.bot.i18n.get("FR_ALREADY_STARTED_ALT")[lang], ephemeral=True)

        embed = Embed(color=0x2B2D31, title=title)
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
        embed.add_field(self.bot.i18n.get("COINS_COLLECTED")[lang],
                        f"0{f' / {coins:,}' if coins else ''}".replace(',', ' '))
        embed.set_footer(text=self.bot.i18n.get("SPONSORS")[lang].replace("%num%", "0"))
        message: disnake.Message = await inter.channel.send(embed=embed)

        fundraising = await Fundraising.create(server_id=inter.guild_id, channel_id=inter.channel_id,
                                               message_id=message.id, penguin_id=p.id, goal=coins)
        await message.edit(view=FundraisingButtons(fundraising, message, p, 0, inter))
        await inter.send(self.bot.i18n.get("FR_BEGUN")[lang], ephemeral=True)

    @fundraising.sub_command(name="close")
    async def fundraising_close(self, inter: AppCommandInter):
        """
        Stop a fundraising {{FR_CLOSE}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        lang: str = str(inter.avail_lang)
        p: Penguin = await inter.user.penguin
        fundraising = await Fundraising.query.where(Fundraising.penguin_id == p.id).gino.first()
        try:
            if not fundraising:
                return await inter.send(self.bot.i18n.get("FR_NOT_STARTED")[lang], ephemeral=True)

            await fundraising.delete()
            channel = await self.bot.fetch_channel(fundraising.channel_id)
            message = await channel.fetch_message(fundraising.message_id)
            await message.edit(self.bot.i18n.get("CLOSED")[lang], view=None)
        except disnake.NotFound:
            pass
        except disnake.errors.Forbidden:
            return await inter.send(self.bot.i18n.get("BOT_DOESNT_HAVE_PERMISSION")[lang], ephemeral=True)
        await inter.send(self.bot.i18n.get("SUCCESS")[lang], ephemeral=True)


def setup(bot):
    bot.add_cog(FundraisingCommands(bot))
