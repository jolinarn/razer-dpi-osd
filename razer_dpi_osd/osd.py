from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QRectF, QPointF,
)
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QFontDatabase, QLinearGradient,
    QPainter, QPainterPath, QPen, QRadialGradient,
)
from PyQt6.QtWidgets import QApplication, QWidget

WIDTH = 320
HEIGHT = 120
RADIUS = 20

BAR_H = 4
BAR_MARGIN = 32
BAR_Y = 88

DOT_RADIUS = 4
DOT_Y = 104

ACCENT = QColor(0, 230, 120)
ACCENT_DIM = QColor(0, 230, 120, 60)
BG = QColor(18, 18, 22, 230)
BORDER = QColor(255, 255, 255, 15)
TEXT_PRIMARY = QColor(255, 255, 255)
TEXT_SECONDARY = QColor(255, 255, 255, 100)
BAR_BG = QColor(255, 255, 255, 20)
DOT_INACTIVE = QColor(255, 255, 255, 40)


class DPIOsd(QWidget):
    def __init__(self):
        super().__init__()
        self._dpi = 0
        self._active_stage = 0
        self._total_stages = 0

        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(WIDTH, HEIGHT)

        self._fade_in = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_in.setDuration(120)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._fade_out = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_out.setDuration(500)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out.finished.connect(self.hide)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._start_fade_out)

    def show_dpi(self, dpi: int, active_stage: int, total_stages: int):
        self._dpi = dpi
        self._active_stage = active_stage
        self._total_stages = total_stages

        self._center_on_screen()

        self._hide_timer.stop()
        self._fade_out.stop()

        self.setWindowOpacity(0.0)
        self.show()

        from . import platform
        platform.set_click_through(self)

        self._fade_in.start()
        self._hide_timer.start(1500)
        self.update()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.geometry()
        x = geo.x() + (geo.width() - WIDTH) // 2
        y = geo.y() + int(geo.height() * 0.33)
        self.move(x, y)

    def _start_fade_out(self):
        self._fade_out.setStartValue(self.windowOpacity())
        self._fade_out.start()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # background with subtle gradient
        bg_path = QPainterPath()
        bg_path.addRoundedRect(QRectF(0, 0, WIDTH, HEIGHT), RADIUS, RADIUS)

        bg_grad = QLinearGradient(0, 0, 0, HEIGHT)
        bg_grad.setColorAt(0, QColor(28, 28, 34, 230))
        bg_grad.setColorAt(1, QColor(14, 14, 18, 240))
        p.fillPath(bg_path, QBrush(bg_grad))

        # subtle border
        p.setPen(QPen(BORDER, 1.0))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(QRectF(0.5, 0.5, WIDTH - 1, HEIGHT - 1), RADIUS, RADIUS)

        # accent glow at top
        glow = QRadialGradient(QPointF(WIDTH / 2, 0), WIDTH * 0.6)
        glow.setColorAt(0, QColor(0, 230, 120, 25))
        glow.setColorAt(1, QColor(0, 230, 120, 0))
        p.save()
        p.setClipPath(bg_path)
        p.fillRect(QRectF(0, 0, WIDTH, HEIGHT / 2), QBrush(glow))
        p.restore()

        # "SENSITIVITY" label
        p.setPen(QPen(TEXT_SECONDARY))
        label_font = QFont("Sans", 8)
        label_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.5)
        label_font.setWeight(QFont.Weight.Medium)
        p.setFont(label_font)
        p.drawText(BAR_MARGIN, 20, WIDTH - BAR_MARGIN * 2, 18,
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   "SENSITIVITY")

        # DPI number
        p.setPen(QPen(TEXT_PRIMARY))
        dpi_font = QFont("Sans", 32, QFont.Weight.Bold)
        dpi_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, -1)
        p.setFont(dpi_font)

        dpi_text = f"{self._dpi:,}"
        p.drawText(BAR_MARGIN, 34, WIDTH - BAR_MARGIN * 2, 48,
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   dpi_text)

        # "DPI" unit label next to number
        metrics = p.fontMetrics()
        num_width = metrics.horizontalAdvance(dpi_text)
        p.setPen(QPen(ACCENT))
        unit_font = QFont("Sans", 10, QFont.Weight.DemiBold)
        unit_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        p.setFont(unit_font)
        p.drawText(int(BAR_MARGIN + num_width + 8), 34, 60, 48,
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                   "DPI")

        # progress bar
        if self._total_stages > 0:
            bar_x = BAR_MARGIN
            bar_w = WIDTH - BAR_MARGIN * 2
            bar_rect = QRectF(bar_x, BAR_Y, bar_w, BAR_H)

            # bar background
            bar_bg_path = QPainterPath()
            bar_bg_path.addRoundedRect(bar_rect, BAR_H / 2, BAR_H / 2)
            p.fillPath(bar_bg_path, QBrush(BAR_BG))

            # filled portion
            fill_frac = (self._active_stage + 1) / self._total_stages
            fill_w = bar_w * fill_frac
            fill_rect = QRectF(bar_x, BAR_Y, fill_w, BAR_H)

            fill_grad = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            fill_grad.setColorAt(0, QColor(0, 200, 100))
            fill_grad.setColorAt(1, QColor(0, 255, 160))

            p.save()
            p.setClipPath(bar_bg_path)
            fill_path = QPainterPath()
            fill_path.addRoundedRect(fill_rect, BAR_H / 2, BAR_H / 2)
            p.fillPath(fill_path, QBrush(fill_grad))
            p.restore()

            # bar glow
            glow_rect = QRectF(bar_x, BAR_Y - 3, fill_w, BAR_H + 6)
            bar_glow = QLinearGradient(bar_x, 0, bar_x + fill_w, 0)
            bar_glow.setColorAt(0, QColor(0, 230, 120, 0))
            bar_glow.setColorAt(1, QColor(0, 230, 120, 40))
            p.fillRect(glow_rect, QBrush(bar_glow))

            # stage dots
            total_dot_w = (self._total_stages - 1) * ((bar_w) / (self._total_stages - 1)) if self._total_stages > 1 else 0
            for i in range(self._total_stages):
                if self._total_stages > 1:
                    cx = bar_x + (bar_w * i) / (self._total_stages - 1)
                else:
                    cx = bar_x + bar_w / 2

                if i == self._active_stage:
                    # active dot: larger, accent colored with glow
                    p.setPen(Qt.PenStyle.NoPen)
                    # glow ring
                    p.setBrush(QBrush(ACCENT_DIM))
                    p.drawEllipse(QPointF(cx, DOT_Y), DOT_RADIUS + 3, DOT_RADIUS + 3)
                    # solid dot
                    p.setBrush(QBrush(ACCENT))
                    p.drawEllipse(QPointF(cx, DOT_Y), DOT_RADIUS, DOT_RADIUS)
                elif i < self._active_stage:
                    p.setPen(Qt.PenStyle.NoPen)
                    p.setBrush(QBrush(QColor(0, 200, 100, 120)))
                    p.drawEllipse(QPointF(cx, DOT_Y), DOT_RADIUS - 1, DOT_RADIUS - 1)
                else:
                    p.setPen(Qt.PenStyle.NoPen)
                    p.setBrush(QBrush(DOT_INACTIVE))
                    p.drawEllipse(QPointF(cx, DOT_Y), DOT_RADIUS - 1, DOT_RADIUS - 1)

        p.end()
