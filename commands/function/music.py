import nextcord
from nextcord import SlashOption, Embed, FFmpegPCMAudio
from nextcord.ext import commands
import pytubefix
from pytubefix import YouTube, Search
import time

import pytubefix.exceptions
from commonModule.embed_message import sendErrorEmbed
import os
import glob
import random  
import asyncio          
from typing import Callable, Awaitable

class UserNotConnectedError(Exception): pass
class BotNotConnectedError(Exception): pass
class ChannelMismatchError(Exception): pass

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
        self.audio.cleanup()
        try: self.audio.read()
        except: ...

        del self.audio
        self.audio = None
        os.remove(self.path)

class YoutubeAudioFile(AudioFile):
    def __init__(self, path, yt):
        super().__init__(path)
        self.yt: YouTube = yt



class GuildPlaylistManager:
    def __init__(self, guild: nextcord.Guild):
        self.guild: nextcord.Guild = guild
        self.voiceClient: nextcord.VoiceClient | None = guild.voice_client
        self.voiceChannel: nextcord.VoiceChannel | None = None
        self.isPlaying: bool = False

        self.eventLoop: asyncio.AbstractEventLoop = None

        self.audioIndex = None
        self.playlistAudioFiles: list[YoutubeAudioFile] = list()
        self.playMode: int = None
        self.isFirstPlay: bool = False

        self.stopCallback: Callable[[GuildPlaylistManager], Awaitable[None]] | None = None

    @property
    def isConnected(self) -> bool: 
        if self.voiceClient is not None:
            # disconnect 메서드와 동기 비동기 뭐시기 하면서 꼬이는거 방지하기 위함
            return True
            # return self.voiceClient.is_connected()
        else: return False

    async def connect(self, voiceChannel: nextcord.VoiceChannel):
        if self.voiceClient and self.voiceClient.is_connected():
            raise RuntimeError("연결할수 없습니다. 이미 보이스 클라이언트가 접속해 있습니다")



        await voiceChannel.connect()
        self.isPlaying = False
        self.voiceClient = voiceChannel.guild.voice_client
        self.voiceChannel = voiceChannel

    def play(self, eventLoop: asyncio.AbstractEventLoop, stopCallback: Callable[['GuildPlaylistManager'], Awaitable[None]]=None, startAudioIndex: int=0):
        if not self.isConnected: raise RuntimeError("재생할수 없습니다. 음성채널에 연결되어 있지 않습니다")
        self.stopCallback = stopCallback
        self.isPlaying = True
        self.isFirstPlay = True
        self.audioIndex = startAudioIndex
        self.eventLoop = eventLoop
        self.loop()
    
    
    def next(self) -> bool:
        '''
        self.playMode 에 따라 다음 음악을 설정하고, 재생의 중지 여부를 반환함 (True 일 경우 중지)
        '''
        if self.isFirstPlay: self.isFirstPlay = False 
        else:
            match self.playMode:
                case PlayMode.ONCE: 
                    self.audioIndex += 1

                    if self.audioIndex == len(self.playlistAudioFiles):
                        return True
                    
                    else: return False

                
                case PlayMode.LOOP:
                    self.audioIndex += 1
                    if self.audioIndex == len(self.playlistAudioFiles):
                        self.audioIndex = 0
                    
                    return False
                
                case PlayMode.SHUFFLE:
                    nextSongIndex = self.audioIndex

                    while nextSongIndex == self.audioIndex:
                        nextSongIndex = random.randrange(0, len(self.playlistAudioFiles))
                    
                    self.audioIndex = nextSongIndex

                    return False
                
                case _: raise ValueError("올바른 재생방식이 아닙니다.")

    def loop(self, error=None):
        if not self.isPlaying: return # self.voiceClient.stop 에 의해 강제 중지 됬을경우 무한 실행 방지


        if error: 
            print(f'================\n재생중 에러 발생!\n==================\n{error}')

        # 다음 음악
        if self.next():
            self.stop()
            return

        elif len(self.voiceChannel.members) == 0:
            self.stop()
            return

        audioFile: AudioFile = self.playlistAudioFiles[self.audioIndex]
        audioFile.new()

        self.voiceClient.play(audioFile.audio, after=self.loop)

    def skip(self):
        if not self.isConnected: raise RuntimeError("봇이 연결한 상태에세 스깁해야함")
        elif not self.isPlaying: raise RuntimeError("재생중인 상태에서 스킵해야함")

        while not self.voiceClient.is_playing(): ...
        self.voiceClient.stop()

    def stop(self):
        self.isPlaying = False
        if not self.voiceClient.is_playing(): time.sleep(1)
        self.voiceClient.stop()

        self.stopCallback(self)

    def disconnect(self):
        if not self.isConnected:
            raise RuntimeError("연결 해제를 할수 없습니다. 연결되어 있지 않습니다")


        self.eventLoop.create_task(self.voiceClient.disconnect())
        self.voiceClient = None
        self.voiceChannel = None


    def clearPlaylist(self):
        if self.isPlaying: raise RuntimeError("플레이리스트릴 비울수 없습니다. 플레이리스트가 재생중입니다")
        
        for audioFile in self.playlistAudioFiles:
            audioFile.delete()
            del audioFile
        
        self.playlistAudioFiles = list()

    def addAudio(self, audioFile: YoutubeAudioFile): 
        if audioFile.yt.video_id in [audioFile.yt.video_id for audioFile in self.playlistAudioFiles]:
            raise ValueError("같은 id 의 오디오를 2개 이상 넣을수 없습니다!")
        self.playlistAudioFiles.append(audioFile)

    def setPlayMode(self, mode: int): self.playMode = mode

def stopCallback(manager: GuildPlaylistManager): 
    print("정지 콜백 호츌")
    manager.disconnect()
    manager.clearPlaylist()



class PlaylistManager:
    def __init__(self):
        self.guildPlaylistManagers: dict[int, GuildPlaylistManager] = dict()

    def newPlaylistManager(self, guild: nextcord.Guild) -> GuildPlaylistManager:
        if self.isManagerExist(guild): raise ValueError("매니저를 만들수 없습니다. 해당 매니저가 이미 존해합니다")
        self.guildPlaylistManagers[guild.id] = GuildPlaylistManager(guild)
        return self.guildPlaylistManagers[guild.id]

    def getPlaylistManager(self, guild: nextcord.Guild) -> GuildPlaylistManager:
        if not self.isManagerExist(guild): KeyError("매니저를 가져올수 없습니다. 해당 매니저가 존재하지 않습니다")
        return self.guildPlaylistManagers[guild.id]

    def isManagerExist(self, guild: nextcord.Guild) -> bool: return guild.id in self.guildPlaylistManagers

    def availabilityCheck(self, interaction: nextcord.Interaction):
        userGuild = interaction.guild
        userVoice = interaction.user.voice


        # 사용자 연결 여부 체크

        if userVoice is not None: # 사용자는 연결 되었을 경우
            userVoiceChannel = userVoice.channel

            # 봇의 연결 여부 (기능 사용 여부) 체크 + 길드 일치 여부 체크
            # 봇이 연결 되었고 사용 가능 하다면
            if self.isManagerExist(userGuild) and (manager := self.getPlaylistManager(userGuild)).isPlaying:

                # 음성채널 일치 여부 체크 (길드 일치여부는 위에서 이미 처리됨!)
                botVoiceChannel = manager.voiceChannel

                # 봇과 유저의 위치가 일치하다면
                if botVoiceChannel.id == userVoiceChannel.id: "ㅇㅋㅇㅋ 굳"
                # 봇과 유저의 위치가 다르다면
                else: raise ChannelMismatchError


            # 봇이 연결되지 않았고 사용 불가능 하다면
            else: raise BotNotConnectedError


        else: # 사용자가 연결하지 않았을경우
            raise UserNotConnectedError

    # async def checkConnectedChannel(self, interaction: nextcord.Interaction) -> VoiceChannel | None:
        # try:
        #     voiceChannel = interaction.user.voice.channel
        # except AttributeError:
        #     await sendErrorEmbed(interaction, "NotConnectToChannelError!!!", "음성 체널에 접속한 상태로 이 명령어를 사용해 주세요")
        #     return None
        
        # return voiceChannel



async def downloadVideoTimeout(stream: pytubefix.Stream, outputPath: str):
    def downloadVideo(stream: pytubefix.Stream, outputPath, filename):
        try:
            stream.download(output_path=outputPath, filename=filename)
        except Exception as e:
            print(f"Error during download: {e}")
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, downloadVideo, stream, *os.path.split(outputPath))
    except asyncio.TimeoutError: "ㅣㅣㅣㅣㅣㅣㅖㅖㅖㅖㅖㅖㅖㅖㅖㅖㅖㅔㅔㅔㅔㅔㅔㅔㅔㅔㅔㅔ!!!!!!!!!!!!"



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.playlistManager: PlaylistManager = PlaylistManager()

        # musics 폴더에 남은 임시 파일 삭제
        for filePath in glob.glob("musics/*.m4a"):
            os.remove(filePath)



    @nextcord.slash_command(name="재생", description="유튜브에서 영상을 찾아 재생합니다")
    async def play(self, interaction: nextcord.Interaction,
                   keyword: str = SlashOption(name="주소or검색어", description="유튜브 영상의 주소 또는 검색어를 입력해 주세요")):


        # 주소, 또는 검색어 적합성 체크

        # 입력이 url 이라면
        if 'youtube.com' in keyword or 'youtu.be' in keyword:
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


        
        # 사운드 파일이 저장될 경로를 지정하고 
        # 응답 지연 설정후 다운로드 시작
        await interaction.response.defer() # 다운로드엔 시간이 걸릴수 있기에 응답 지연 설정

        # 영상의 사용 가능성 체크 (아동용 아닌지, 외부 다운 막힌건 아닌지 등등) + 스트림 가져오기
        try: stream: pytubefix.Stream = yt.streams.filter(only_audio=True).first()

        except pytubefix.exceptions.VideoUnavailable:
            await sendErrorEmbed(interaction, "VideoSettingsError!!!", """해당 영상을 재생할수 없습니다!
영상이 아동용이거나, 업로더가 외부에서 영상을 다운받는것을 막아두었을수도 있습니다""", followup=True)
            return



        # 시간제한 걸고 영상 다운
        # "musics/시간.소수점시간.m4a" 형식의 경로 생성
        audioFilePath = f'musics/{time.time()}'.replace('.', '_') + '.m4a'

        try:
            await asyncio.wait_for(
                downloadVideoTimeout(stream=stream, outputPath=audioFilePath), timeout=10)
        
        except TimeoutError: # 다운로드 너무 오래 걸리면 막음
            await sendErrorEmbed(interaction, "VideoSettingsError!!!", """해당 영상이 너무 길거나 다운로드가 너무 오래 걸립니다!""", 
                                 followup=True)
            return



        # 사용자가 재생 기능을 사용할수 있는 환경에 있는지 확인
        # 이 부분에선, 사용 가능성만 체크 하며, 사용 가능하게 만들수 있는경우 그렇게 만들고
        # play 는 이 코드 부분에서 처리하지 않음
        try: self.playlistManager.availabilityCheck(interaction)

        except UserNotConnectedError:
            await sendErrorEmbed(interaction, "UserNotConnectedError", "음성 채널에 접속한 상태로 이 명령어를 사용해 주세요")
            return



        except BotNotConnectedError: 
            if not self.playlistManager.isManagerExist(interaction.guild):
                manager = self.playlistManager.newPlaylistManager(interaction.guild)
            else: manager = self.playlistManager.getPlaylistManager(interaction.guild)

            # interaction.user.voice.channel 가 None 이 아님이 윗줄에서 보장됨
            await manager.connect(interaction.user.voice.channel)



        except ChannelMismatchError:
            manager = self.playlistManager.getPlaylistManager(interaction.guild)

            # 봇이 위치한 음성 채팅방이 비었는지, 비지 않았는지 확인
            if 0 < len([None for memeber in manager.voiceChannel.members if not memeber.bot]):
                await sendErrorEmbed(interaction, "ChannelMismatchError", 
                               "봇과 일치하는 음성 채널에 접속하거나, 봇이 위치한 음성 체널이 모두 빌때까지 기다려 주세요")
                return
            
            # 봇이 위치한 채널이 비었다면 이동함
            else: 
                # manager.play 에서 stopCallback 이 입력되었음을 가정함
                # = manager.stop 을 할때 disconnect 도 같이 호출됨
                manager.stop()

                # disconnect 가 비동기 실행 이기에 때문에 연결 끊길때까지 대기 타야함
                # while 문으로다가 끊길때까지 기달라 했는데 코드 블로킹 되고 꼬여서 안됨;;
                await asyncio.sleep(1) # 대충 1초 정도 기다리면 적당함
                await manager.connect(interaction.user.voice.channel)



        else: # 그 어떤 전처리도 필요하지 않다면

            # 해당 길드에 대한 매니저가 존재하며, 정상적으로 사용중임이 보장됨
            manager = self.playlistManager.getPlaylistManager(interaction.guild)

        try: manager.addAudio(YoutubeAudioFile(audioFilePath, yt=yt))
        except ValueError:
            await sendErrorEmbed(interaction, "DuplicationError!!!", """이미 플레이 리스트에 해당 영상이 있습니다!""", 
                                 followup=True)
            return



        embed = Embed(title=f'검색된 영상 \n```{yt.title}``` \n영상을 플레이 리스트에 추가했습니다!', description=f'길이: {yt.length//60}분 {yt.length%60}초')
        embed.set_image(yt.thumbnail_url)
        embed.color = 0x9cdcfe

        await interaction.followup.send(embed=embed)

        # /재생 기능을 처음 사용한 경우
        if manager.isPlaying is False: 
            manager.playMode = PlayMode.ONCE
            manager.play(eventLoop=asyncio.get_event_loop(), stopCallback=stopCallback)



    @nextcord.slash_command(name="재생방식", description="음악을 재생하는 방식을 정합니다")
    async def playMode(self, interaction: nextcord.Interaction,
                       playMode: str = SlashOption(name="재생방식", choices=["무한반복", "한번씩", "무작위"])):
        
        try: self.playlistManager.availabilityCheck(interaction)
        except: 
            sendErrorEmbed(interaction, "RuntimeError!!!", "재생 기능을 사용 중이지 않거나\n 봇과 같은 음성 채팅방에 있지 않습니다")

        manager = self.playlistManager.getPlaylistManager(interaction.guild)


        match(playMode):
            case "한번씩":
                manager.setPlayMode(PlayMode.ONCE)
                await interaction.send(f'이제부터 음악을 한번씩 차례로 재생합니다!')
                return
            case "무한반복":
                manager.setPlayMode(PlayMode.LOOP)
                await interaction.send(f'이제부터 음악을 차례대로 계속 재생합니다!')
                return
            case "무작위":
                manager.setPlayMode(PlayMode.SHUFFLE)
                await interaction.send(f'이제부터 음악을 무작위로 계속 재생합니다!')
                return



    @nextcord.slash_command(name="스킵", description="음악 하나를 스킵합니다")
    async def skip(self, interaction: nextcord.Interaction): 
        try: self.playlistManager.availabilityCheck(interaction)
        except: 
            sendErrorEmbed(interaction, "RuntimeError!!!", "재생 기능을 사용 중이지 않거나\n 봇과 같은 음성 채팅방에 있지 않습니다")

        manager = self.playlistManager.getPlaylistManager(interaction.guild)

        manager.skip()

        await interaction.send("음악을 스킵했습니다!")



    @nextcord.slash_command(name="재생목록", description="현재 재생중인 재생 목록을 확인합니다")
    async def playlist(self, interaction: nextcord.Interaction):
        try: self.playlistManager.availabilityCheck(interaction)
        except: 
            sendErrorEmbed(interaction, "RuntimeError!!!", "재생 기능을 사용 중이지 않거나\n 봇과 같은 음성 채팅방에 있지 않습니다")

        manager = self.playlistManager.getPlaylistManager(interaction.guild)


        message = '## 현재 플레이 리스트: \n'

        for i, audioFile in enumerate(manager.playlistAudioFiles):
            message += f'{i+1}. `{audioFile.yt.title}`  |  길이: *{audioFile.yt.length//60}분 {audioFile.yt.length%60}초*'
            if i == manager.audioIndex: message += "  |  🔊 현재 재생중!"

            message += '\n'

        await interaction.send(message)



    @nextcord.slash_command(name="정지", description="음악 재생을 중지합니다")
    async def stop(self, interaction: nextcord.Interaction):
        try: self.playlistManager.availabilityCheck(interaction)
        except: 
            sendErrorEmbed(interaction, "RuntimeError!!!", "재생 기능을 사용 중이지 않거나\n 봇과 같은 음성 채팅방에 있지 않습니다")

        manager = self.playlistManager.getPlaylistManager(interaction.guild)
        
        manager.stop()

        await interaction.send("음악 재생을 정지했습니다!")





def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))