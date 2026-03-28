from __future__ import annotations

from sdl2.sdlmixer import (
    Mix_PlayChannel, Mix_HaltChannel, Mix_Volume, Mix_Playing,
    Mix_PlayMusic, Mix_HaltMusic, Mix_PauseMusic, Mix_ResumeMusic,
    Mix_VolumeMusic, Mix_PlayingMusic, Mix_PausedMusic, Mix_FadeInMusic,
    Mix_FadeOutMusic,
    MIX_MAX_VOLUME,
)


class Sound:
    """Short sound effect. Loaded via ResourceManager, played here.

    Example:
        sound = Sound("jump.wav")
        sound.play()
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._chunk = None
        self._channel = -1

    def _ensure_loaded(self) -> None:
        if self._chunk is None:
            from engine.core.app import current_app
            self._chunk = current_app().resources.load_sound(self._path)

    def play(self, volume: float = 1.0, loops: int = 0) -> None:
        """Play the sound effect.
        volume: 0.0 to 1.0
        loops: 0 = play once, -1 = loop forever
        """
        self._ensure_loaded()
        self._channel = Mix_PlayChannel(-1, self._chunk, loops)
        if self._channel >= 0:
            Mix_Volume(self._channel, int(volume * MIX_MAX_VOLUME))

    def stop(self) -> None:
        if self._channel >= 0:
            Mix_HaltChannel(self._channel)
            self._channel = -1

    @property
    def is_playing(self) -> bool:
        return self._channel >= 0 and Mix_Playing(self._channel)


class Music:
    """Streaming background music. Only one track plays at a time.

    Example:
        Music.play("bgm.mp3")
        Music.set_volume(0.5)
        Music.stop(fade_out_ms=2000)
    """

    @staticmethod
    def play(path: str, volume: float = 1.0, loops: int = -1,
             fade_in_ms: int = 0) -> None:
        """Play background music.
        loops: -1 = loop forever, 0 = play once
        """
        from engine.core.app import current_app
        mus = current_app().resources.load_music(path)
        if fade_in_ms > 0:
            Mix_FadeInMusic(mus, loops, fade_in_ms)
        else:
            Mix_PlayMusic(mus, loops)
        Mix_VolumeMusic(int(volume * MIX_MAX_VOLUME))

    @staticmethod
    def stop(fade_out_ms: int = 0) -> None:
        if fade_out_ms > 0:
            Mix_FadeOutMusic(fade_out_ms)
        else:
            Mix_HaltMusic()

    @staticmethod
    def pause() -> None:
        Mix_PauseMusic()

    @staticmethod
    def resume() -> None:
        Mix_ResumeMusic()

    @staticmethod
    def set_volume(volume: float) -> None:
        """Set volume: 0.0 to 1.0."""
        Mix_VolumeMusic(int(volume * MIX_MAX_VOLUME))

    @staticmethod
    def is_playing() -> bool:
        return bool(Mix_PlayingMusic()) and not bool(Mix_PausedMusic())

    @staticmethod
    def is_paused() -> bool:
        return bool(Mix_PausedMusic())
