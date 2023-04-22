import disnake


class LoginModal(disnake.ui.Modal):
    def __init__(self, authApprove):
        self.authApprove = authApprove

        components = [
            disnake.ui.TextInput(label="Одноразовый код аутентификации", required=True,
                                 placeholder="Введите код, который вы получили в открытке", custom_id="authCodeInput")]

        super().__init__(title="Привяжите свои аккаунты", components=components, custom_id="login")

    async def callback(self, interaction: disnake.ModalInteraction):
        authCode = interaction.text_values["authCodeInput"]
        await self.authApprove(interaction, authCode)
