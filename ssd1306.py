"""
Small SSD1306 I2C driver for MicroPython.

Supports common 128x64 and 128x32 monochrome OLED displays.
"""

import framebuf
import time


SET_CONTRAST = 0x81
SET_ENTIRE_ON = 0xA4
SET_NORM_INV = 0xA6
SET_DISP = 0xAE
SET_MEM_ADDR = 0x20
SET_COL_ADDR = 0x21
SET_PAGE_ADDR = 0x22
SET_DISP_START_LINE = 0x40
SET_SEG_REMAP = 0xA0
SET_MUX_RATIO = 0xA8
SET_COM_OUT_DIR = 0xC0
SET_DISP_OFFSET = 0xD3
SET_COM_PIN_CFG = 0xDA
SET_DISP_CLK_DIV = 0xD5
SET_PRECHARGE = 0xD9
SET_VCOM_DESEL = 0xDB
SET_CHARGE_PUMP = 0x8D


class SSD1306:
    def __init__(self, width, height, external_vcc=False):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(
            self.buffer,
            self.width,
            self.height,
            framebuf.MONO_VLSB,
        )

        self.poweron()
        self.init_display()

    def init_display(self):
        commands = (
            SET_DISP | 0x00,
            SET_MEM_ADDR,
            0x00,
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > (2 * self.height) else 0x12,
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,
            SET_CONTRAST,
            0xFF,
            SET_ENTIRE_ON,
            SET_NORM_INV,
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        )

        for command in commands:
            self.write_command(command)

        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_command(SET_DISP | 0x00)

    def poweron(self):
        pass

    def contrast(self, value):
        self.write_command(SET_CONTRAST)
        self.write_command(value)

    def invert(self, invert):
        self.write_command(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1

        if self.width == 64:
            x0 += 32
            x1 += 32

        self.write_command(SET_COL_ADDR)
        self.write_command(x0)
        self.write_command(x1)
        self.write_command(SET_PAGE_ADDR)
        self.write_command(0)
        self.write_command(self.pages - 1)
        self.write_data(self.buffer)

    def fill(self, colour):
        self.framebuf.fill(colour)

    def pixel(self, x, y, colour=None):
        if colour is None:
            return self.framebuf.pixel(x, y)
        self.framebuf.pixel(x, y, colour)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)

    def text(self, string, x, y, colour=1):
        self.framebuf.text(string, x, y, colour)

    def hline(self, x, y, width, colour):
        self.framebuf.hline(x, y, width, colour)

    def vline(self, x, y, height, colour):
        self.framebuf.vline(x, y, height, colour)

    def line(self, x1, y1, x2, y2, colour):
        self.framebuf.line(x1, y1, x2, y2, colour)

    def rect(self, x, y, width, height, colour):
        self.framebuf.rect(x, y, width, height, colour)

    def fill_rect(self, x, y, width, height, colour):
        self.framebuf.fill_rect(x, y, width, height, colour)

    def blit(self, source, x, y):
        self.framebuf.blit(source, x, y)


class SSD1306_I2C(SSD1306):
    def __init__(
        self,
        width,
        height,
        i2c,
        address=0x3C,
        external_vcc=False,
    ):
        self.i2c = i2c
        self.address = address
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]
        super().__init__(width, height, external_vcc)

    def write_command(self, command):
        self.temp[0] = 0x80
        self.temp[1] = command
        self.i2c.writeto(self.address, self.temp)

    def write_data(self, buffer):
        self.write_list[1] = buffer
        self.i2c.writevto(self.address, self.write_list)

    def poweron(self):
        time.sleep_ms(10)
