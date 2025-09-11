+++
title = "Hardware Fastmem 101"
date = 2025-09-11
description = "An ELI5 walkthrough of hardware fastmem on Windows and Linux"
[extra]
summary = "Explaining how I finally got the grasp about hardware fastmem"
author = "cakehonolulu"
[taxonomies]
tags = ["emulation", "emulator", "fastmem", "fast", "memory", "jit", "dynarec", "hw_fastmem"]
+++

<div style="text-align: center;">

![virtual_memory](https://media.geeksforgeeks.org/wp-content/uploads/20250115142221545470/virtual_memory.webp)
_Slightly simplified virtual memory diagram - Courtesy of GeeksForGeeks_
</div>

## Preface

The following blog entry is more geared towards enthusiasts who may want to optimize their emulation platform
to squeeze some more performance out of it in comparison with more traditional bus designs.

## Memory access patterns in emulation

When we talk about memory access patterns, what we usually mean is, how the emulator handles (Emulated) memory
accesses.

That means, how the target system behaves when it comes to accessing it's memory; be it physical memory,
virtual memory, I/D Caches, IO...

There's usually a few ways of emulating those, usually memory accesses are delegated to certain opcodes.

On MIPS they're **lb**/**lh**/**lw**/*et al* for memory loads, **sb**/**sh**/**sw**/*et al* for stores.

For ARM, **ldr**/**str** pairs for loads/stores respectively... and so on for other ISAs.

So one, has to properly emulate those opcodes and in turn, call the required function to do the access in order
for the execution to be successful.

There's 3 "mainstream" ways of handling this accesses.

### Ranged accesses

This type of access is usually the most common denominator when it comes to popularity. It tends to be simple, effective,
and whilst not super-fast, easy to grasp.

The main idea is to define a predefined amount of memory ranges and use a big if-else chain or a big switch.

Then, based on what each opcode asks for to be accessed, you make the memory handlers check against that value and return
the accessed value accordingly:

**bus.rs:**
```rust
// Reads a byte from memory
fn readb(&self, addr: u16) -> u8 {
    if addr < 0x2000 {
        self.ram[addr as usize]
    } else if addr < 0x4000 {
        let index = (addr - 0x2000);
        self.ppu_registers[index as usize]
    } else if addr < 0x4020 {
        let index = (addr - 0x4000);
        self.apu_io_registers[index as usize]
    } else if addr >= 0x8000 {
        let index = (addr - 0x8000);
        self.rom[index as usize]
    } else {
        unreachable!();
    }
}

// Wrutes a byte to memory
fn writeb(&mut self, addr: u16, data: u8) {
    if addr < 0x2000 {
        self.ram[addr as usize] = data;
    } else if addr < 0x4000 {
        let index = (addr - 0x2000);
        self.ppu_registers[index as usize] = data;
    } else if addr < 0x4020 {
        let index = (addr - 0x4000);
        self.apu_io_registers[index as usize] = data;
    } else if addr >= 0x8000 {
        // ROM is read only
    }
}
```

This is for systems that have no MMU, when systems have an MMU, you first have to do the virtual-to-physical
address translation to get the physical address so you can properly access the correct memory location.

That means that you may need to emulate enough of the MMU to get it to spew the correct PA's (For MIPS-based consoles,
you can usually **&** the high bits and that gives you the PA due to how they "mirror" memory).

### Software fastmem

The main idea behind software fastmem is to have an array of pointers point (_duh_) whose sole objective is mimicking
a page-table structure.

That is, if we were to divide the address space of the target system into pages; we'd have to populate both the read
and the write arrays with pointers to page-size-aligned entries (For RAM, scratchpad...).

So we'd be effectively "mapping" those addresses to our array, simple example (Assuming the pointer array has been built):

**bus.rs:**
```rust
fn sw_readb(&mut self, va: u32) -> u8 {
    let page = (va as usize) >> PAGE_BITS;
    let offset = (va as usize) & (PAGE_SIZE - 1);
    let host = self.page_read[page];
    if host != 0 {
        unsafe {
            (host as *const u8)
                .add(offset)
                .cast::<u8>()
                .read_unaligned()
        }
    } else {
        // IO access
    }
}

fn sw_writeb(&mut self, va: u32, value: u8) {
    let page = (va as usize) >> PAGE_BITS;
    let offset = (va as usize) & (PAGE_SIZE - 1);
    let host = self.page_write[page];
    if host != 0 {
        unsafe {
            (host as *mut u8)
                .add(offset)
                .write_unaligned(value)
        }
    } else {
        // IO access
    }
}
```

As you can see, this approach is much, much more faster; since we "delegate" the costly part on startup (The actual filling
of the page table arrays for reads/writes) and then we just have to index the corresponding page entry (Else we assume it's unmapped
and that means it's usually an IO access for simpler systems or that you may need to update the mappings because a TLB entry was modified f.e.).

There's a great article by wheremyfoodat, [on which it explains perfectly how to archieve this system](https://wheremyfoodat.github.io/software-fastmem/).

So this already cuts down lots of the cost of memory addressing, but we still have one more trick on our sleeves.

## Hardware fastmem

Out of all the methods we've already seen, this one was the most difficult one for me to grasp.

Turns out we can get native-speed (That means, host-level performance) accesses for memory reads/writes for an emulated system.

The way to do this is really tied to what Operating System we want to target and how the emulated system's memory subsystem behaves.

Approach itself should be relatively simple for systems without virtual memory (But you'll have to make some considerations as to how
worth it is to implement hardware fastmem for simpler systems), but complexity increases based on how target system memory access patterns (Because 
one may encounter an MMU and the need to remap memory ranges and that by itself, can become a hassle to do depending on how we tackle it).

This system is also really unsuitable for anything that's not a JIT. Since we kinda need to jump to exception handlers, doing this on a per-memory-access
basis will tank our performance, so from now on, we'll assume that this is targetted for a dynamic recompiler-based emulator.

### Allocating a virtual memory pool

First and foremost, we need to ask the host operating system for a pool of free and usable virtual memory chunk.

The approach varies between Windows and Linux (Other operating systems may also have it's own quirks but won't be covered here) varies.

For instance, under Linux, one would issue a call to `mmap()`:

```rust
#[cfg(unix)]

...
let size = ...;
let base = mmap(
    ptr::null_mut(),
    size,
    PROT_NONE,
    MAP_PRIVATE | MAP_ANONYMOUS,
    -1,
    0,
);
...
```

For this specific case, we ask the kernel for a chunk of `size`, mapped wherever it wants (`ptr::null_mut()`), initially w/o any access to it (`PROT_NONE`) and
not backed by a file, we4 also don't specify a file descriptor (`-1`) since the second flag we specified to `mmap()` is `MAP_ANONYMOUS`. Changes are also private to
the process thanks to `MAP_PRIVATE`.

Thanks to `PROT_MODE` (Not physically backed with anything) we gain a crucial ability for hardware fastmem (Which we'll explain later), faulting on unmapped accesses.

--------------

For Windows, we'll use `VirtualAlloc2()` (Which means that we'll need version Windows 10 v1803 >=, from 2018) because Windows memory management was bound to 64K alignment
[for legacy reasons](https://devblogs.microsoft.com/oldnewthing/20031008-00/?p=42223).

```rust
#[cfg(windows)]

...
let size = ...;
let base = unsafe {
    VirtualAlloc2(
        ptr::null_mut(),
        ptr::null_mut(),
        size,
        MEM_RESERVE | MEM_RESERVE_PLACEHOLDER,
        PAGE_NOACCESS,
        ptr::null_mut(),
        0,
    )
};
...
```

Again, `ptr::null_mut()`'s are, in order, to let the kernel choose the base address, and then so we don't specify a file-mapped region.

`MEM_RESERVE | MEM_RESERVE_PLACEHOLDER`, the crucial bit is `MEM_RESERVE_PLACEHOLDER`, since that's why we use `VirtualAlloc2()` on the first place.

And then, same as with Linux; `PAGE_NOACCESS` to make unmapped accesses fault.

### Adding mappings

To do this under Linux, my way of doing is was using shared memory files. There could be better ways but this one worked for my PS2 Emulator, [RustEE](https://github.com/cakehonolulu/RustEE).

First we open a shared memory file:

```rust
#[cfg(unix)]

...
let name = c"...";
let fd = shm_open(
    name,
    OFlag::O_CREAT | OFlag::O_RDWR,
    Mode::S_IRUSR | Mode::S_IWUSR,
);
...
```

When we have the file descriptor for it, we truncate the size of the fd itself; we can use `ftruncate()` for that:

```rust
#[cfg(unix)]

...
let fd_size = ...;
ftruncate(&fd, fd_size);
...
```

(Worth noting I'm omitting error handling and stuff not to clutter the post with that).

After this, it's a matter of actually adding the mapping to our "base" pointer of virtual addresses:

```rust
#[cfg(unix)]

...
let target = base.add(...);
let map_sz = ...;
let prot = PROT_READ | PROT_WRITE;
mmap(
    target as *mut c_void,
    size,
    prot,
    MAP_SHARED | MAP_FIXED,
    &fd.as_raw_fd(),
    0, /* offset */
);
...
```

This would suffice to have the region mapped. You can also map R/O regions by doing: `PROT_READ` instead of `PROT_READ | PROT_WRITE` (Think 
BootROMs and such).

If you need to copy a BootROM/BIOS/propietary binary over the mapping, you can do it by `mmap()`-ing a simple `PROT_READ | PROT_WRITE` temporal
R/W mapping for the fd, then copying the bytes to it and finally remapping it correctly as R/O (Using `munmap()` and the subsequent `mmap()` to the 
virtual memory pool base):

```rust
#[cfg(unix)]

...
let fd = ...;
let temp_map = ...;
let binary: /* Vec<u8> */ ...;
std::ptr::copy_nonoverlapping(
    binary.bytes.as_ptr(),
    temp_map as *mut u8,
    binary.bytes.len(),
);

munmap(temp_map, sz);
...
```

--------------

On the Windows side of things, we'll use `CreateFileMapping2` to archieve similar results.

```rust
#[cfg(windows)]

...
let sz = ...;
let fd = unsafe {
    CreateFileMapping2(
        INVALID_HANDLE_VALUE,
        ptr::null_mut(),
        FILE_MAP_READ | FILE_MAP_WRITE,
        PAGE_READWRITE,
        0,
        sz,
        /* OsStr */,
        ptr::null_mut(),
        0,
    )
};
...
```

This grants us a memory mapped file.

We then "initialize" the region we'll place the mapping on the pool by issuing a `VirtualFree()` with a special bit set...

```rust
#[cfg(windows)]

let sz = ...;
let addr = ...;
VirtualFree(addr, sz, MEM_RELEASE | MEM_PRESERVE_PLACEHOLDER)
...
```

...and we map the fd to the virtual address pool using `MapViewOfFile3()`:

```rust
#[cfg(windows)]

let res = unsafe {
    MapViewOfFile3(
        fd,
        GetCurrentProcess(),
        base.add(offset) as *const c_void,
        0,
        sz,
        MEM_REPLACE_PLACEHOLDER,
        PAGE_READWRITE,
        ptr::null_mut(),
        0,
    )
};
...
```

Again, if you need to copy any propietary binary to those sections; the approach is similar to that of Linux's.

### Handling accesses

Thanks to leaveraging the host's MMU we can now do memory accesses as follows:

```rust
fn hw_read32(&mut self, addr: u32) -> u32 {
    unsafe {
        let host_ptr = self.base.add(addr as usize) as *const u32;
        *host_ptr
    }
}

fn hw_write32(&mut self, addr: u32, val: u32) {
    unsafe {
        let host_ptr = self.base.add(addr as usize) as *mut u32;
        *host_ptr = val;
    }
}
```

As you can see, this is a vast improvement in comparison with what we had for previous methods.

### Segmentation fault handlers

This pretty much covers memory-backed regions (RAM, ROM, Scratchpad...) but, what about IO accesses for instance? Or TLB exceptions that
may require actually mapping pages or things akin?

Here come custom signal handlers!

The requisite for a JIT for this is explained now, when catching this faults, one can go and patch the emitted memory access machine code (Proven that 
it can be easily identified by heuristics in the case of not being the one responsible for the emission, think LLVM IR or Cranelift; or because you know 
the exact bytes to look for) by the function call to the slower, IO handler.

The general idea is to install a signal handler (`sigaction()` for Linux, `AddVectoredExceptionHandler()` for Windows) for `SIGSEGV` (Linux) or look for `0xC0000005` (Windows) exceptions inside the handler.

After you enter the signal handler, you can retrieve the faulting address (Linux: `(*info).si_addr()`, Windows: `record.ExceptionInformation[1]`) and based on your preferred 
method of action, patch the access accordingly. Be wary that you should anticipate which bus access type it was (read? write?) and length (8/16/32/64... bits) so you should design 
a way of doing that carefully and efficiently (We're in a sighandler, we're not supposed to run lots of code here!).

I personally pre-compute the ranges of each memory access function at start, that is, I store the start and end addresses for each of my memory handler functions and check against that. That way I know the memory access type and length "for free" w/o overcomplicating stuff.

Then you simply patch the call and substitute it with your `io_read()`/`io_write()`. You could try using Capstone or similar to get the system going as a PoC, but I'd recommend against for later versions since it's costly (I ended up doing manual byte-matching heuristics which works well enough for my use-case).

## Results

Reference:

```
AMD Ryzen 5 5600G
32 GB RAM DDR4 3200MHz (No XMP, purely JEDEC)
```

With `sw_fastmem` on my PS2 emulator (Built with `--release`) I get on the ballpark of 250~ FPSs.

The following image is with `hw_fastmem`:

<div style="text-align: center;">

![jit_hw_fastmem](https://cakehonolulu.github.io/images/hw_fastmem/hw_fastmem.png)
_610~ FPSs_
</div>

Pretty worth.