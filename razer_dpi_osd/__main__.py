import signal
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction

from .monitor import DPIMonitor
from .osd import DPIOsd


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    osd = DPIOsd()

    try:
        monitor = DPIMonitor()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    monitor.dpi_changed.connect(osd.show_dpi)

    icon = QSystemTrayIcon()
    icon.setIcon(QIcon.fromTheme("input-mouse", QIcon.fromTheme("preferences-desktop-peripherals")))
    icon.setToolTip(f"DPI OSD — {monitor.mouse_name}")

    menu = QMenu()
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    icon.setContextMenu(menu)
    icon.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
