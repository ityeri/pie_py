import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
import requests
from bs4 import BeautifulSoup, Tag
from random import randint
from PIL import Image
from io import BytesIO
import urllib.parse

# TODO: 그 뭐냐 75번 줄에 url 이랑 검색어 길이 이슈 해결


def searchImageLinks(keyword: str):
    url = f"https://www.google.com/search?q={keyword}&udm=2"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers, timeout=3)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    imgLinks: list[Tag] | None = soup.findAll('img', class_="DS1iW")

    if imgLinks == None or imgLinks[0] == None:
        return []
    else: return [imgLink.get('src') for imgLink in imgLinks]



class ImageSearch(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @nextcord.slash_command(name='사진검색', description="입력된 검색어를 구글에서 사진으로 검색 해옵니다")
    async def search(self, interaction: nextcord.Interaction, 
                   keyword: str = SlashOption(name='검색어', description="검색어를 여기에 입력하세요")):

        try:
            imgLinks = searchImageLinks(urllib.parse.quote(keyword))
            if len(imgLinks) == 0:
                await interaction.send(embed=nextcord.Embed(
                    title="**SearchNotFoundError!!!**\n`이 에러를 봤다면 봇이 뭔가 고장난거임`", color=0xff0000))
                return
            imgLink = imgLinks[0]
            response = requests.get(imgLink, timeout=3)
        except TimeoutError:
            await interaction.send(embed=nextcord.Embed(title="**TimeoutError!!!**\n구글에서 이미지를 너무 늦게 줍니다!", color=0xff0000))
            return
        except:
            await interaction.send(embed=nextcord.Embed(title="**UnknowError!!!**", color=0xff0000))
            return



        image = Image.open(BytesIO(response.content))
        if image.size[0] > image.size[1]:
            ratio = 1000 / image.size[0]
        else: ratio = 1000 / image.size[1]
        
        image = image.resize((int(image.size[0]*ratio), 
                      int(image.size[1]*ratio)))

        byteArray = BytesIO()

        image.save(byteArray, format='PNG')
        byteArray.seek(0)

        file = nextcord.File(byteArray, "image.png")

        # 디코 api 글자수 제한 이슈 (url, 키워드 총합 200 글자 아래로 맞춤)

        # 둘다 각각 200을 넘을때 -> 링크 삭제하고 검색어 잘라냄
        if 200 < len(keyword) and 200 < len(imgLink): 
            cutLength = len(keyword)-200

            embed = nextcord.Embed(
                title=f'```{keyword[0:200]}```\n...(+{cutLength}글자)\n의 이미지 검색결과!\n~~(사진 링크는 너무 길어요)~~', 
                color=0x00ff00,)\
                .set_image('attachment://image.png')
        
        # 링크가 200 안넘는데 총합은 넘으면 -> 검색어 잘라냄
        elif len(imgLink) <= 200 and 200 < len(keyword) + len(imgLink):
            extraLength = 200 - len(imgLink)
            cutLength = len(keyword)-200

            embed = nextcord.Embed(
                title=f'```{keyword[0:extraLength]}```\n...(+{cutLength}글자)\n의 이미지 검색결과!\n{imgLink}', 
                color=0x00ff00,)\
                .set_image('attachment://image.png')

        
        else: 
            embed = nextcord.Embed(title=f'```{keyword}```\n의 이미지 검색결과!\n{imgLink}', color=0x00ff00)\
                .set_image('attachment://image.png')
        
        await interaction.response.defer()
        await interaction.followup.send(embed=embed, file=file)

def setup(bot: commands.Bot):
    bot.add_cog(ImageSearch(bot))