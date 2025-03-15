import os

from nextcord import FFmpegPCMAudio
from pytubefix import YouTube


# import pytube as pytube
# from pytube import YouTube





class AudioFile:
    def __init__(self, path: str):
        self.audio: FFmpegPCMAudio | None = None
        self.path: str = path

    def new(self):
        self.audio = None
        self.audio = FFmpegPCMAudio(source=self.path,
                                    executable="ffmpeg",
                                    # before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                    options='-ar 48000 -filter:a "volume=0.2" -vn -loglevel error')

        pass

    def delete(self):
        if self.audio is not None:
            self.audio.cleanup()
            try:
                self.audio.read()
            except:
                ...

            del self.audio
            self.audio = None

        os.remove(self.path)


class YoutubeAudioFile(AudioFile):
    def __init__(self, path, yt):
        super().__init__(path)
        self.yt: YouTube = yt
