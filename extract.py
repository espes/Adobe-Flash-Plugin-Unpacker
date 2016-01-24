#!/usr/bin/env python3
# Copyright (c) 2016 espes
# Licensed under GPLv2 or later

import os
import lzma
import struct

def extract(data, path=b"."):
    while data:
        # header
        assert data[0] == 2
        compression = data[1] & 0x7F
        nested = data[1] >> 7

        buf_len = data[2]
        name_buf = data[3:3+buf_len]

        chunk_length = struct.unpack(">I", data[3+buf_len:3+buf_len+4])[0]

        header_len = buf_len+7


        n_path = path
        if name_buf:
            n_path += b"/" + name_buf
        print(repr(n_path))

        if compression == 1:
            decomp_len = struct.unpack(">I", data[header_len:header_len+4])[0]
            props = data[header_len+4:header_len+9]
            lzma_data = data[header_len+9:header_len+9+chunk_length]

            lzma_file = props+struct.pack("<Q", decomp_len)+lzma_data

            chunk_data = lzma.decompress(lzma_file, lzma.FORMAT_ALONE)
        else:
            chunk_data = data[header_len:header_len+chunk_length]

        if nested:
            try:
                os.makedirs(n_path)
            except FileExistsError:
                pass
            extract(chunk_data, n_path)
        else:
            with open(n_path, "wb") as out_file:
                out_file.write(chunk_data)

        data = data[header_len+chunk_length:]

if __name__ == "__main__":
    in_data = open("Flash Player.plugin.lzma", "rb").read()
    extract(in_data)
