import pymem
from NativeMethods import *


def RemapMemoryRegion(process_handle, base_address, region_size, map_protection):
    # 分配新内存空间以重新映射
    addr = VirtualAlloc(None, region_size, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE,
                        MemoryProtectionConstraints.PAGE_EXECUTE_READWRITE)
    if addr == 0:
        return False

    # 分配缓冲区用于存储原内存区域的数据
    copy_buf = VirtualAlloc(None, region_size, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE,
                            MemoryProtectionConstraints.PAGE_EXECUTE_READWRITE)
    if copy_buf == 0:
        return False

    # 读取原内存区域的数据到缓冲区
    bytes_read = ctypes.c_size_t(0)
    if not ReadProcessMemory(process_handle, base_address, copy_buf, region_size, ctypes.byref(bytes_read)):
        return False

    section_handle = ctypes.c_void_p()

    # 创建一个新的内存段
    status = NtCreateSection(ctypes.byref(section_handle), AccessMask.SECTION_ALL_ACCESS, None,
                             ctypes.byref(region_size), MemoryProtectionConstraints.PAGE_EXECUTE_READWRITE,
                             SectionProtectionConstraints.SEC_COMMIT, None)
    if status.value != Ntstatus.STATUS_SUCCESS:
        return False

    # 解除原内存区域的映射
    status = NtUnmapViewOfSection(process_handle, base_address)
    if status.value != Ntstatus.STATUS_SUCCESS:
        return False

    # 将新的内存段映射到进程空间
    view_base = ctypes.c_void_p(base_address)
    section_offset = ctypes.c_long()
    view_size = ctypes.c_uint()
    status = NtMapViewOfSection(section_handle, process_handle, ctypes.byref(view_base), 0, region_size,
                                ctypes.byref(section_offset), ctypes.byref(view_size), 2, 0,
                                MemoryProtectionConstraints.PAGE_EXECUTE_READWRITE)
    if status.value != Ntstatus.STATUS_SUCCESS:
        return False

    # 将缓冲区的数据写入新的内存段
    bytes_written = ctypes.c_size_t(0)
    if not WriteProcessMemory(process_handle, view_base, copy_buf, view_size.value, ctypes.byref(bytes_written)):
        return False

    # 释放缓冲区的内存
    if not VirtualFree(copy_buf, 0, MemFree.MEM_RELEASE):
        return False

    return True


if __name__ == '__main__':
    pm = pymem.Pymem("WowClassic.exe")
    # 获取内存基本信息
    basic_information = MEMORY_BASIC_INFORMATION()
    if VirtualQueryEx(pm.process_handle, pm.base_address, ctypes.byref(basic_information),
                      ctypes.sizeof(basic_information)) == 0:
        print("VirtualQueryEx 失败。 返回0字节。")
        exit()
    region_base = basic_information.baseAddress
    region_size = basic_information.regionSize

    # 挂起进程
    NtSuspendProcess(pm.process_handle)

    # 重新映射内存区域
    success = RemapMemoryRegion(pm.process_handle, region_base, ctypes.c_int(region_size),
                                MemoryProtectionConstraints.PAGE_EXECUTE_READWRITE)
    if success:
        print("内存区域重新映射成功。")
    else:
        print("内存区域重新映射失败。")

    # 恢复进程
    NtResumeProcess(pm.process_handle)

    # 关闭句柄
    CloseHandle(pm.process_handle)
