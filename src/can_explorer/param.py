from __future__ import annotations

import uuid
from typing import Optional

import dearpygui.dearpygui as dpg


class Param:
    def __init__(self, value: Optional[int] = None):
        self._value = value
        self._tag = hash(uuid.uuid4())

    @property
    def value(self) -> Optional[int]:
        return self._value

    def _update(self) -> None:
        self._value = dpg.get_value(self._tag)

    def as_dict(self) -> dict:
        return dict(tag=self._tag, callback=self._update)


class OptionParam(Param):
    _options: Optional[tuple] = None

    @property
    def options(self) -> Optional[tuple]:
        return self._options

    @options.setter
    def options(self, options: list[str]) -> None:
        dpg.configure_item(self._tag, items=options)
        self._options = options


class RangeParam(Param):
    def __init__(self, minimum: int, maximum: int, value: Optional[int] = None):
        super().__init__(value)
        self._min = minimum
        self._max = maximum

    def __iter__(self):
        yield self._min
        yield self._max


baudrate = OptionParam()
channel = OptionParam()
interface = OptionParam()
buffer_size = RangeParam(minimum=50, maximum=2500, value=100)
plot_height = RangeParam(minimum=50, maximum=500, value=100)
