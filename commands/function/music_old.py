import nextcord
from nextcord import VoiceClient, SlashOption, Embed, VoiceChannel
from nextcord.ext import commands
from pytubefix import YouTube, Search
import time
from commonModule.embed_message import sendErrorEmbed
import os
import glob
import random
import asyncio

class PlayMode:
    ONCE = 0
    LOOP = 1
    SHUFFLE = 2

class Playlist:
    def __init__(self, voiceClient: VoiceClient, voiceChannel: VoiceChannel):
        self.client: VoiceClient = voiceClient
        self.channel: VoiceChannel = voiceChannel

        self.beforeAudioFilePath: str = None

        self.audioPaths: list[str] = list()
        self.audioSources: dict[str, nextcord.FFmpegPCMAudio] = dict()
        
        self.songIndex: int = 0
        self.isPlaying: bool = False
        self.playMode: int = PlayMode.ONCE

    def start(self):
        '''
        이 함수는 봇이 음성 체널에 연결한 상태에서 실행되어야 함
        '''
        self.isPlaying = True
        self.playMode: int = PlayMode.ONCE
        self.songIndex = -1 # play 메서드에서 songIndex 바꾸는 순서 땜에 이렇게 함
        self.play()



    def play(self, error=None):
        '''
        이 코드는 기본적으로 self.playMode 가 ONCE 라 가정하고 실행됨
        '''

        match self.playMode:
            case PlayMode.ONCE: self.songIndex += 1
            case PlayMode.LOOP:
                self.songIndex += 1
                if self.songIndex == len(self.audioPaths):
                    self.songIndex = 0
            case PlayMode.SHUFFLE: self.songIndex = random.randrange(0, len(self.audioPaths))

        if error:
            print(f'================\n재생중 에러 발생!\n==================\n{error}')
            asyncio.run(self.stop())
            return
        
        if len(self.channel.members) == 0:
            asyncio.run(self.stop())
            return

        if not self.isPlaying:
            asyncio.run(self.stop())
            return

        if self.playMode == PlayMode.ONCE and self.songIndex == len(self.audioPaths):
            asyncio.run(self.stop())
            return


        audioFilePath = self.audioPaths[self.songIndex]
        audioSource = self.audioSources[audioFilePath]


        time.sleep(1)

        self.client.play(audioSource, after=self.play)


    async def stop(self):
        if self.isPlaying == False: raise RuntimeError("정지할수 없음. 플레이 리스트가 재생중이지 않습니다") 
        self.isPlaying = False
        
        if self.client.is_playing(): self.client.stop()
        await self.client.disconnect()

        for audioFilePath in self.audioPaths:
            os.remove(audioFilePath)


    def addSong(self, audioFilePath: str):
        self.audioPaths.append(audioFilePath)

        self.audioSources[audioFilePath] = nextcord.FFmpegPCMAudio(source=audioFilePath, executable="ffmpeg",
                                                                   options="-filter:a 'volume=0.7'")
        
    def setPlayMode(self, playMode: int):
        self.playMode = playMode
    
    def skip(self):
        
        if self.isPlaying == True:
            while not self.client.is_playing():
                self.client.stop()
        
        else: raise RuntimeError("스킵할수 없음. 플레이 리스트가 재생중이지 않습니다") 





class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.playlists: dict[int, Playlist] = dict()

        # musics 폴더에 남은 임시 파일 삭제
        for filePath in glob.glob("musics/*.m4a"):
            os.remove(filePath)

    

    @nextcord.slash_command(name="재생", description="유튜브에서 영상을 찾아 재생합니다")
    async def play(self, interaction: nextcord.Interaction,
                   keyword: str = SlashOption(name="주소or검색어", description="유튜브 영상의 주소 또는 검색어를 입력해 주세요")):
        
        try:
            voiceChannel = interaction.user.voice.channel
        except AttributeError:
            await sendErrorEmbed(interaction, "NotConnectToChannelError!!!", "음성 체널에 접속한 상태로 이 명령어를 사용해 주세요")
            return
        
        await interaction.response.defer()

        # 영상 가져오기
        if 'youtube.com' in keyword:
            url = keyword
            try: yt = YouTube(url)
            except:
                await sendErrorEmbed(interaction, "BadLinkError!!!", "올바른 URL 이나 검색어를 입력해 주세요", followup=True)
                return
        else:
            try:
                search = Search(keyword)
                yt = search.videos[0]
            except:
                await sendErrorEmbed(interaction, "BadKeywordError!!!", f"검색어 `{keyword}`\n에 대한 검색 결과가 없습니다", followup=True)
                return
        
        audioFileName = f'{time.time()}'.replace('.', '_')
        audioStream = yt.streams.filter(only_audio=True).first()
        audioStream.download(output_path="musics/", filename=audioFileName)
        
        embed = Embed(title=f'검색된 영상 \n```{yt.title}``` \n영상을 플레이 리스트에 추가했습니다!', description=f'길이: {yt.length//60}분 {yt.length%60}초')
        embed.set_image(yt.thumbnail_url)

        await interaction.followup.send(embed=embed)



        audioFilePath = f"musics/{audioFileName}.m4a"
        # 봇이 이미 해당 채널에 있는지 확인ㄷ
        if self.isConnectVoiceChannel(voiceChannel):
            # 이미 채널에 접속해 있으면
            self.addSong(voiceChannel.id, audioFilePath)
        else:
            # 채널에 접속 아직 안했으면 
            await voiceChannel.connect()

            voiceClient: VoiceClient = interaction.guild.voice_client # 봇 음성 클라이언트 가져오기
            playlist = self.initPlaylist(voiceClient, voiceChannel) # 플리 생성
            
            self.addSong(voiceChannel.id, audioFilePath)
            playlist.start()



    @nextcord.slash_command(name="재생방식", description="음악을 재생하는 방식을 정합니다")
    async def playMode(self, interaction: nextcord.Interaction,
                       playMode: str = SlashOption(name="재생방식", choices=["무한반복", "한번씩", "무작위"])):
        try:
            voiceChannel = interaction.user.voice.channel
        except AttributeError:
            await sendErrorEmbed(interaction, "NotConnectToChannelError!!!", "음성 체널에 접속한 상태로 이 명령어를 사용해 주세요")
            return


        if not self.getPlaylist(voiceChannel.id).isPlaying:
            await interaction.send("음성 채널에서 재생 기능을 사용중이지 않습니다")
            return


        match(playMode):
            case "한번씩":
                self.getPlaylist(voiceChannel.id).setPlayMode(PlayMode.ONCE)
                await interaction.send(f'이제부터 음악을 한번씩 차례로 재생합니다!')
                return
            case "무한반복":
                self.getPlaylist(voiceChannel.id).setPlayMode(PlayMode.LOOP)
                await interaction.send(f'이제부터 음악을 차례대로 계속 재생합니다!')
                return
            case "무작위":
                self.getPlaylist(voiceChannel.id).setPlayMode(PlayMode.SHUFFLE)
                await interaction.send(f'이제부터 음악을 무작위로 계속 재생합니다!')
                return



    @nextcord.slash_command(name="스킵", description="음악 하나를 스킵합니다")
    async def skip(self, interaction: nextcord.Interaction): ...



    @nextcord.slash_command(name="정지", description="음악 재생을 중지하고 음성체널에서 나갑니다")
    async def stop(self, interaction: nextcord.Interaction):
        try:
            voiceChannel = interaction.user.voice.channel
        except AttributeError:
            await sendErrorEmbed(interaction, "NotConnectToChannelError!!!", "음성 체널에 접속한 상태로 이 명령어를 사용해 주세요")
            return

        try:
            await self.getPlaylist(voiceChannel.id).stop()
        except KeyError: 
            await interaction.send("음성 채널에서 재생 기능을 사용중이지 않습니다")
            return
        
        self.deletPlaylist(voiceChannel.id)

        await interaction.send("재생을 중지 했습니다!")




    def initPlaylist(self, voiceClient: VoiceClient, voiceChannel: VoiceChannel) -> Playlist:
        self.playlists[voiceChannel.id] = Playlist(voiceClient, voiceChannel)
        return self.playlists[voiceChannel.id]
    
    def deletPlaylist(self, voiceChannelId: int) -> list[nextcord.FFmpegPCMAudio]:
        try: del self.playlists[voiceChannelId]
        except: raise KeyError(f"서버 id: {voiceChannelId} 를 플레이 리스트에서 찾을수 없습니다")
    
    def getPlaylist(self, voiceChannelId: int) -> Playlist:
        try:
            return self.playlists[voiceChannelId]
        except:
            raise KeyError(f"서버 id: {voiceChannelId} 를 플레이리스트에서 찾을수 없습니다")

    def addSong(self, voiceChannelId: int, audioFilePath: str):
        self.getPlaylist(voiceChannelId).addSong(audioFilePath)
    


    def isConnectVoiceChannel(self, voiceChannel: VoiceChannel) -> bool:
        for voiceClient in self.bot.voice_clients:
            if voiceClient.channel == voiceChannel:
                return True
            
        return False
    
    async def checkConnectedChannel(self, interaction: nextcord.Interaction) -> VoiceChannel | None:
        try:
            voiceChannel = interaction.user.voice.channel
        except AttributeError:
            await sendErrorEmbed(interaction, "NotConnectToChannelError!!!", "음성 체널에 접속한 상태로 이 명령어를 사용해 주세요")
            return None
        
        return voiceChannel
    
    # async def checkUsing



def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))