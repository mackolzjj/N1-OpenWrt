#!/usr/bin/env python3
"""Compile a gettext .po file into a LuCI .lmo catalog.

OpenWrt ships its own ``po2lmo`` in ``staging_dir/host/bin``, but that tool only
exists after the build has started.  This pure-Python equivalent is used by the
workflow *before* ``make`` to compile the small supplementary catalogs in
``diy/po/``.  It writes the exact same on-disk format: SuperFastHash key,
big-endian sorted index, 4-byte aligned values.

Usage:  python3 po2lmo.py INPUT.po OUTPUT.lmo
"""

import struct
import sys

M = 0xFFFFFFFF


def u32(x):
    return x & M


def sfh_hash(data):
    """Paul Hsieh's SuperFastHash, byte-identical to LuCI's lmo implementation."""
    n = len(data)
    h = n
    rem = n & 3
    off = 0
    for _ in range(n >> 2):
        g16a = data[off] | (data[off + 1] << 8)
        g16b = data[off + 2] | (data[off + 3] << 8)
        h = u32(h + g16a)
        tmp = u32((g16b << 11) ^ h)
        h = u32((h << 16) ^ tmp)
        off += 4
        h = u32(h + (h >> 11))
    if rem == 3:
        h = u32(h + (data[off] | (data[off + 1] << 8)))
        h = u32(h ^ u32(h << 16))
        c = data[off + 2]
        h = u32(h ^ u32((c if c < 128 else c - 256) << 18))
        h = u32(h + (h >> 11))
    elif rem == 2:
        h = u32(h + (data[off] | (data[off + 1] << 8)))
        h = u32(h ^ u32(h << 11))
        h = u32(h + (h >> 17))
    elif rem == 1:
        c = data[off]
        h = u32(h + (c if c < 128 else c - 256))
        h = u32(h ^ u32(h << 10))
        h = u32(h + (h >> 1))
    h = u32(h ^ u32(h << 3))
    h = u32(h + (h >> 5))
    h = u32(h ^ u32(h << 4))
    h = u32(h + (h >> 17))
    h = u32(h ^ u32(h << 25))
    h = u32(h + (h >> 6))
    return h


_SIMPLE = {
    'n': b'\n', 't': b'\t', 'r': b'\r', 'a': b'\a', 'b': b'\b',
    'f': b'\f', 'v': b'\v', '"': b'"', '\\': b'\\',
}


def unescape(s):
    """Decode a gettext string literal body into UTF-8 bytes."""
    out = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt in _SIMPLE:
                out += _SIMPLE[nxt]
                i += 2
                continue
            if nxt in '01234567':
                j, oct_s = i + 1, ''
                while j < len(s) and len(oct_s) < 3 and s[j] in '01234567':
                    oct_s += s[j]
                    j += 1
                out.append(int(oct_s, 8) & 0xFF)
                i = j
                continue
            if nxt == 'x':
                j, hex_s = i + 2, ''
                while j < len(s) and s[j] in '0123456789abcdefABCDEF':
                    hex_s += s[j]
                    j += 1
                if hex_s:
                    out.append(int(hex_s, 16) & 0xFF)
                    i = j
                    continue
        out += c.encode('utf-8')
        i += 1
    return bytes(out)


def literal(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s


def parse_po(path):
    """Return [(msgid_bytes, msgstr_bytes), ...], skipping header/fuzzy/empty."""
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().splitlines()

    entries = []
    cur = None
    field = None

    def new_entry():
        return {'id': b'', 'str': b'', 'fuzzy': False}

    def flush():
        if cur and cur['id'] and cur['str'] and not cur['fuzzy']:
            entries.append((cur['id'], cur['str']))

    for raw in lines:
        line = raw.strip()
        if not line:
            flush()
            cur, field = None, None
            continue
        if line.startswith('#'):
            if 'fuzzy' in line:
                if cur is None:
                    cur = new_entry()
                cur['fuzzy'] = True
            continue
        if line.startswith('msgid_plural'):
            field = 'plural'
            continue
        if line.startswith('msgid '):
            if cur is None:
                cur = new_entry()
            cur['id'] = unescape(literal(line[6:]))
            field = 'id'
            continue
        if line.startswith('msgstr'):
            if cur is None:
                cur = new_entry()
            if line.startswith('msgstr[') and not line.startswith('msgstr[0]'):
                field = None  # only the first plural form is used by LuCI
                continue
            rest = line.split(' ', 1)[1] if ' ' in line else ''
            cur['str'] = unescape(literal(rest))
            field = 'str'
            continue
        if line.startswith('"'):
            if cur is None:
                cur = new_entry()
            chunk = unescape(literal(line))
            if field == 'id':
                cur['id'] += chunk
            elif field == 'str':
                cur['str'] += chunk
            continue
    flush()
    return entries


def make_lmo(pairs):
    payload = bytearray()
    index = []
    for key, val in pairs:
        offset = len(payload)
        payload += val
        payload += b'\0' * ((4 - len(val) % 4) % 4)
        index.append((sfh_hash(key), 1, offset, len(val)))
    index_off = len(payload)
    index.sort(key=lambda e: e[0])
    idx = b''.join(struct.pack('>IIII', *e) for e in index)
    return bytes(payload) + idx + struct.pack('>I', index_off)


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: po2lmo.py INPUT.po OUTPUT.lmo')
    pairs = parse_po(sys.argv[1])
    if not pairs:
        raise SystemExit('no translatable entries in ' + sys.argv[1])
    blob = make_lmo(pairs)
    with open(sys.argv[2], 'wb') as fh:
        fh.write(blob)
    print('%s: %d entries -> %s (%d bytes)' %
          (sys.argv[1], len(pairs), sys.argv[2], len(blob)))


if __name__ == '__main__':
    main()
