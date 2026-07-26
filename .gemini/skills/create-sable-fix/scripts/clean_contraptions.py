#!/usr/bin/env python3
import os
import struct
import zlib
import shutil
import sys

def clean_file(filepath):
    if not os.path.exists(filepath):
        return False
    with open(filepath, "rb") as f:
        mca = bytearray(f.read())
    if len(mca) < 8192:
        return False

    fname = os.path.basename(filepath)
    parts = fname.split(".")
    try:
        rx, rz = int(parts[1]), int(parts[2])
    except Exception:
        return False

    modified = False
    for i in range(1024):
        off = struct.unpack(">I", b"\x00" + mca[i*4 : i*4+3])[0]
        sec = mca[i*4+3]
        if off == 0 or sec == 0:
            continue
        byte_off = off * 4096
        length = struct.unpack(">I", mca[byte_off : byte_off+4])[0]
        comp = mca[byte_off+4]
        chunk_data = mca[byte_off+5 : byte_off+4+length]
        try:
            chunk_nbt = zlib.decompress(chunk_data)
        except Exception:
            continue

        targets = [b"create:stationary_contraption", b"create:oriented_contraption"]
        chunk_mod = False
        for target in targets:
            while True:
                pos = chunk_nbt.find(target)
                if pos == -1:
                    break
                str_len_pos = pos - 2
                str_len = struct.unpack(">H", chunk_nbt[str_len_pos:pos])[0]
                if str_len == len(target):
                    new_id = b"minecraft:marker"
                    new_len_bytes = struct.pack(">H", len(new_id))
                    chunk_nbt = chunk_nbt[:str_len_pos] + new_len_bytes + new_id + chunk_nbt[pos + len(target):]
                    chunk_mod = True
                    # Find approximate coordinates if Pos tag is near
                    pos_tag = chunk_nbt.find(b"Pos", max(0, pos-300))
                    coords_str = ""
                    if pos_tag != -1 and pos_tag < pos + 300:
                        try:
                            d_bytes = chunk_nbt[pos_tag+8 : pos_tag+32]
                            if len(d_bytes) == 24:
                                x, y, z = struct.unpack(">ddd", d_bytes)
                                coords_str = f" at ({x:.1f}, {y:.1f}, {z:.1f})"
                        except Exception:
                            pass
                    print(f"[{fname}] Chunk {i}: Replaced {target.decode()}{coords_str}")
                else:
                    break

        if chunk_mod:
            new_compressed = zlib.compress(chunk_nbt)
            new_len = len(new_compressed)
            pad_len = (sec * 4096) - (new_len + 5)
            if pad_len >= 0:
                new_chunk_block = struct.pack(">I", new_len + 1) + bytes([comp]) + new_compressed + (b"\x00" * pad_len)
                mca[byte_off : byte_off + sec * 4096] = new_chunk_block
                modified = True
            else:
                print(f"[{fname}] Chunk {i} resized beyond sector bounds, skipping for now")

    if modified:
        shutil.copyfile(filepath, filepath + ".bak")
        with open(filepath, "wb") as f_out:
            f_out.write(mca)
        print(f"-> Cleaned and saved {filepath}")
        return True
    return False

def main():
    world_dir = "world"
    if len(sys.argv) > 1:
        world_dir = sys.argv[1]

    entities_dir = os.path.join(world_dir, "entities")
    sublevels_dir = os.path.join(world_dir, "sublevels")

    if not os.path.exists(entities_dir):
        print(f"Error: Entities directory {entities_dir} not found.")
        sys.exit(1)

    print("Scanning entity MCA files for broken Create/Sable contraptions...")
    cleaned_count = 0
    for root, dirs, files in os.walk(entities_dir):
        for f in files:
            if f.endswith(".mca"):
                if clean_file(os.path.join(root, f)):
                    cleaned_count += 1

    if os.path.exists(sublevels_dir):
        print("Clearing Sable sublevel cache files...")
        for root, dirs, files in os.walk(sublevels_dir):
            for f in files:
                if f.endswith(".slvlr") or f.endswith(".slvls"):
                    file_path = os.path.join(root, f)
                    try:
                        os.remove(file_path)
                        print(f"Removed cache file: {file_path}")
                    except Exception as e:
                        print(f"Failed to remove {file_path}: {e}")

    print(f"Done! Cleaned {cleaned_count} region entity files.")

if __name__ == "__main__":
    main()
