from io import BytesIO

from requests import get
from disnake import Embed

# ids
cppsapp_server_id = 755445822920982548
test_server_id = 830884170934124585
rules_webhook_id = 1126642813543657525
rules_message_id = 1126642815544344628
about_message_id = 1126642785219530782

# Links
avatarImageLink = "https://sun9-53.userapi.com/impg/u2ZUQnEo_eY4SgbIGIWy860tArL6mIeeObol1w/WoMi6hnW2QE.jpg?size=1536x1536&quality=96&sign=be7a5cade4cbb255a120f937271f327c"
enFullRulesLink = "https://docs.google.com/document/d/1gqgdoT1BeAUGahlAr3zrPqWmr3yDh0irG3sRVqMNt1c/"
ruFullRulesLink = "https://wiki.cpps.app/index.php?title=Правила"
placeholderImageLink = "https://cdn.discordapp.com/attachments/937328189859057674/944647455109156884/1.png"
online_url = "https://play.cpps.app/ru/online"

# Dicts
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

# Arrays
guild_ids = [cppsapp_server_id, test_server_id]

# Bytearrays
avatarImageBytearray = BytesIO(get(avatarImageLink).content).getvalue()

# Custom emojis
emojiLaughing = "<:laughing:788392697336954920>"
emojiDay = "<:day:788395886450966588>"
emojiModerator = "<:moderator:789476531915325510>"
emojiGame = "<:game:788396232456011796>"
emojiVk = "<:VK:1121760227994382459>"
emojiYt = "<:yt:1121764618239496263>"
emojiGameFavicon = "<:favicon:1121758719634571405>"
emojiWikiFavicon = "<:wiki:1121764147307237447>"

# ========== EMBEDS ==========


# Russian rule embeds
embedRuleRu = Embed(color=0x2B2D31)
embedRuleRu.add_field(name=f"{emojiLaughing} **Уважай окружающих**", value="Не дразни и не обижай окружающих",
                      inline=False)
embedRuleRu.add_field(name=f"{emojiDay} **Общайся вежливо**",
                      value="Не используй грубые или неприличные выражения", inline=False)
embedRuleRu.add_field(name=f"{emojiModerator} **Соблюдай правила безопасности в интернете**",
                      value="Не делись личной информацией", inline=False)
embedRuleRu.add_field(name=f"{emojiGame} **Играй по-честному**",
                      value="Не используй программы сторонних разработчиков", inline=False)
embedRuleRu.set_image(url=placeholderImageLink)
embedRuleRu.set_footer(text="До встречи на острове!")
embedRuleImageRu = Embed(color=0x2B2D31)
embedRuleImageRu.set_image(url="https://cpps.app/rules-ru.png")

# English rule embeds
embedRuleEn = Embed(color=0x2B2D31)
embedRuleEn.add_field(name=f"{emojiLaughing} **Respect others**", value="No bullying or being mean to others",
                      inline=False)
embedRuleEn.add_field(name=f"{emojiDay} **Chat nicely**", value="No rude or inappropriate language", inline=False)
embedRuleEn.add_field(name=f"{emojiModerator} **Stay safe online**",
                      value="No sharing personal information", inline=False)
embedRuleEn.add_field(name=f"{emojiGame} **Play fair**",
                      value="No cheating or use of third party programs", inline=False)
embedRuleEn.set_image(url=placeholderImageLink)
embedRuleEn.set_footer(text="Waddle On!")
embedRuleImageEn = Embed(color=0x2B2D31)
embedRuleImageEn.set_image(url="https://cpps.app/rules-en.png")

# About embeds
embedAbout = Embed(color=0x2B2D31)
embedAbout.description = """
## :flag_ru:
Мы возрождение оригинального Клуба Пингвинов от Disney, сделанное его фанатами. 
*Перейдите в раздел, нажав на него в меню выбора, чтобы узнать подробнее.*

## :flag_us:
We are a copy of the original game from Disney, made by fans.
*Go to the section by clicking on it in the selection menu to learn more.*
"""
embedAbout.set_image(url=placeholderImageLink)
embedAboutImage = Embed(color=0x2B2D31)
embedAboutImage.set_image(url="https://cpps.app/CPPS.APP.png")

# Links embed
embedLinks = Embed(color=0x2B2D31)
embedLinks.description = f"""
```Links to social networks and other```
> **{emojiVk} • VK – https://vk.com/cpps_official/**

> **{emojiYt} • YOUTUBE – https://www.youtube.com/@cppsapp/**

> **{emojiGameFavicon} • GAME – https://cpps.app/**

> **{emojiWikiFavicon} • WIKI – https://wiki.cpps.app/**
"""
embedLinks.set_image(url=placeholderImageLink)

# Roles embeds
embedRolesRu = Embed(color=0x2B2D31)
embedRolesRu.description = """
```Роли-достижения (ACHIEVEMENTS):```
<@&860176034834153543> — Победитель конкурса «Рейтинг активности».

<@&792899688608038913> — [Nitro бустеры](https://support.discord.com/hc/ru/articles/360028038352) сервера.

<@&860125656427003905> — Пингвины, владеющие популярным бизнесом.

<@&1124784263754158090> — Игроки, получившие *шляпу экскурсовода* в игре.
"""
embedRolesRu.set_image(url=placeholderImageLink)
embedRolesEn = Embed(color=0x2B2D31)
embedRolesEn.description = """
```Achievements roles:```
<@&860176034834153543> — The winner of the «Activity Rating» contest.

<@&792899688608038913> — [Nitro boosters](https://support.discord.com/hc/en-us/articles/360028038352).

<@&860125656427003905> — Penguins who own a popular business.

<@&1124784263754158090> — Players who have received a *tour guide hat* in the game.
"""
embedRolesEn.set_image(url=placeholderImageLink)
