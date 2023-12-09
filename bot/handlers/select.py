from disnake import MessageInteraction, SelectOption, AllowedMentions
from disnake.ui import Select

from bot.handlers.button import RulesEphemeral, Roles
from bot.misc.constants import embedLinks, embedRuleImageRu, embedRuleRu, embedRolesRu, embedRoles2Ru
from bot.misc.penguin import Penguin


class ChoosePenguin(Select):
    def __init__(self, penguinsList, user, inter):
        self.disabled = False
        self.user = user

        options = []
        for penguin in penguinsList:
            options.append(SelectOption(label=penguin["safe_name"], value=penguin["id"]))
        super().__init__(placeholder=inter.bot.i18n.get("CHOOSE_PENGUIN")[str(inter.locale)], options=options,
                         custom_id="penguins")

    async def callback(self, inter: MessageInteraction):
        penguin_id = int(inter.values[0])
        newCurrentPenguin = await Penguin.get(penguin_id)

        await self.user.update(penguin_id=penguin_id).apply()

        await inter.send(
            inter.bot.i18n.get("PENGUIN_CHOSEN")[str(inter.locale)].replace("%nickname%",
                                                                             newCurrentPenguin.safe_name()),
            ephemeral=True)


class AboutSelect(Select):
    def __init__(self):
        options = [SelectOption(label="Links", value="Links"),
                   SelectOption(label="Rules", value="Rules"),
                   SelectOption(label="List of roles", value="Roles")]
        super().__init__(options=options, custom_id="about")

    async def callback(self, inter: MessageInteraction):
        if inter.values[0] == "Links":
            await inter.send(ephemeral=True, embeds=[embedLinks],
                             allowed_mentions=AllowedMentions(roles=False, users=False))
        elif inter.values[0] == "Rules":
            await inter.send(ephemeral=True, embeds=[embedRuleImageRu, embedRuleRu],
                             allowed_mentions=AllowedMentions(roles=False, users=False))
            await inter.edit_original_response(view=RulesEphemeral(inter))
        elif inter.values[0] == "Roles":
            await inter.send(ephemeral=True, embeds=[embedRolesRu, embedRoles2Ru],
                             allowed_mentions=AllowedMentions(roles=False, users=False))
            await inter.edit_original_response(view=Roles(inter))

        else:
            await inter.send(ephemeral=True, content=inter.values[0])
