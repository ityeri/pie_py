import nextcord
from nextcord import VoiceClient, SlashOption, Embed, VoiceChannel, FFmpegPCMAudio
from nextcord.ext import commands
from pytubefix import YouTube, Search
import time
from commonModule.embed_message import sendErrorEmbed
import os
import glob
import random
import asyncio
from typing import Callable, Awaitable

class GuildMismatchError(Exception): pass

class PlayMode:
    ONCE = 0
    LOOP = 1
    SHUFFLE = 2



class AudioFile:
    def __init__(self, path: str):
        self.audio: FFmpegPCMAudio | None = None
        self.path: str = path

    def new(self):
        self.audio = None
        self.audio = FFmpegPCMAudio(source=self.path, 
                                    executable="ffmpeg",
                                    options="-filter:a 'volume=0.7'")
    
    def delete(self): 
        del self.audio
        self.audio = None
        os.remove(self.path)

class GuildPlaylistManager:
    def __init__(self, guild: nextcord.Guild):
        self.guild: nextcord.Guild = guild
        self.voiceClient: nextcord.VoiceClient | None = guild.voice_client
        self.voiceChannel: nextcord.VoiceChannel | None = None
        self.isPlaying: bool = False

        self.audioIndex = None
        self.playlistAudioFiles: list[AudioFile] = list()
        self.playMode: int = None
        self.isFirstPlay: bool = False

        # self.stopCallback: Callable[[GuildPlaylistManager], Awaitable[None]] | None = None

    @property
    def isConnected(self) -> bool: return bool(self.voiceClient)

    async def connect(self, voiceChannel: nextcord.VoiceChannel):
        if self.voiceClient:
            raise RuntimeError("연결할수 없습니다. 이미 보이스 클라이언트가 접속해 있습니다")
        # elif self.voiceClient != voiceChannel.guild.id:
        #     raise GuildMismatchError("연결할수 없습니다. 보이스 클라이언트가 속한 길드와 연결하고자 하는 길드가 다릅니다")



        await voiceChannel.connect()
        self.isPlaying = False
        self.voiceClient = voiceChannel.guild.voice_client
        self.voiceChannel = voiceChannel

    def play(self, stopCallback: Callable[['GuildPlaylistManager'], Awaitable[None]]=None, startAudioIndex: int=0):
        # self.stopCallback = stopCallback
        self.isPlaying = True
        self.isFirstPlay = True
        self.audioIndex = startAudioIndex
        self.loop()

    def loop(self, error=None):
        '''
        이 코드는 기본적으로 self.playMode 가 ONCE 라 가정하고 실행됨
        '''
        if not self.isConnected: raise RuntimeError("재생할수 없습니다. 음성채널에 연결되어 있지 않습니다")
        if not self.isPlaying: return # self.voiceClient.stop 에 의해 강제 중지 됬을경우 무한 실행 방지


        if error: 
            print(f'================\n재생중 에러 발생!\n==================\n{error}')
            # 솔직히 에러 별로 안중요할듯 암튼 그럼
            # asyncio.run(self.stop())
            # return


        # 다음 음악
        if self.isFirstPlay: self.isFirstPlay = False
        else:
            match self.playMode:
                case PlayMode.ONCE: 
                    self.audioIndex += 1
                
                case PlayMode.LOOP:
                    self.audioIndex += 1
                    if self.audioIndex == len(self.playlistAudioFiles):
                        self.audioIndex = 0
                
                case PlayMode.SHUFFLE:
                    nextSongIndex = self.audioIndex

                    while nextSongIndex == self.audioIndex:
                        nextSongIndex = random.randrange(0, len(self.playlistAudioFiles))
                    
                    self.audioIndex = nextSongIndex
                
                case _: raise ValueError("올바른 재생방식이 아닙니다.")

        if len(self.voiceChannel.members) == 0:
            asyncio.run(self.stop())
            return

        elif self.playMode == PlayMode.ONCE and self.audioIndex == len(self.playlistAudioFiles):
            asyncio.run(self.stop())
            return
        



        audioFile: AudioFile = self.playlistAudioFiles[self.audioIndex]
        audioFile.new()

        time.sleep(1)

        self.voiceClient.play(audioFile.audio, after=self.loop)

    def skip(self):
        if not self.isConnected: raise RuntimeError("봇이 연결한 상태에세 스깁해야함")
        elif not self.isPlaying: raise RuntimeError("재생중인 상태에서 스킵해야함")

        while not self.voiceClient.is_playing(): ...
        self.voiceClient.stop()

    async def stop(self):
        self.isPlaying = False
        if not self.voiceClient.is_playing(): time.sleep(1)
        self.voiceClient.stop()

        # 원래 콜백합수 입력받을라 했는데 안되서 stop 내에 걍 disconnect 내장 할라다가 안되서
        # 걍 연결 끊는 기능을 내장했는데 안되서 걍 암것도 안할거임
        # 결론: stop 만으론 음성챛방에선 안나감 걍

        # if self.stopCallback is not None:
        #     await self.stopCallback(self)

        # await self.disconnect()

        # await self.voiceClient.disconnect()
        # self.voiceClient = None
        # self.voiceChannel = None

    async def disconnect(self):
        if not self.isConnected:
            raise RuntimeError("연결 해제를 할수 없습니다. 연결되어 있지 않습니다")
        
        await self.voiceClient.disconnect()
        self.voiceClient = None
        self.voiceChannel = None

    def clearPlaylist(self):
        if self.isPlaying: raise RuntimeError("플레이리스트릴 비울수 없습니다. 플레이리스트가 재생중입니다")
        
        for audioFile in self.playlistAudioFiles:
            audioFile.delete()
            del audioFile
        
        self.playlistAudioFiles = list()

    def addAudio(self, audioFile: AudioFile): self.playlistAudioFiles.append(audioFile)



# async def stopCallback(manager: GuildPlaylistManager): await manager.disconnect()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.guildPlaylistManagers: dict[int, GuildPlaylistManager] = dict()

        # musics 폴더에 남은 임시 파일 삭제
        for filePath in glob.glob("musics/*.m4a"):
            os.remove(filePath)

    

    @nextcord.slash_command(name="재생", description="유튜브에서 영상을 찾아 재생합니다")
    async def play(self, interaction: nextcord.Interaction,
                   keyword: str = SlashOption(name="주소or검색어", description="유튜브 영상의 주소 또는 검색어를 입력해 주세요")):
        
        # 사용자 연결 여부 체크
        if (userVoiceChannel := await self.checkConnectedChannel(interaction)) is None: return

        #봇의 연결 여부 체크
        voiceClient = interaction.guild.voice_client
        guild = interaction.guild

        # 봇이 연결 안됬을 경우
        if voiceClient is None:
            playlistManager = self.newPlaylistManager(guild)
            await playlistManager.connect(userVoiceChannel)
        
        # 봇이 연결 되어 있을 경우
        else:
            playlistManager = self.getPlaylistManager(guild)
            
            # 사용자와 서로 다른 음성 채널일경우
            if userVoiceChannel.id != playlistManager.voiceChannel.id:


                # 봇이 접속한 체널에 이미 사람이 있을경우
                if len(playlistManager.voiceChannel.members) > 1: # 자기 자신도 인원으로 잡힘
                    await sendErrorEmbed(interaction, "GuildMismatchError!!!", 
                        "봇이 이미 다른 음성채널에 있습니다!\n봇이 위치한 채널의 사람이 빈 후에 사용해 주세요.")
                    return
                
                # 봇이 접속한 채널에 사람이 없을경우
                else:
                    playlistManager = self.getPlaylistManager(guild)
                    await playlistManager.stop()
                    await playlistManager.disconnect()
                    playlistManager.clearPlaylist()
                    await playlistManager.connect(userVoiceChannel)
            
            # 같은 음성채널이면
            else:
                playlistManager = self.getPlaylistManager(guild)



        # 주소, 또는 검색어 적합성 체크

        # 입력이 url 이라면
        if 'youtube.com' in keyword:
            url = keyword
            try: yt = YouTube(url)
            except:
                await sendErrorEmbed(interaction, "BadLinkError!!!", "올바른 URL 이나 검색어를 입력해 주세요")
                return
        # 입력이 검색어라면
        else:
            try:
                search = Search(keyword)
                yt = search.videos[0]
            except:
                await sendErrorEmbed(interaction, "BadKeywordError!!!", f"검색어 `{keyword}`\n에 대한 검색 결과가 없습니다")
                return
        
        await interaction.response.defer()
        
        audioFileName = f'{time.time()}'.replace('.', '_')
        audioStream = yt.streams.filter(only_audio=True).first()
        audioStream.download(output_path="musics/", filename=audioFileName)
        
        embed = Embed(title=f'검색된 영상 \n```{yt.title}``` \n영상을 플레이 리스트에 추가했습니다!', description=f'길이: {yt.length//60}분 {yt.length%60}초')
        embed.set_image(yt.thumbnail_url)

        await interaction.followup.send(embed=embed)



        audioFilePath = f"musics/{audioFileName}.m4a"
        playlistManager.addAudio(AudioFile(audioFilePath))
        playlistManager.playMode = PlayMode.ONCE
        if playlistManager.isPlaying is False: playlistManager.play()



    @nextcord.slash_command(name="재생방식", description="음악을 재생하는 방식을 정합니다")
    async def playMode(self, interaction: nextcord.Interaction,
                       playMode: str = SlashOption(name="재생방식", choices=["무한반복", "한번씩", "무작위"])):
        if (voiceChannel := await self.checkConnectedChannel(interaction)) == None: return


        if (playlistManager := self.getPlaylistManager(interaction.guild)).isPlaying is False:
            await interaction.send("음성 채널에서 해당 기능을 사용중이지 않습니다")
            return


        match(playMode):
            case "한번씩":
                playlistManager.playMode = PlayMode.ONCE
                await interaction.send(f'이제부터 음악을 한번씩 차례로 재생합니다!')
                return
            case "무한반복":
                playlistManager.playMode = PlayMode.LOOP
                await interaction.send(f'이제부터 음악을 차례대로 계속 재생합니다!')
                return
            case "무작위":
                playlistManager.playMode = PlayMode.SHUFFLE
                await interaction.send(f'이제부터 음악을 무작위로 계속 재생합니다!')
                return



    @nextcord.slash_command(name="스킵", description="음악 하나를 스킵합니다")
    async def skip(self, interaction: nextcord.Interaction): 
        # 사용자 연결 여부 체크
        if (userVoiceChannel := await self.checkConnectedChannel(interaction)) is None: return

        #봇의 연결 여부 체크
        voiceClient = interaction.guild.voice_client
        guild = interaction.guild

        # 봇이 연결 안됬을 경우
        if voiceClient is None:
            sendErrorEmbed(interaction, "RuntimeError!!!", "재생 기능을 사용중이지 않습니다")
            return

        # 봇이 연결 되어 있을 경우
        else:
            playlistManager = self.getPlaylistManager(guild)
            
            # 사용자와 서로 다른 음성 채널일경우
            if userVoiceChannel.id != playlistManager.voiceChannel.id:
                await sendErrorEmbed(interaction, "ChannelMismatchError!!!", 
                    "봇과 동일한 음성 채팅방에 연결한 상태로 이 기능을 사용해 주세요")
                return

            # 같은 음성채널이면
            else:
                playlistManager = self.getPlaylistManager(guild)
        
        playlistManager.skip()

        await interaction.send("음악을 스킵했습니다!")



    @nextcord.slash_command(name="정지", description="음악 재생을 중지합니다")
    async def stop(self, interaction: nextcord.Interaction):
        # 사용자 연결 여부 체크
        if (userVoiceChannel := await self.checkConnectedChannel(interaction)) is None: return

        #봇의 연결 여부 체크
        voiceClient = interaction.guild.voice_client
        guild = interaction.guild

        # 봇이 연결 안됬을 경우
        if voiceClient is None:
            sendErrorEmbed(interaction, "RuntimeError!!!", "재생 기능을 사용중이지 않습니다")
            return

        # 봇이 연결 되어 있을 경우
        else:
            playlistManager = self.getPlaylistManager(guild)
            
            # 사용자와 서로 다른 음성 채널일경우
            if userVoiceChannel.id != playlistManager.voiceChannel.id:
                await sendErrorEmbed(interaction, "ChannelMismatchError!!!", 
                    "봇과 동일한 음성 채팅방에 연결한 상태로 이 기능을 사용해 주세요")
                return

            # 같은 음성채널이면
            else:
                playlistManager = self.getPlaylistManager(guild)
        
        await playlistManager.stop()
        await playlistManager.disconnect()

        await interaction.send("음악 재생을 정지했습니다!")



    def newPlaylistManager(self, guild: nextcord.Guild) -> GuildPlaylistManager:
        if self.isManagerExist(guild): raise ValueError("매니저를 만들수 없습니다. 해당 매니저가 이미 존해합니다")
        self.guildPlaylistManagers[guild.id] = GuildPlaylistManager(guild)
        return self.guildPlaylistManagers[guild.id]

    def getPlaylistManager(self, guild: nextcord.Guild) -> GuildPlaylistManager:
        if not self.isManagerExist(guild): KeyError("매니저를 가져올수 없습니다. 해당 매니저가 존재하지 않습니다")
        return self.guildPlaylistManagers[guild.id]

    def isManagerExist(self, guild: nextcord.Guild) -> bool: guild.id in self.guildPlaylistManagers

    async def checkConnectedChannel(self, interaction: nextcord.Interaction) -> VoiceChannel | None:
        try:
            voiceChannel = interaction.user.voice.channel
        except AttributeError:
            await sendErrorEmbed(interaction, "NotConnectToChannelError!!!", "음성 체널에 접속한 상태로 이 명령어를 사용해 주세요")
            return None
        

        
        return voiceChannel
    
    # async def checkUsingPlaylist(self): ...



def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))