from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path

import dearpygui.dearpygui as dpg
from dearpygui_ext.themes import create_theme_imgui_light

RESOURCES_DIR = Path(__file__).parent / "resources"


def frozen(value) -> property:
    return property(fget=lambda _: value)


class IterParam(int):
    @property
    @abstractmethod
    def _min(self):
        ...

    @property
    @abstractmethod
    def _max(self):
        ...

    def __iter__(self):
        yield self._min
        yield self._max


class BufferSize(IterParam):
    _min = frozen(50)
    _max = frozen(2_500)
    value = 100


class PlotSize(IterParam):
    _min = frozen(50)
    _max = frozen(500)
    value = 100


class Baudrate:
    value = None


class Interface:
    value = None


class Channel:
    value = None


@dataclass(frozen=True)
class Window:
    height = 600
    width = 600


class Font:
    height = frozen(14)
    path = frozen(RESOURCES_DIR / "Inter-Medium.ttf")

    def default(self) -> int:
        return dpg.add_font(self.path, self.height)

    def label(self) -> int:
        return dpg.add_font(self.path, self.height * 1.75)


class Theme:
    def default(self) -> int:
        return 0

    def light(self) -> int:
        return create_theme_imgui_light()
