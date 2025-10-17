preload_modules = [
    'pie_py.censorship.core.censorship.models'
]

extensions = [
    "pie_py.music.music_extension",
    'pie_py.censorship.censorship_extension'
]


__all__ = [
    'preload_modules',
    "extensions"
]