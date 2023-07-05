import disnake
from disnake import ApplicationCommandInteraction, AllowedMentions, Webhook
from disnake.ext.commands import Cog, slash_command
from loguru import logger

from bot.misc.buttons import Rules
from bot.misc.constants import embedRuleImageRu, embedRuleRu, embedAboutImage, embedAbout, guild_ids, \
    avatarImageBytearray
from bot.misc.select import About


class PrivateCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loads {len(self.get_slash_commands())} private commands")

    @slash_command(name="transfer", description="Transfer images from the current channel to the forum",
                   guild_ids=guild_ids)
    async def transfer(self, inter: ApplicationCommandInteraction, channel_id: str):
        await inter.response.defer()
        source_channel = inter.channel
        destination_channel = disnake.utils.get(inter.guild.channels, id=int(channel_id))

        async for message in source_channel.history(limit=None):
            if message.attachments:
                content = f", комментарий: {message.content}" if message.content else ''
                await destination_channel.create_thread(name=f"{message.author.display_name}",
                                                        content=f'Автор: {message.author.mention}{content}',
                                                        files=[await attachment.to_file() for attachment in
                                                               message.attachments],
                                                        allowed_mentions=AllowedMentions(users=False)
                                                        )
        await inter.edit_original_response(f"Успешно перенесено в <#{channel_id}>!")

    @slash_command(name="rules", description="Send rules embed", guild_ids=guild_ids)
    async def rules(self, inter: ApplicationCommandInteraction):
        webhook: Webhook = await inter.channel.create_webhook(name="CPPS.APP", avatar=avatarImageBytearray)
        message = await webhook.send(embeds=[embedRuleImageRu, embedRuleRu], wait=True)
        await message.edit(view=Rules(message))
        await inter.send("Success", ephemeral=True)

    @slash_command(name="about", description="Send about embed", guild_ids=guild_ids)
    async def about(self, inter: ApplicationCommandInteraction):
        view = disnake.ui.View(timeout=None)
        view.add_item(About())
        webhook = await inter.channel.create_webhook(name="CPPS.APP", avatar=avatarImageBytearray)
        await webhook.send(embeds=[embedAboutImage, embedAbout], view=view)
        await inter.send("Success", ephemeral=True)


def setup(bot):
    bot.add_cog(PrivateCommands(bot))
