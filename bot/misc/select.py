from disnake import MessageInteraction, SelectOption, AllowedMentions
from disnake.ui import Select

from bot.misc.buttons import RulesEphemeral, Roles
from bot.misc.constants import embedLinks, embedRuleImageRu, embedRuleRu, embedRolesRu


class SelectPenguins(Select):
    def __init__(self, penguinsList, function, userID):
        self.disabled = False
        self.function = function
        self.userID = userID

        options = []
        for penguin in penguinsList:
            options.append(SelectOption(label=penguin["safe_name"], value=penguin["id"]))
        super().__init__(placeholder="Выберите пингвина", options=options, custom_id="penguins")

    async def callback(self, interaction: MessageInteraction):
        if interaction.user.id != self.userID:
            await interaction.response.send_message(content=f"Ай-ай-ай,не суй пальцы в розетку", ephemeral=True)
            return
        if self.disabled:
            await interaction.response.send_message(content=f"Вы уже сменили аккаунт", ephemeral=True)
            return
        self.disabled = True

        penguin_id = int(interaction.values[0])
        await self.function(interaction, penguin_id)


class About(Select):
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
            await inter.send(ephemeral=True, embeds=[embedRolesRu],
                             allowed_mentions=AllowedMentions(roles=False, users=False))
            await inter.edit_original_response(view=Roles(inter))

        else:
            await inter.send(ephemeral=True, content=inter.values[0])
