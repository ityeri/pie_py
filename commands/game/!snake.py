import nextcord
from nextcord.ext import commands
from nextcord import ButtonStyle, Interaction
from nextcord.ui import Button, View


class ButtonView(View):
    def __init__(self):
        super().__init__()

        # 버튼 정의 (style, label, and custom_id)
        self.add_item(Button(style=ButtonStyle.primary, label="Click Me", custom_id="button_click"))

    # 버튼 클릭 시 처리할 함수 정의
    @nextcord.ui.button(label="Click me!", style=ButtonStyle.green)
    async def button_callback(self, button: Button, interaction: Interaction):
        await interaction.response.send_message(f"{interaction.user.name} clicked the button!")


class Snake(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @nextcord.slash_command(name="지렁이", description="과연 이게 가능할까")
    async def snake(self, interaction: Interaction):
        message = interaction.send("지렁이 게임이 곧 시작합니다!")
        