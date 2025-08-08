import os

from discord import PCMVolumeTransformer, FFmpegPCMAudio

class Music:
    def __init__(self, title: str, length: float, file_path: str):
        self.title: str = title
        self.length: float = length
        self.file_path: str = file_path

        self.source: PCMVolumeTransformer = PCMVolumeTransformer(FFmpegPCMAudio(self.file_path))

    def cleanup(self):
        self.source.cleanup()
        os.remove(self.file_path)

    def set_volume(self, volume: float):
        self.source.volume = volume