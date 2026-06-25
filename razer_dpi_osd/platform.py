import os

from PyQt6.QtWidgets import QWidget


def is_wayland() -> bool:
    return os.environ.get("XDG_SESSION_TYPE") == "wayland"


def set_click_through(widget: QWidget):
    if is_wayland():
        _set_click_through_wayland(widget)
    else:
        _set_click_through_x11(widget)


def _set_click_through_x11(widget: QWidget):
    try:
        from Xlib import X
        from Xlib.display import Display
        from Xlib.Xatom import Atom
        import Xlib.protocol.event

        wid = int(widget.winId())
        display = Display()
        window = display.create_resource_object("window", wid)

        window.shape_select_input(0)
        from Xlib.ext import shape
        shape.input_shape_rectangles(window, shape.SO.Set, 0, 0, [], shape.SK.Input)
        display.sync()
    except Exception:
        pass


def _set_click_through_wayland(widget: QWidget):
    try:
        widget.setWindowFlag(
            __import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.WindowType.WindowTransparentForInput,
            True,
        )
    except Exception:
        pass
