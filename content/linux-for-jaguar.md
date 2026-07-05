+++
title = "'Desktop-ifying' the Atari Jaguar"
date = 2026-07-05
description = "The challenges around porting Linux to an old videogame console by Atari"
[extra]
summary = "Porting process of Linux for a new m68k target"
author = "cakehonolulu"
[taxonomies]
tags = ["c", "linux", "kernel", "atari", "jaguar"]
+++

## What in the tarnation is an Atari Jaguar?

Released in North America in November of 1993, the Atari Jaguar promised to be the new cool kid in the block thanks to it's (Debatable) 64 bits of pure power.


<div style="text-align: center;">

![Atari Jaguar](https://www.hwlegend.tech/wp-content/uploads/2011/03/Atari-Jaguar.png)
_The Atari Jaguar_
</div>

The console itself ended up being a commercial disaster, even after the release of the CD addon, the Jaguar CD; which managed to sell even less units in a desperate attempt to try and compete with the Sony Playstation and the Sega Saturn.

## Why in the tarnation Linux of all things?

Interestingly enough, to this day, Linux has code for the base 68000 processor. It's under ```arch/m68k/68000```.

As a refresher, the Motorola 68000 was a CISC processor with mixed 16-32 bit capabilities (It's usually described as being 32-bit internally due to the register width length and 16-bit because the data bus was 16-bit, so 2-byte transfers at a time).

It had a 24-bit address bus, 2 to the power 24; thereabout a maximum of 16MBs of addressable memory.

It was released on 1979 to compete with the soon-to-be-released 16-bit CPUs of the era.

<div style="text-align: center;">

![M68000](https://www.autoitscript.com/site/wp-content/uploads/2019/03/mc68000_640x314.jpg)
_The Motorola 68000_
</div>

Overall, it got lots of traction commercially; it ended up being incoporated in lots of popular commercial hardware. Biggest contenders are the original Macintosh (And Apple Lisa), the Commodore Amiga series of computers (With varying generations of the 68000), the Sega Genesis/Megadrive, the Neo-Geo AES, Plexus workstations... and the Jaguar.

Let's now address the elephant in the room, why Linux.

Well, it's easy; `because we can` (_-ish_).

## Getting our hands dirty and technical challenges that were overcomed

This design choices basically involved tip-toeing around the very limited characteristics of the machine (Mostly the memory). So you can imagine that lots of kernel features had to be turned off.

The Jaguar has 2 megabytes of RAM (Mapped at $000000), (up to) 6 megabytes of ROM (The cartridge, basically) mapped at $80000 and 2 custom ICs (Tom & Jerry, a "GPU" and a DSP) which are also memory-mapped. 

Jerry, which is the DSP on the board (Which does lots of things, one of them being audio) has 2 dedicated TXD and RXD pins so I figured I'd repurpose to develop a dead simple UART state machine (So I could basically get `earlyprintk` and `earlycon` logging).

Most of the issues with the bringup process were mostly related to design choices I had to do, for instance, we leaverage Linux's mechanism where it lets us have `vmlinux` XIP'd (Execute-in-place: So, `.text`, `.rodata` within ROM boundaries and `.bss`+ `.data` remapped onto RAM at boot).

We also have the issue of what do we want to run when Linux finishes loading; I initially played around with `toybox` and a few other initramfs solutions but fortunately enough, 

I initially thought of using `m68k-linux-gnu-` but strangely (Even after passing `-68000`) it emitted unaligned memory accesses (Which are _no bueno_ on the base 68000) and I had to resort to doing toolchain building.

`crosstool-ng` has recently got support to build for the base 68000 (With `nommu`); which I basically used as a "trampoline" to have a decent toolchain built for the processor; it also takes care of adding one of the features we need toolchain-wise: `elf2flt`.

Since we don't have an MMU, we basically need to enable support for loading the so-called `FLAT` binaries, which can be obtained by linking with `-W,-elf2flt` (Or running `elf2flt` afterwards). This is a complex topic but the gist of it is that it basically needs to pre-handle the relocations (Again, no MMU) the loader may do so that it can be used.

There's a few interesting tidbits that you can basically configure in that regard (Load the entire binary to RAM, do GOT/PLT relocation... all of which can be checked with `flthdr`).

```
❯ flthdr ~/jagfs/rootfs/bin/busybox
/home/cakehonolulu/jagfs/rootfs/bin/busybox
    Magic:        bFLT
    Rev:          4
    Build Date:   Thu Jul  2 03:08:09 2026
    Entry:        0x44
    Data Start:   0x1e0a0
    Data End:     0x25808
    BSS End:      0x2a1c0
    Stack Size:   0x10000
    Reloc Start:  0x25808
    Reloc Count:  0x100e
    Flags:        0x1 ( Load-to-Ram )
```

Pretty nifty thing...

With all this, we basically built a very stripped down `busybox` (We also had to tune `uClibc` malloc strategies to set it as `malloc-simple` else busybox would OOM).

There were some other porting hurdles (The Jaguar has a custom handler on romvec for the #64 which basically routes the TIM0 and VBLANK interrupts which need to be demuxed) but they were mostly easy to overcome thanks to how Linux is programmed (And the amount stuff it let's you override to bring up a platform).

Find the modified Linux repository over at: https://github.com/cakehonolulu/linux_jag

<div style="text-align: center;">

![boot](https://cakehonolulu.github.io/images/linux_jaguar/boot.png)
</div>
