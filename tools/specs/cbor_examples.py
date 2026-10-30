"""Small independent CBOR codec for specification examples, not network input."""
import math
import struct


def encode(value):
    def head(major, n):
        if n < 24:
            return bytes([major << 5 | n])
        for small, width in [(24, 1), (25, 2), (26, 4), (27, 8)]:
            if n < 1 << (width * 8):
                return bytes([major << 5 | small]) + n.to_bytes(width, 'big')
        raise ValueError('integer outside CBOR range')
    if value is None:
        return b'\xf6'
    if isinstance(value, bool):
        return b'\xf5' if value else b'\xf4'
    if isinstance(value, int):
        return head(0, value) if value >= 0 else head(1, -1-value)
    if isinstance(value, float):
        if math.isnan(value):
            return bytes.fromhex('f97e00')
        for prefix, fmt in [(b'\xf9', '>e'), (b'\xfa', '>f'), (b'\xfb', '>d')]:
            try:
                raw = struct.pack(fmt, value)
                if struct.pack('>d', struct.unpack(fmt, raw)[0]) == struct.pack('>d', value):
                    return prefix + raw
            except OverflowError:
                pass
        raise ValueError('float encoding failed')
    if isinstance(value, bytes):
        return head(2, len(value)) + value
    if isinstance(value, str):
        raw = value.encode()
        return head(3, len(raw)) + raw
    if isinstance(value, list):
        return head(4, len(value)) + b''.join(map(encode, value))
    if isinstance(value, dict):
        pairs = sorted([(encode(k), encode(v)) for k, v in value.items()],
                       key=lambda pair: (len(pair[0]), pair[0]))
        return head(5, len(pairs)) + b''.join(k+v for k, v in pairs)
    raise TypeError(type(value))


def decode(data):
    pos = 0
    def item():
        nonlocal pos
        head = data[pos]
        pos += 1
        major, small = head >> 5, head & 31
        if small < 24:
            n = small
        else:
            width = {24: 1, 25: 2, 26: 4, 27: 8}[small]
            raw = data[pos:pos+width]
            pos += width
            if major == 7:
                return struct.unpack({2: '>e', 4: '>f', 8: '>d'}[width], raw)[0]
            n = int.from_bytes(raw, 'big')
        if major == 0:
            return n
        if major == 1:
            return -1-n
        if major in (2, 3):
            raw = data[pos:pos+n]
            pos += n
            return raw if major == 2 else raw.decode()
        if major == 4:
            return [item() for _ in range(n)]
        if major == 5:
            return {item(): item() for _ in range(n)}
        if major == 7:
            return {20: False, 21: True, 22: None}[n]
        raise ValueError((major, n))
    result = item()
    if pos != len(data):
        raise ValueError('trailing bytes')
    return result
