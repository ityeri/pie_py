import os
import uuid
from pathlib import Path

import yspy
from ydpy import Video

from piepy.player_manager import LocalFileMusicElement, MusicElement

_MAX_AUDIO_BPS: int = 50_000


class YouTubeMusicElementProvider:  # 지금 무료체험 하세요
    def __init__(self, download_dir: str):
        self.download_dir: str = download_dir

    def init(self):
        os.makedirs(self.download_dir, exist_ok=True)

        # remove leftover files from crashed previous sessions
        for leftover in Path(self.download_dir).glob('*.bin*'):
            leftover.unlink()

    async def create_music_from_video(self, video: yspy.Video) -> MusicElement:
        downloading_video = Video(video.url)
        video_data = await downloading_video.afetch()

        audio_formats = [format for format in video_data.formats if format.is_audio and not format.is_video]
        sorted_formats = sorted(audio_formats, key=lambda f: f.bitrate)
        filtered_formats = [format for format in sorted_formats if format.bitrate <= _MAX_AUDIO_BPS]

        if filtered_formats:
            picked_format = filtered_formats[-1]
        else:
            picked_format = sorted_formats[0]

        filename = f'{uuid.uuid4()}.bin'
        file_path = str(Path(self.download_dir).joinpath(filename))

        await picked_format.adownload(file_path)

        return LocalFileMusicElement(
            f'yt_video_{video.id}',
            title=video.title,
            url=video.url,
            title_image_url=video.get_highest_res_thumbnail().url,
            length=video.length_seconds,
            file_path=file_path,
            auto_file_delete=True
        )
