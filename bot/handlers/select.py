from disnake import MessageInteraction, SelectOption, AllowedMentions
from disnake.ui import Select

from bot.handlers.buttons import RulesEphemeral, Roles
from bot.misc.constants import embedLinks, embedRuleImageRu, embedRuleRu, embedRolesRu
from bot.misc.penguin import Penguin


class SelectPenguins(Select):
    def __init__(self, penguinsList, user):
        self.disabled = False
        self.user = user

        options = []
        for penguin in penguinsList:
            options.append(SelectOption(label=penguin["safe_name"], value=penguin["id"]))
        super().__init__(placeholder="Выберите пингвина", options=options, custom_id="penguins")

    async def callback(self, inter: MessageInteraction):
        penguin_id = int(inter.values[0])
        newCurrentPenguin = await Penguin.get(penguin_id)

        await self.user.update(penguin_id=penguin_id).apply()

        await inter.send(f"Успешно. Теперь ваш текущий аккаунт `{newCurrentPenguin.safe_name()}`", ephemeral=True)


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
