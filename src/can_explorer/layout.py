from enum import Enum, auto, unique
from typing import Callable, Final, Union

import dearpygui.dearpygui as dpg
from dearpygui_ext.themes import create_theme_imgui_light

from can_explorer import param
from can_explorer.resources import DIR_PATH as RESOURCES_DIR
from can_explorer.resources import Percentage


class Font:
    HEIGHT: Final = 14
    PATH: Final = RESOURCES_DIR / "Inter-Medium.ttf"
    registered = False
    _default = None
    _label = None

    @classmethod
    def init(cls):
        # For some reason multiple calls to the font registry cause buggy behavior
        with dpg.font_registry():
            cls._default = dpg.add_font(cls.PATH, cls.HEIGHT)
            cls._label = dpg.add_font(cls.PATH, cls.HEIGHT * 1.75)

        cls.registered = True

    @classmethod
    def default(cls) -> int:
        if not cls.registered:
            cls.init()
        return cls._default  # type: ignore [return-value]

    @classmethod
    def label(cls) -> int:
        if not cls.registered:
            cls.init()
        return cls._label  # type: ignore [return-value]


class Theme:
    DEFAULT_BACKGROUND: Final = (50, 50, 50, 255)

    @staticmethod
    def default() -> int:
        return 0

    @classmethod
    def disabled(cls) -> int:
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvButton, enabled_state=False):
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonHovered, cls.DEFAULT_BACKGROUND
                )
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, cls.DEFAULT_BACKGROUND)
        return theme

    @staticmethod
    def light() -> int:
        return create_theme_imgui_light()


class Window:
    HEIGHT: Final = 600
    WIDTH: Final = 600


@unique
class Tag(str, Enum):
    HEADER = auto()
    BODY = auto()
    FOOTER = auto()
    MAIN_BUTTON = auto()
    CLEAR_BUTTON = auto()
    PLOT_LABEL = auto()
    PLOT_ITEM = auto()
    TAB_VIEWER = auto()
    TAB_SETTINGS = auto()
    SETTINGS_PLOT_BUFFER = auto()
    SETTINGS_PLOT_HEIGHT = auto()
    SETTINGS_APPLY = auto()


class PercentageWidthTableRow:
    # https://github.com/hoffstadt/DearPyGui/discussions/1306

    def __init__(self, **kwargs):
        self.table_id = dpg.add_table(
            header_row=False,
            policy=dpg.mvTable_SizingStretchProp,
            **kwargs,
        )
        self.stage_id = dpg.add_stage()
        dpg.push_container_stack(self.stage_id)

    def add_widget(self, uuid, percentage):
        dpg.add_table_column(
            init_width_or_weight=percentage / 100.0, parent=self.table_id
        )
        dpg.set_item_width(uuid, -1)

    def submit(self):
        dpg.pop_container_stack()
        with dpg.table_row(parent=self.table_id):
            dpg.unstage(self.stage_id)


class PlotTable(PercentageWidthTableRow):
    COLUMN_1_WIDTH: Final = 15
    COLUMN_2_WIDTH: Final = 85

    def __init__(self, **kwargs):
        super().__init__(parent=Tag.TAB_VIEWER, **kwargs)

    def add_label(self, uuid):
        return super().add_widget(uuid, self.COLUMN_1_WIDTH)

    def add_plot(self, uuid):
        return super().add_widget(uuid, self.COLUMN_2_WIDTH)


def _init_fonts():
    dpg.bind_font(Font.default())


def _init_themes():
    dpg.bind_theme(Theme.disabled())


def _header() -> None:
    def tab_callback(sender, app_data, user_data) -> None:
        current_tab = dpg.get_item_label(app_data)

        if current_tab == "Viewer":
            dpg.configure_item(Tag.TAB_VIEWER, show=True)
            dpg.configure_item(Tag.TAB_SETTINGS, show=False)
        else:
            dpg.configure_item(Tag.TAB_VIEWER, show=False)
            dpg.configure_item(Tag.TAB_SETTINGS, show=True)

    with dpg.tab_bar(tag=Tag.HEADER, callback=tab_callback):
        dpg.add_tab(label="Viewer")
        dpg.add_tab(label="Settings")


def _body() -> None:
    with dpg.child_window(tag=Tag.BODY, border=False):
        with dpg.group(tag=Tag.TAB_VIEWER, show=True):
            _viewer_tab()
        with dpg.group(tag=Tag.TAB_SETTINGS, show=False):
            _settings_tab()


def _footer() -> None:
    with dpg.child_window(tag=Tag.FOOTER, height=110, border=False, no_scrollbar=True):
        dpg.add_spacer(height=2)
        dpg.add_separator()
        dpg.add_spacer(height=2)

        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                with dpg.group(horizontal=True):
                    dpg.add_text("Message Buffer Size")
                    dpg.add_spacer()
                    dpg.add_slider_int(
                        tag=Tag.SETTINGS_PLOT_BUFFER,
                        width=-1,
                        default_value=Percentage.get(
                            param.buffer_size.value, max(param.buffer_size)
                        ),
                        min_value=2,
                        max_value=100,
                        clamped=True,
                        format="%d%%",
                    )

                with dpg.group(horizontal=True):
                    dpg.add_text("Plot Height")
                    dpg.add_spacer()
                    dpg.add_slider_int(
                        tag=Tag.SETTINGS_PLOT_HEIGHT,
                        width=-1,
                        default_value=Percentage.get(
                            param.plot_height.value, max(param.plot_height)
                        ),
                        min_value=10,
                        max_value=100,
                        clamped=True,
                        format="%d%%",
                    )
        dpg.add_spacer(height=2)

        dpg.add_separator()
        dpg.add_spacer()
        with dpg.group(horizontal=True):
            dpg.add_button(
                tag=Tag.MAIN_BUTTON,
                label="Start",
                width=-100,
                height=50,
                user_data=False,
            )
            dpg.add_button(
                tag=Tag.CLEAR_BUTTON,
                label="Clear",
                width=-1,
                height=50,
            )


def _viewer_tab() -> None:
    ...


def _settings_tab() -> None:
    with dpg.collapsing_header(label="CAN Bus", default_open=True):
        dpg.add_combo(
            label="Interface",
            **param.interface.as_dict(),
        )
        dpg.add_input_text(label="Channel", **param.channel.as_dict())
        dpg.add_combo(
            label="Baudrate",
            **param.baudrate.as_dict(),
        )
        dpg.add_spacer(height=5)
        dpg.add_button(tag=Tag.SETTINGS_APPLY, label="Apply", height=30)
        dpg.add_spacer(height=5)

    with dpg.collapsing_header(label="GUI"):
        with dpg.group(horizontal=True):
            dpg.add_text("Light Theme")
            dpg.add_checkbox(
                callback=lambda sender: dpg.bind_theme(
                    Theme.light() if dpg.get_value(sender) else Theme.default()
                )
            )

        dpg.add_button(
            label="Launch Font Manager", width=-1, callback=dpg.show_font_manager
        )
        dpg.add_button(
            label="Launch Style Editor", width=-1, callback=dpg.show_style_editor
        )
        dpg.add_spacer(height=5)


def create() -> None:
    _init_fonts()
    _init_themes()
    _header()
    _body()
    _footer()


def resize() -> None:
    dpg.set_item_height(
        Tag.BODY, (dpg.get_viewport_height() - dpg.get_item_height(Tag.FOOTER) - 50)
    )
    dpg.set_item_width(Tag.SETTINGS_APPLY, dpg.get_viewport_width() // 4)


def popup_error(name: Union[str, Exception], info: Union[str, Exception]) -> None:
    # https://github.com/hoffstadt/DearPyGui/discussions/1308

    # guarantee these commands happen in the same frame
    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()

        with dpg.window(label="ERROR", modal=True, no_close=True) as modal_id:
            dpg.add_text(name, color=(255, 0, 0))  # red
            dpg.add_separator()
            dpg.add_text(info)
            with dpg.group():
                dpg.add_button(
                    label="Close",
                    width=-1,
                    user_data=(modal_id, True),
                    callback=lambda _, __, user_data: dpg.delete_item(user_data[0]),
                )

    # guarantee these commands happen in another frame
    dpg.split_frame()
    width = dpg.get_item_width(modal_id)
    height = dpg.get_item_height(modal_id)
    dpg.set_item_pos(
        modal_id,
        [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2],
    )


def get_main_button_state() -> bool:
    return dpg.get_item_user_data(Tag.MAIN_BUTTON)


def get_settings_plot_buffer() -> int:
    percentage = dpg.get_value(Tag.SETTINGS_PLOT_BUFFER)
    return Percentage.reverse(percentage, max(param.buffer_size))


def get_settings_plot_height() -> int:
    percentage = dpg.get_value(Tag.SETTINGS_PLOT_HEIGHT)
    return Percentage.reverse(percentage, max(param.plot_height))


def set_main_button_callback(callback: Callable) -> None:
    button_labels = ("Stop", "Start")

    def wrapped_callback(sender, app_data, user_data):
        """
        Set the button label and toggle the state.
        """
        dpg.configure_item(
            Tag.MAIN_BUTTON, label=button_labels[user_data], user_data=not user_data
        )

        return callback(sender, app_data, user_data)

    dpg.configure_item(Tag.MAIN_BUTTON, callback=wrapped_callback)


def set_clear_button_callback(callback: Callable) -> None:
    dpg.configure_item(Tag.CLEAR_BUTTON, callback=callback)


def set_plot_buffer_slider_callback(callback: Callable) -> None:
    dpg.configure_item(Tag.SETTINGS_PLOT_BUFFER, callback=callback)


def set_plot_height_slider_callback(callback: Callable) -> None:
    dpg.configure_item(Tag.SETTINGS_PLOT_HEIGHT, callback=callback)


def set_settings_apply_button_callback(callback: Callable) -> None:
    dpg.configure_item(Tag.SETTINGS_APPLY, callback=callback)
