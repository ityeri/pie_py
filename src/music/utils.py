from youtubesearchpython.__future__ import VideosSearch

import asyncio

from discord import Guild
from discord.abc import GuildChannel

from src.music.music import Music


def get_guild_display_info(guild: Guild) -> str:
    return f'Guild: "{guild.name}" id: {guild.id}'

def get_channel_display_info(channel: GuildChannel) -> str:
    return f'GuildChannel: "{channel.name}" id: {channel.id}'

async def get_urls_by_query(query: str, limit: int) -> list[str]:
    search = VideosSearch(query, limit=limit)
    result = await search.next()

    return [single_result["link"] for single_result in result["result"]]


def parse_time(
        time_sec: float,
        hour_suffix: str = "시간",
        min_suffix: str = "분",
        sec_suffix: str = "초",
        sep: str = " "
) -> str:
    hour = time_sec // 3600
    time_sec %= 3600

    mins = time_sec // 60
    time_sec %= 60

    sec = int(time_sec)

    out = str(sec) + sec_suffix

    if 0 < mins:
        out = str(mins) + min_suffix + sep + out

    if 0 < hour:
        out = str(hour) + hour_suffix + sep + out

    return out


def query_music_naturally(musics: list[Music], title_or_index: str) -> Music | None:
    try:
        index: int = int(title_or_index) - 1

        if 0 <= index:  # 맞다 파이썬 음수 인덱스도 있었지
            try:
                return musics[index]
            except IndexError:
                pass

    except ValueError:
        title: str = title_or_index

        for checking_music in musics:
            if title in checking_music.title:
                return checking_music

    return None