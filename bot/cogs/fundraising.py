import disnake
from disnake import ApplicationCommandInteraction, Embed
from disnake.ext.commands import Cog, slash_command
from loguru import logger

from bot.data.pufflebot.fundraising import Fundraising
from bot.handlers.button import FundraisingButtons
from bot.handlers.censure import is_message_valid
from bot.misc.penguin import Penguin
from bot.misc.utils import getPenguinFromInter


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
            return await inter.send("Соблюдайте правила!", ephemeral=True)

        p: Penguin = await getPenguinFromInter(inter)
        currentFundraising = await Fundraising.query.where(Fundraising.penguin_id == p.id).gino.first()
        if currentFundraising:
            try:
                channel = await self.bot.fetch_channel(currentFundraising.channel_id)
                message = await channel.fetch_message(currentFundraising.message_id)
                return await inter.send(f"Вы уже начали сбор пожертвований: {message.jump_url}", ephemeral=True)
            except disnake.errors.NotFound:
                await currentFundraising.delete()
            except disnake.errors.Forbidden:
                return await inter.send(f"Вы уже начали сбор пожертвований.", ephemeral=True)

        embed = Embed(color=0x2B2D31, title=title)
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
        embed.add_field("Собрано монет", f"0{f' из {goal:,}' if goal else ''}".replace(',', ' '))
        embed.set_footer(text="Спонсоры: 0")
        message: disnake.Message = await inter.channel.send(embed=embed)

        fundraising = await Fundraising.create(server_id=inter.guild_id, channel_id=inter.channel_id,
                                               message_id=message.id, penguin_id=p.id, goal=goal)
        await message.edit(view=FundraisingButtons(fundraising, message, p, 0))
        await inter.send("Сбор пожертвований начат.", ephemeral=True)

    @fundraising.sub_command(name="close")
    async def fundraising_close(self, inter: ApplicationCommandInteraction):
        """
        Stop a fundraising {{FR_CLOSE}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        """
        p: Penguin = await getPenguinFromInter(inter)
        fundraising = await Fundraising.query.where(Fundraising.penguin_id == p.id).gino.first()
        try:
            if not fundraising:
                return await inter.send("Сбор пожертвований ещё не был открыт", ephemeral=True)

            await fundraising.delete()
            channel = await self.bot.fetch_channel(fundraising.channel_id)
            message = await channel.fetch_message(fundraising.message_id)
            await message.edit("Закрыт", view=None)
        except disnake.NotFound:
            pass
        except disnake.errors.Forbidden:
            return await inter.send(f"У бота недостаточно прав для этого", ephemeral=True)
        await inter.send("Успешно", ephemeral=True)


def setup(bot):
    bot.add_cog(FundraisingCommands(bot))
