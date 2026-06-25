import glob
import struct
from pathlib import Path

from PyQt6.QtCore import QTimer, QObject, pyqtSignal

SYSFS_PATTERN = "/sys/bus/hid/drivers/razermouse/*/dpi"


def _find_mouse() -> Path | None:
    for dpi_path in glob.glob(SYSFS_PATTERN):
        return Path(dpi_path).parent
    return None


def _read_dpi(device: Path) -> tuple[int, int]:
    text = (device / "dpi").read_text().strip()
    x, y = text.split(":")
    return int(x), int(y)


def _read_stages(device: Path) -> tuple[int, list[tuple[int, int]]]:
    data = (device / "dpi_stages").read_bytes()
    active = data[0]
    stages = []
    offset = 1
    while offset + 3 < len(data):
        x = struct.unpack(">H", data[offset:offset + 2])[0]
        y = struct.unpack(">H", data[offset + 2:offset + 4])[0]
        stages.append((x, y))
        offset += 4
    return active, stages


class DPIMonitor(QObject):
    dpi_changed = pyqtSignal(int, int, int)  # dpi_value, active_stage (0-based), total_stages

    def __init__(self, poll_ms: int = 200):
        super().__init__()
        self._device = _find_mouse()
        if not self._device:
            raise RuntimeError("No Razer mouse found in sysfs")

        self._last_dpi = _read_dpi(self._device)
        active, stages = _read_stages(self._device)
        self._last_stage = active
        self._total_stages = len(stages)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self._timer.start(poll_ms)

    @property
    def mouse_name(self) -> str:
        try:
            return (self._device / "device_type").read_text().strip()
        except OSError:
            return "Razer Mouse"

    def _poll(self):
        try:
            dpi = _read_dpi(self._device)
            active, stages = _read_stages(self._device)

            if dpi != self._last_dpi or active != self._last_stage:
                self._last_dpi = dpi
                self._last_stage = active
                self._total_stages = len(stages)
                self.dpi_changed.emit(dpi[0], active - 1, self._total_stages)
        except OSError:
            pass
