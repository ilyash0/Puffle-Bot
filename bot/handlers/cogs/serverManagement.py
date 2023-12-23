import disnake
from disnake import AppCommandInter, AllowedMentions, Webhook
from disnake.ext.commands import Cog, slash_command
from loguru import logger

from bot.handlers.button import Rules
from bot.misc.constants import embedRuleImageRu, embedRuleRu, avatarImageBytearray


class ServerManagementCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} app commands for server management")

    @slash_command()
    async def transfer(self, inter: AppCommandInter, forum: disnake.ForumChannel):
        """
        Transfer images from the current channel to the forum {{TRANSFER}}

        Parameters
        ----------
        inter: AppCommandInter
        forum: disnake.ForumChannel
            Target forum channel on the current server {{FORUM}}
        """
        await inter.response.defer()
        source_channel = inter.channel
        destination_channel = disnake.utils.get(inter.guild.channels, id=forum.id)

        async for message in source_channel.history(limit=None):
            if message.attachments:
                content = f", comment: {message.content}" if message.content else ''
                await destination_channel.create_thread(name=f"{message.author.display_name}",
                                                        content=f'Author: {message.author.mention}{content}',
                                                        files=[await attachment.to_file() for attachment in
                                                               message.attachments],
                                                        allowed_mentions=AllowedMentions(users=False)
                                                        )
        await inter.edit_original_response(f"Success transferred in {forum.mention}!")

    @slash_command()
    async def rules(self, inter: AppCommandInter):
        """
        Send rules embed {{RULES}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        webhook: Webhook = await inter.channel.create_webhook(name="CPPS.APP", avatar=avatarImageBytearray)
        message = await webhook.send(embeds=[embedRuleImageRu, embedRuleRu], wait=True)
        await message.edit(view=Rules(message))
        await inter.send("Success", ephemeral=True)
        await webhook.delete()


def setup(bot):
    bot.add_cog(ServerManagementCommands(bot))
