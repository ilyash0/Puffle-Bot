import discord


class LoginModal(discord.ui.Modal, title="Привяжите свои аккаунты"):
    def __init__(self, authApprove):
        super().__init__()
        self.authApprove = authApprove

    authCodeInput = discord.ui.TextInput(
        label="Одноразовый код аутентификации",
        required=True,
        placeholder="Введите код, который вы получили в открытке"
    )

    async def on_submit(self, interaction: discord.Interaction):
        await self.authApprove(interaction, self.authCodeInput.value)
