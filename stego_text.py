#!/usr/bin/env python3

"""
stego_text.py - Fixed version
Text steganography using zero-width Unicode characters as an invisible bit channel.
"""
                                                        from __future__ import annotations
import argparse, sys, os, math, zlib, base64

# FIXED: Use actual Unicode characters, not escape strings
ZW_ZERO = '\u200B'  # zero width space -> '0'
ZW_ONE  = '\u200C'  # zero width non-joiner -> '1'
HEADER_BITS = 40  # 32 bits length + 8 bits flags

FLAG_COMPRESSED = 0x01

def bytes_to_bits(b: bytes) -> str:
    return ''.join(f'{byte:08b}' for byte in b)

def bits_to_bytes(bits: str) -> bytes:
    if len(bits) % 8 != 0:
        raise ValueError('bits length must be multiple of 8')
    out = bytearray()
    for i in range(0, len(bits), 8):
        out.append(int(bits[i:i+8], 2))
    return bytes(out)

def build_header(payload_len: int, flags: int) -> str:
    if payload_len >= 2**32:
        raise ValueError('payload too large (>= 4GiB unsupported)')
    length_bits = f'{payload_len:032b}'
    flags_bits = f'{flags:08b}'
    return length_bits + flags_bits

def parse_header(bits: str) -> tuple[int, int]:
    if len(bits) < HEADER_BITS:
        raise ValueError('not enough header bits')
    length_bits = bits[:32]
    flags_bits = bits[32:40]
    length = int(length_bits, 2)
    flags = int(flags_bits, 2)
    return length, flags

def encode_dense(host_text: str, payload_bytes: bytes, flags: int = 0, bold_words: bool = True) -> str:
    # Build complete bit stream including header
    header = build_header(len(payload_bytes), flags)
    bits_payload = bytes_to_bits(payload_bytes)
    all_bits = header + bits_payload

    # Find all non-space carrier positions
    carriers = [i for i, ch in enumerate(host_text) if not ch.isspace()]
    if len(carriers) == 0:
        raise ValueError('host text has no carriers (all whitespace)')

    # Calculate how many bits to embed per carrier
    bits_per_carrier = math.ceil(len(all_bits) / len(carriers))

    # Build the encoded text
    out_chars = []
    bit_index = 0

    for i, ch in enumerate(host_text):
        out_chars.append(ch)
        if not ch.isspace() and bit_index < len(all_bits):
            # Add zero-width characters for this carrier
            slice_bits = all_bits[bit_index: bit_index + bits_per_carrier]
            for b in slice_bits:
                out_chars.append(ZW_ONE if b == '1' else ZW_ZERO)
            bit_index += len(slice_bits)

    encoded = ''.join(out_chars)

    # Optional visible bold channel
    if bold_words:
        words = encoded.split(' ')
        out_words = []
        wb_index = 0

        for w in words:
            if wb_index < len(bits_payload) and any(not ch.isspace() for ch in w):
                if bits_payload[wb_index] == '1':
                    # Find first non-space character to bold
                    for j, ch in enumerate(w):
                        if not ch.isspace():
                            # Insert bold markers around the character
                            w = w[:j] + '**' + ch + '**' + w[j+1:]
                            break
                wb_index += 1
            out_words.append(w)

        encoded = ' '.join(out_words)

    return encoded

def decode_dense(encoded_text: str) -> bytes:
    # First, remove any bold markers that might interfere
    clean_text = encoded_text.replace('**', '')

    # Extract zero-width bits
    bits = []
    i = 0

    while i < len(clean_text):
        ch = clean_text[i]
        if ch.isspace():
            i += 1
            continue

        # Skip the regular character
        i += 1

        # Collect all zero-width characters that follow
        while i < len(clean_text) and clean_text[i] in (ZW_ZERO, ZW_ONE):
            bits.append('1' if clean_text[i] == ZW_ONE else '0')
            i += 1

    if len(bits) < HEADER_BITS:
        raise ValueError('no header found (not enough hidden bits)')

    # Parse header
    header_bits = ''.join(bits[:HEADER_BITS])
    payload_len, flags = parse_header(header_bits)

    # Extract payload
    payload_bits_needed = payload_len * 8
    if len(bits) < HEADER_BITS + payload_bits_needed:
        raise ValueError(f'not enough bits for payload: expected {payload_bits_needed}, got {len(bits) - HEADER_BITS}')

    payload_bits = ''.join(bits[HEADER_BITS:HEADER_BITS + payload_bits_needed])
    payload = bits_to_bytes(payload_bits)

    # Handle compression
    if flags & FLAG_COMPRESSED:
        try:
            payload = zlib.decompress(payload)
        except zlib.error:
            raise ValueError('failed to decompress payload (corrupted or not compressed)')

    return payload

def cli_encode(args):
    # Read payload
    if args.infile and os.path.isfile(args.infile):
        with open(args.infile, 'rb') as f:
            payload = f.read()
    elif args.text:
        payload = args.text.encode('utf-8')
    else:
        raise ValueError('No payload provided. Use --infile or --text.')

    # Read host text
    if args.host_file:
        with open(args.host_file, 'r', encoding='utf-8') as f:
            host_text = f.read()
    elif args.host_text:
        host_text = args.host_text
    else:
        raise ValueError('No host text provided. Use --host-file or --host-text.')

    # Handle compression
    flags = 0
    if args.compress:
        payload = zlib.compress(payload)
        flags |= FLAG_COMPRESSED

    # Encode
    encoded = encode_dense(host_text, payload, flags, bold_words=args.bold)

    # Write output
    if args.outfile:
        with open(args.outfile, 'w', encoding='utf-8') as f:
            f.write(encoded)
        print(f'Wrote stego text to {args.outfile}')
    else:
        print(encoded)

def cli_decode(args):
    # Read encoded text
    if args.infile and os.path.isfile(args.infile):
        with open(args.infile, 'r', encoding='utf-8') as f:
            encoded = f.read()
    elif args.text:
        encoded = args.text
    else:
        raise ValueError('No encoded text provided. Use --infile or --text.')

    # Decode
    try:
        payload = decode_dense(encoded)
    except Exception as e:
        print(f'Decoding failed: {e}', file=sys.stderr)
        sys.exit(1)

    # Write output
    if args.outfile:
        with open(args.outfile, 'wb') as f:
            f.write(payload)
        print(f'Wrote payload to {args.outfile}')
    else:
        # Try to display as text, fall back to base64
        try:
            text = payload.decode('utf-8')
            print(text)
        except UnicodeDecodeError:
            print('Binary payload (base64):')
            print(base64.b64encode(payload).decode('ascii'))

def main():
    p = argparse.ArgumentParser(description='Text steganography using zero-width Unicode characters.')
    sub = p.add_subparsers(dest='cmd', required=True)

    # Encode command
    pe = sub.add_parser('encode', help='Embed payload into host text')
    pe.add_argument('--host-file', help='Host text file (UTF-8)')
    pe.add_argument('--host-text', help='Host text on command line')
    pe.add_argument('--infile', help='Payload file to embed (binary)')
    pe.add_argument('--text', help='Payload text to embed')
    pe.add_argument('--outfile', help='Output file for stego text')
    pe.add_argument('--bold', action='store_true', help='Add visible bold markers')
    pe.add_argument('--compress', action='store_true', help='Compress payload')

    # Decode command
    pd = sub.add_parser('decode', help='Extract payload from stego text')
    pd.add_argument('--infile', help='Stego text file (UTF-8)')
    pd.add_argument('--text', help='Stego text on command line')
    pd.add_argument('--outfile', help='Output file for recovered payload')

    args = p.parse_args()

    if args.cmd == 'encode':
        cli_encode(args)
    elif args.cmd == 'decode':
        cli_decode(args)

if __name__ == '__main__':
    main()
