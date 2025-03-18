import asyncio
import glob
import os
import time

import nextcord
from nextcord import SlashOption, Embed
from nextcord.ext import commands

import pytubefix
import pytubefix.exceptions
from pytubefix import YouTube, Search

# import pytube
# import pytube.exceptions

from common_module.embed_message import send_error_embed, Color
from commands.function.music_tools import *


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.playlist_manager: PlaylistManager = PlaylistManager(self.bot)

        # musics 폴더에 남은 임시 파일 삭제
        for file_path in glob.glob("musics/*.m4a"):
            os.remove(file_path)



    @nextcord.slash_command(name="재생", description="유튜브에서 영상을 찾아 재생합니다")
    async def play(self, interaction: nextcord.Interaction,
                   keyword: str = SlashOption(name="주소or검색어", description="유튜브 영상의 주소 또는 검색어를 입력해 주세요")):


        # 주소, 또는 검색어 적합성 체크

        # 입력이 url 이라면
        if 'youtube.com' in keyword or 'youtu.be' in keyword:
            url = keyword
            try: yt = YouTube(url)
            except:
                await send_error_embed(interaction, "BadLinkError!!!", "올바른 URL 이나 검색어를 입력해 주세요")
                return

        # 입력이 검색어라면
        else:
            try:
                search = Search(keyword)
                yt = search.videos[0]
            except:
                await send_error_embed(interaction, "BadKeywordError!!!", f"검색어 `{keyword}`\n에 대한 검색 결과가 없습니다")
                return



        # 사운드 파일이 저장될 경로를 지정하고 
        # 응답 지연 설정후 다운로드 시작
        await interaction.response.defer() # 다운로드엔 시간이 걸릴수 있기에 응답 지연 설정

        # 영상의 사용 가능성 체크 (아동용 아닌지, 외부 다운 막힌건 아닌지 등등) + 스트림 가져오기
        try: stream: pytubefix.Stream = yt.streams.filter(only_audio=True, abr="128kbps").first()

        except pytubefix.exceptions.VideoUnavailable:
            await send_error_embed(interaction, "VideoSettingsError!!!", """해당 영상을 재생할수 없습니다!
영상이 아동용이거나, 업로더가 외부에서 영상을 다운받는것을 막아두었을수도 있습니다""", followup=True)
            return



        # 시간제한 걸고 영상 다운
        # "musics/시간_소수점시간.m4a" 형식의 경로 생성
        audio_file_path = f'musics/{time.time()}'.replace('.', '_') + '.m4a'

        try:
            await asyncio.wait_for(
                download_video_timeout(stream=stream, output_path=audio_file_path), timeout=10)
        except TimeoutError: # 다운로드 너무 오래 걸리면 막음
            await send_error_embed(interaction, "VideoSettingsError!!!", """해당 영상이 너무 길거나 다운로드가 너무 오래 걸립니다!""",
                                   followup=True)
            return



        # 사용자가 재생 기능을 사용할수 있는 환경에 있는지 확인
        # 이 부분에선, 사용 가능성만 체크 하며, 사용 가능하게 만들수 있는경우 그렇게 만들고
        # play 는 이 코드 부분에서 처리하지 않음
        try: self.playlist_manager.availability_check(interaction)

        except UserNotConnectedError:
            await send_error_embed(interaction, "UserNotConnectedError", "음성 채널에 접속한 상태로 이 명령어를 사용해 주세요")
            return



        except BotNotConnectedError:
            if not self.playlist_manager.is_manager_exist(interaction.guild):
                manager = self.playlist_manager.new_playlist_manager(interaction.guild)
            else: manager = self.playlist_manager.get_playlist_manager(interaction.guild)

            # interaction.user.voice.channel 가 None 이 아님이 윗줄에서 보장됨
            await manager.connect(interaction.user.voice.channel)



        except ChannelMismatchError:
            manager = self.playlist_manager.get_playlist_manager(interaction.guild)

            # 봇이 위치한 음성 채팅방이 비었는지, 비지 않았는지 확인
            if 0 < len([None for memeber in manager.voice_channel.members if not memeber.bot]):
                await send_error_embed(interaction, "ChannelMismatchError",
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
            manager = self.playlist_manager.get_playlist_manager(interaction.guild)

        try: manager.add_audio(YoutubeAudioFile(audio_file_path, yt=yt))
        except ValueError:
            await send_error_embed(interaction, "DuplicationError!!!", """이미 플레이 리스트에 해당 영상이 있습니다!""",
                                   followup=True)
            return



        embed = Embed(title=f'검색된 영상 \n```{yt.title}``` \n영상을 플레이 리스트에 추가했습니다!', description=f'길이: {yt.length//60}분 {yt.length%60}초')
        embed.set_image(yt.thumbnail_url)
        embed.color = Color.SKY

        await interaction.followup.send(embed=embed)

        # /재생 기능을 처음 사용한 경우
        if manager.is_playing is False:
            manager.play_mode = PlayMode.ONCE
            manager.play(event_loop=asyncio.get_event_loop(), stop_callback=stop_callback)



    @nextcord.slash_command(name="삭제", description="플레이 리스트의 특정 음악을 지웁니다")
    async def delete_song(self, interaction: nextcord.Interaction,
                          index: int = SlashOption(name="번호",
                                                  description="음악의 번호를 적어 주세요 음악의 번호는 `/재생목록` 으로 확인 가능합니다")):
        
        try: self.playlist_manager.availability_check(interaction)
        except: 
            await send_error_embed(interaction, "RuntimeError!!!", "재생 기능을 사용 중이지 않거나\n 봇과 같은 음성 채팅방에 있지 않습니다")
            return

        manager = self.playlist_manager.get_playlist_manager(interaction.guild)

        try: audio_file: YoutubeAudioFile = manager.rm_audio(index - 1)
        except IndexError: 
            await send_error_embed(interaction, "IndexError!!!", "음악의 번호가 알맞지 않습니다! 음악의 번호는 `/재생목록` 으로 확인 가능합니다")
            return
        
        except PermissionError:
            await send_error_embed(interaction, "DeleteError!!!", "현재 재생중인 음악을 지울수 없습니다! 음악의 번호는 `/재생목록` 으로 확인 가능합니다")
            return
        
        await interaction.send(f'`{audio_file.yt.title}` 곡을 플레이 리스트에서 제거했습니다')



    @nextcord.slash_command(name="재생방식", description="음악을 재생하는 방식을 정합니다")
    async def playMode(self, interaction: nextcord.Interaction,
                       play_mode: str = SlashOption(name="재생방식", choices=["무한반복", "한번씩", "무작위"])):
        
        try: self.playlist_manager.availability_check(interaction)
        except: 
            await send_error_embed(interaction, "RuntimeError!!!", "재생 기능을 사용 중이지 않거나\n 봇과 같은 음성 채팅방에 있지 않습니다")
            return

        manager = self.playlist_manager.get_playlist_manager(interaction.guild)


        match(play_mode):
            case "한번씩":
                manager.set_play_mode(PlayMode.ONCE)
                await interaction.send(f'이제부터 음악을 한번씩 차례로 재생합니다!')
                return
            case "무한반복":
                manager.set_play_mode(PlayMode.LOOP)
                await interaction.send(f'이제부터 음악을 차례대로 계속 재생합니다!')
                return
            case "무작위":
                manager.set_play_mode(PlayMode.SHUFFLE)
                await interaction.send(f'이제부터 음악을 무작위로 계속 재생합니다!')
                return



    @nextcord.slash_command(name="스킵", description="음악 하나를 스킵합니다")
    async def skip(self, interaction: nextcord.Interaction): 
        try: self.playlist_manager.availability_check(interaction)
        except: 
            await send_error_embed(interaction, "RuntimeError!!!", "재생 기능을 사용 중이지 않거나\n 봇과 같은 음성 채팅방에 있지 않습니다")
            return

        manager = self.playlist_manager.get_playlist_manager(interaction.guild)

        manager.skip()

        await interaction.send("음악을 스킵했습니다!")



    @nextcord.slash_command(name="재생목록", description="현재 재생중인 재생 목록을 확인합니다")
    async def playlist(self, interaction: nextcord.Interaction):
        try: self.playlist_manager.availability_check(interaction)
        except: 
            await send_error_embed(interaction, "RuntimeError!!!", "재생 기능을 사용 중이지 않거나\n 봇과 같은 음성 채팅방에 있지 않습니다")
            return

        manager = self.playlist_manager.get_playlist_manager(interaction.guild)

        embed = Embed(
            title="현재 재생 목록",
            description=f"현재 {manager.audio_index + 1}번째 음악이 재생중입니다",
            color=Color.SKY
        )
        embed.set_footer(text=f"현재 {len(manager.audio_files)}개의 음악이 재생목록에 있습니다")


        for i, audio_file in enumerate(manager.audio_files):
            field_name = f'`{i+1}` : {audio_file.yt.title}'
            if i == manager.audio_index: field_name += "\n> 🔊 현재 재생중!"

            embed.add_field(
                name=field_name,
                value=f"> 길이: *{audio_file.yt.length//60}분 {audio_file.yt.length%60}초*"
                      f"\n\u180e\u2800\u3164",
                inline=False
            )

        await interaction.send(embed=embed)



    @nextcord.slash_command(name="정지", description="음악 재생을 중지합니다")
    async def stop(self, interaction: nextcord.Interaction):
        try: self.playlist_manager.availability_check(interaction)
        except: 
            await send_error_embed(interaction, "RuntimeError!!!", "재생 기능을 사용 중이지 않거나\n 봇과 같은 음성 채팅방에 있지 않습니다")
            return

        manager = self.playlist_manager.get_playlist_manager(interaction.guild)
        
        manager.stop()

        await interaction.send("음악 재생을 정지했습니다!")





def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))