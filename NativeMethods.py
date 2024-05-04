import ctypes
class Ntstatus(ctypes.c_uint):
    STATUS_ACCESS_VIOLATION = 3221225477
    STATUS_SUCCESS = 0
    STATUS_FILE_LOCK_CONFLICT = 0xC0000054
    STATUS_INVALID_FILE_FOR_SECTION = 0xC0000020
    STATUS_INVALID_PAGE_PROTECTION = 0xC0000045
    STATUS_MAPPED_FILE_SIZE_ZERO = 0xC000011E
    STATUS_SECTION_TOO_BIG = 0xC0000040


class AccessMask(ctypes.c_uint):
    STANDARD_RIGHTS_REQUIRED = 0x000F0000
    SECTION_QUERY = 0x0001
    SECTION_MAP_WRITE = 0x0002
    SECTION_MAP_READ = 0x0004
    SECTION_MAP_EXECUTE = 0x0008
    SECTION_EXTEND_SIZE = 0x0010
    SECTION_MAP_EXECUTE_EXPLICIT = 0x0020
    SECTION_ALL_ACCESS = (
                STANDARD_RIGHTS_REQUIRED | SECTION_QUERY | SECTION_MAP_WRITE | SECTION_MAP_READ | SECTION_MAP_EXECUTE | SECTION_EXTEND_SIZE)


class ProcessAccessFlags(ctypes.c_uint):
    PROCESS_ALL_ACCESS = 0xFFFF


class MemoryProtectionConstraints(ctypes.c_uint):
    PAGE_EXECUTE = 0x10
    PAGE_EXECUTE_READ = 0x20
    PAGE_EXECUTE_READWRITE = 0x40
    PAGE_EXECUTE_WRITECOPY = 0x80
    PAGE_NOACCESS = 0x01
    PAGE_READONLY = 0x02
    PAGE_READWRITE = 0x04
    PAGE_WRITECOPY = 0x08
    PAGE_TARGETS_INVALID = 0x40000000
    PAGE_TARGETS_NO_UPDATE = 0x40000000
    PAGE_GUARD = 0x100
    PAGE_NOCACHE = 0x200
    PAGE_WRITECOMBINE = 0x400


class MemoryAllocationType(ctypes.c_uint):
    MEM_COMMIT = 0x00001000
    MEM_RESERVE = 0x00002000


class SectionProtectionConstraints(ctypes.c_uint):
    SEC_COMMIT = 0x08000000


class State(ctypes.c_uint):
    MEM_COMMIT = 0x1000
    MEM_FREE = 0x10000
    MEM_RESERVE = 0x2000


class Type(ctypes.c_uint):
    MEM_IMAGE = 0x1000000
    MEM_MAPPED = 0x40000
    MEM_PRIVATE = 0x20000


class MemFree(ctypes.c_uint):
    MEM_RELEASE = 0x00008000


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("baseAddress", ctypes.c_void_p),
        ("allocationBase", ctypes.c_void_p),
        ("allocationProtect", MemoryProtectionConstraints),
        ("regionSize", ctypes.c_size_t),
        ("state", State),
        ("protect", MemoryProtectionConstraints),
        ("type", Type)
    ]


kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
ntdll = ctypes.WinDLL('ntdll', use_last_error=True)

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [ctypes.c_void_p]
CloseHandle.restype = ctypes.c_bool

NtCreateSection = ntdll.NtCreateSection
NtCreateSection.argtypes = [ctypes.POINTER(ctypes.c_void_p), AccessMask, ctypes.c_void_p, ctypes.POINTER(ctypes.c_long),
                            MemoryProtectionConstraints, SectionProtectionConstraints, ctypes.c_void_p]
NtCreateSection.restype = Ntstatus

NtResumeProcess = ntdll.NtResumeProcess
NtResumeProcess.argtypes = [ctypes.c_void_p]
NtResumeProcess.restype = None

NtSuspendProcess = ntdll.NtSuspendProcess
NtSuspendProcess.argtypes = [ctypes.c_void_p]
NtSuspendProcess.restype = None

NtUnmapViewOfSection = ntdll.NtUnmapViewOfSection
NtUnmapViewOfSection.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
NtUnmapViewOfSection.restype = Ntstatus

NtMapViewOfSection = ntdll.NtMapViewOfSection
NtMapViewOfSection.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.c_ulong,
                               ctypes.c_int, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_uint),
                               ctypes.c_uint, MemoryAllocationType, MemoryProtectionConstraints]
NtMapViewOfSection.restype = Ntstatus

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [ProcessAccessFlags, ctypes.c_bool, ctypes.c_uint]
OpenProcess.restype = ctypes.c_void_p

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = ctypes.c_bool

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_size_t)]
WriteProcessMemory.restype = ctypes.c_bool

VirtualAlloc = kernel32.VirtualAlloc
VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_int, MemoryAllocationType, MemoryProtectionConstraints]
VirtualAlloc.restype = ctypes.c_void_p

VirtualFree = kernel32.VirtualFree
VirtualFree.argtypes = [ctypes.c_void_p, ctypes.c_int, MemFree]
VirtualFree.restype = ctypes.c_bool

VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_int]
VirtualQueryEx.restype = ctypes.c_int