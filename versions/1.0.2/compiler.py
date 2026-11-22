import os
import struct
import ctypes

def create_minimal_dll(filepath):
    dos_header = b'MZ' + b'\x00' * 58 + struct.pack('<I', 0x40)
    pe_sig = b'PE\x00\x00'
    coff = struct.pack('<HHIIIHH', 0x8664, 1, 0, 0, 0, 240, 0x2210)
    
    opt = b''.join([
        struct.pack('<H', 0x020B),      # Magic (PE32+)
        struct.pack('<B', 14),        # MajorLinkerVersion
        struct.pack('<B', 0),         # MinorLinkerVersion
        struct.pack('<I', 0x200),     # SizeOfCode
        struct.pack('<I', 0x200),     # SizeOfInitializedData
        struct.pack('<I', 0),         # SizeOfUninitializedData
        struct.pack('<I', 0x1000),    # AddressOfEntryPoint
        struct.pack('<I', 0x1000),    # BaseOfCode
        struct.pack('<Q', 0x10000000),# ImageBase
        struct.pack('<I', 0x1000),    # SectionAlignment
        struct.pack('<I', 0x200),     # FileAlignment
        struct.pack('<H', 6),         # MajorOperatingSystemVersion
        struct.pack('<H', 0),         # MinorOperatingSystemVersion
        struct.pack('<H', 0),         # MajorImageVersion
        struct.pack('<H', 0),         # MinorImageVersion
        struct.pack('<H', 6),         # MajorSubsystemVersion
        struct.pack('<H', 0),         # MinorSubsystemVersion
        struct.pack('<I', 0),         # Win32VersionValue
        struct.pack('<I', 0x3000),    # SizeOfImage
        struct.pack('<I', 0x200),     # SizeOfHeaders
        struct.pack('<I', 0),         # CheckSum
        struct.pack('<H', 2),         # Subsystem (Windows GUI)
        struct.pack('<H', 0x8140),    # DllCharacteristics
        struct.pack('<Q', 0x100000),  # SizeOfStackReserve
        struct.pack('<Q', 0x1000),    # SizeOfStackCommit
        struct.pack('<Q', 0x100000),  # SizeOfHeapReserve
        struct.pack('<Q', 0x1000),    # SizeOfHeapCommit
        struct.pack('<I', 0),         # LoaderFlags
        struct.pack('<I', 16),        # NumberOfRvaAndSizes
    ])
    
    data_dirs = b'\x00' * 16 + struct.pack('<II', 0x1000, 0x200) + b'\x00' * 104
    
    sec_rsrc = struct.pack(
        '<8sIIIIIIIII', b'.rsrc\x00\x00\x00',
        0x200, 0x1000, 0x200, 0x200, 0, 0, 0, 0, 0x40000040
    )
    
    headers = dos_header + pe_sig + coff + opt + data_dirs + sec_rsrc
    headers += b'\x00' * (0x200 - len(headers))
    
    root_res_dir = struct.pack('<IIHHHH', 0, 0, 0, 0, 0, 0)
    rsrc_data = root_res_dir + b'\x00' * (0x200 - len(root_res_dir))
    
    with open(filepath, 'wb') as f:
        f.write(headers + rsrc_data)

def compile_dll_native():
    assets_dir = "assets"
    output_dll = "project.dll"

    if not os.path.exists(assets_dir):
        print(f"Error: '{assets_dir}' directory not found.")
        return

    ico_files = sorted([f for f in os.listdir(assets_dir) if f.lower().endswith('.ico')])
    if not ico_files:
        print(f"Error: No .ico files found in '{assets_dir}' directory.")
        return

    print(f"Found {len(ico_files)} icon files. Processing...")

    if os.path.exists(output_dll):
        try:
            os.remove(output_dll)
        except Exception:
            pass

    create_minimal_dll(output_dll)

    kernel32 = ctypes.windll.kernel32

    kernel32.BeginUpdateResourceW.argtypes = [ctypes.c_wchar_p, ctypes.c_bool]
    kernel32.BeginUpdateResourceW.restype = ctypes.c_void_p

    kernel32.UpdateResourceW.argtypes = [
        ctypes.c_void_p,  # hUpdate
        ctypes.c_void_p,  # lpType
        ctypes.c_void_p,  # lpName
        ctypes.c_ushort,  # wLanguage
        ctypes.c_void_p,  # lpData
        ctypes.c_uint     # cbData
    ]
    kernel32.UpdateResourceW.restype = ctypes.c_bool

    kernel32.EndUpdateResourceW.argtypes = [ctypes.c_void_p, ctypes.c_bool]
    kernel32.EndUpdateResourceW.restype = ctypes.c_bool

    hUpdate = kernel32.BeginUpdateResourceW(output_dll, False)
    if not hUpdate:
        print(f"ERROR: Could not open DLL for resource updates! Windows Error Code: {kernel32.GetLastError()}")
        return

    RT_ICON = 3
    RT_GROUP_ICON = 14

    global_icon_id = 1
    success = True

    try:
        for group_index, filename in enumerate(ico_files, start=1):
            path = os.path.join(assets_dir, filename)
            with open(path, 'rb') as f:
                data = f.read()

            reserved, ico_type, image_count = struct.unpack('<HHH', data[:6])
            if ico_type != 1: 
                continue

            offset = 6
            group_entries = bytearray()

            for _ in range(image_count):
                header_data = data[offset:offset+16]
                if len(header_data) < 16: 
                    break
                    
                width, height, color_count, reserved_byte, planes, bit_count, img_size, img_offset = struct.unpack('<BBBBHHII', header_data)
                img_bytes = data[img_offset:img_offset+img_size]

                res1 = kernel32.UpdateResourceW(
                    hUpdate,
                    RT_ICON,
                    global_icon_id,
                    1033,
                    img_bytes,
                    len(img_bytes)
                )
                if not res1:
                    print(f"WARNING: Could not add icon layer. Code: {kernel32.GetLastError()}")

                group_entries.extend(struct.pack(
                    '<BBBBHHIH',
                    width, height, color_count, reserved_byte,
                    planes, bit_count, img_size, global_icon_id
                ))

                global_icon_id += 1
                offset += 16

            group_header = struct.pack('<HHH', 0, 1, image_count)
            group_resource_bytes = group_header + group_entries

            res2 = kernel32.UpdateResourceW(
                hUpdate,
                RT_GROUP_ICON,
                group_index,
                1033,
                group_resource_bytes,
                len(group_resource_bytes)
            )
            if not res2:
                print(f"WARNING: Could not add group icon. Code: {kernel32.GetLastError()}")

            print(f"  -> Processed: {filename} ({image_count} layers)")

    except Exception as e:
        print(f"Unexpected error during processing: {e}")
        success = False

    if success:
        result = kernel32.EndUpdateResourceW(hUpdate, False)
        if result:
            print(f"\nSUCCESS! DLL generated and icons embedded: {output_dll}")
        else:
            print(f"\nERROR: Could not save resources. Error Code: {kernel32.GetLastError()}")
    else:
        kernel32.EndUpdateResourceW(hUpdate, True)
        print("\nOperation aborted due to errors.")

if __name__ == "__main__":
    try:
        compile_dll_native()
    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
    input("\nPress ENTER to close...")
