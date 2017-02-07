# -*- coding: utf-8 -*-
import mss
import struct

from zlib import compress, crc32

def _to_png(data, width, height):
    # From MSS

    line = width * 3
    png_filter = struct.pack('>B', 0)
    scanlines = b''.join(
        [png_filter + data[y * line:y * line + line]
         for y in range(height)])

    magic = struct.pack('>8B', 137, 80, 78, 71, 13, 10, 26, 10)

    # Header: size, marker, data, CRC32
    ihdr = [b'', b'IHDR', b'', b'']
    ihdr[2] = struct.pack('>2I5B', width, height, 8, 2, 0, 0, 0)
    ihdr[3] = struct.pack('>I', crc32(b''.join(ihdr[1:3])) & 0xffffffff)
    ihdr[0] = struct.pack('>I', len(ihdr[2]))

    # Data: size, marker, data, CRC32
    idat = [b'', b'IDAT', compress(scanlines), b'']
    idat[3] = struct.pack('>I', crc32(b''.join(idat[1:3])) & 0xffffffff)
    idat[0] = struct.pack('>I', len(idat[2]))

    # Footer: size, marker, None, CRC32
    iend = [b'', b'IEND', b'', b'']
    iend[3] = struct.pack('>I', crc32(iend[1]) & 0xffffffff)
    iend[0] = struct.pack('>I', len(iend[2]))

    return b''.join([
        magic,
        b''.join(ihdr),
        b''.join(idat),
        b''.join(iend)
    ])

def screens():
    screenshoter = mss.mss()
    monitors = screenshoter.enum_display_monitors()
    return monitors[1:] if len(monitors) > 1 else monitors

def screenshot(idx=None):
    screenshoter = mss.mss()
    screenshots = []

    try:
        idx = int(idx)
    except:
        idx = None

    monitors = screenshoter.enum_display_monitors()
    if len(monitors) == 0:
        return None

    screen = 0

    if not (idx is None or idx+1 > len(monitors)):
        screen = idx+1

    try:
        monitor = monitors[screen]
        return _to_png(
            screenshoter.get_pixels(monitor),
            monitor['width'], monitor['height']), None
    except Exception as e:
        return None, '{}'.format(e)
