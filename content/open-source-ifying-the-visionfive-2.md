+++
title = "Pushing VisionFive 2 RISC-V board into 2025"
date = 2025-05-05
description = "Because Open Source *always* ends up taking the reins"
[extra]
summary = "Detailing how I pushed the SBC to have an up-to-date stack (Minus EDK2)."
author = "cakehonolulu"
[taxonomies]
tags = ["visionfive2", "vf", "risc-v", "riscv", "rv", "sbc"]
+++

<div style="text-align: center;">

![vf2_board](https://cdn.armbian.com/wp-content/uploads/2023/03/vision-five2.png)
_StarFive's VisionFive 2 RISC-V Board_
</div>

## Trip down the memory lane

Bit of a preface:

I bought this board somewhere in June 2024; I plugged it in to verify it worked and that was pretty much it; I remember
interfacing it through UART and it came with a super custom Debian-based distro on an SD Card. It also came with a 128GB eMMC
module (I had never seen removable eMMC module until that point!) which kinda increased the cool factor for me.

It felt super cool to start seeing "mainstream" adoption of RISC-V, this new and open-source ISA that had started
powering electronics all around the globe; but how was the software stack?

It was *okay*...*-ish*

Let's start by saying that considering how costly it is to develop the ecosystem, we, the users, can't really expect upstream
support from day one; heck, sometimes even after years in production, products still are closed source and are pretty much destined
to die off slowly without the help of the Open Source community!

So yes, it was okay-ish but it served good; hardware accelerated graphics, external displays, a network stack... It was and **still is**,
usable, but we can make it even better.

## The hardware

The VisionFive 2, is powered by a JH7110 SoC, containing 1.5GHz quad-core 64-bit RISC-V Scalar Processor implementing **RV64IMAFDCSUZicsr_Zifencei_Zba_Zbb** features (It's basically **RV64GC** plus **Zba** and **Zbb**).

It has a few other goodies, such as an Imagination GPU and so on; but this are irrelevant for us right now.

It's by no means fast, but it doesn't pretend to be; it's sole prupose was/is being an early-adoption board so that the enthusiasts/companies can run their tests on to gauge how it may look like on actual hardware; so that by itself, is quite the feat already.

At some point in late '24 the (Supposed) successor to the 7110, the 8100, was mentioned on a Linux Kernel Mailing List; but it hasn't been officially announced/released as of May 2025.

Now that we understand the basics of our SoC...

## How much has been already upstreamed?

I started looking at probably the easiest place to check for mainline support...

### Linux!

Lo-and-behold, there's patches that have already been upstreamed to support the SoC and it's peripherals; as of May 2025 there's still some that haven't
been merged yet (Most important one, being the HDMI controller logic, DRM... and whatnot) and I personally think they probably won't be merged because
it's been a bit of a while since last activity on patchwork; but you can easily download the patches in .mbox format if needed and apply them manually into
your tree.

I only had to search for a defconfig, [thankfully the cool people over at StarFive already have a Linux tree with one](https://github.com/starfive-tech/linux/) (`starfive_visionfive2_defconfig`), clone the project and target that config; it all compiled fine and booted first try. All the major things I mainly need the board to have working (Ethernet, NVME, SD Slot and eMMC), worked first try.

It is worth noting I have not personally tried the GPU on it's own (Haven't connected the board to a monitor nor have tested the hardware acceleration, video encoding/decoding...) so if that's a feature you actually need, it's a bit of a mistery for me. I planned on using this as a headless homelab-esque machine to run some stuff on.

So there we had it, VF2 board running the latest and greatest Linux version! But... I figured I may as well not stop there...

## VisionFive 2 Boot Process

### RISC-V Machine-mode stage

*NOTE: This may have inaccuracies since I don't work for StarFive, it's based on my personal interpretations and findings/reverse engineering regarding the board whilst doing all the work on it.*

When the board powers on, the CPU executes a ZSBL (Zero-stage bootloader) presumably off of an EEPROM or something similar, it's read-only and you can't access it's contents because it's unmapped as soon as the rest of the boot chain starts executing; you could probably try sniffing the contents out of it if provided it's not in the die package of the SoC an is located somewhere in the board; but considering the things it does it's probably best just to ignore it since it's unique task is bootstrapping the processor to the next stage (So most probably, boring assembly to do all of this; nothing interesting).

Then, it jumps to a cut-down u-boot that gets loaded off of flash storage. It's called **u-boot SPL** (**S**econd **P**rogram **L**oader), it basically exists to provide a bit of a richer environment to run code on; it has a few interesting things bootloader-wise (It can load things off of an SPI NOR/NAND for instance) but not much else; it's task is to bootstrap into OpenSBI to finally enter RISC-V's S (**S**upervisor) mode and act as a handler for a few "supervisor" calls launched from lower privilege levels.

{% mermaid() %}
graph LR
    ZSBL["ZSBL<br/>(Zero stage bootloader)"] --> SPL["u‑boot SPL<br/>(Second program loader)"]
    SPL --> OpenSBI["OpenSBI"]
    ZSBL -.-> M["Machine mode"]
    SPL -.-> M
    OpenSBI -.-> S["Supervisor mode"]

    %% -- node colour classes with contrasting text color
    classDef m_mode fill:#FF9A00,stroke:#333,stroke-width:1px,color:#000;
    classDef s_mode fill:#FF0000,stroke:#333,stroke-width:1px,color:#000;

    %% -- assign nodes to classes
    class M m_mode
    class S s_mode
{% end %}

### RISC-V Supervisor-mode stage

Now we're on supervisor mode thanks to OpenSBI, what happens now is that it tries loading the actual u-boot (Not the cut-down SPL) from the flash and jumps to it.

This is where things start getting interesting because it's where the gates really open up to anything; but to keep it simple, we just need to know that u-boot is autoconfigured to load a "DTB" (**D**evice **T**ree **B**inary, think of it of a **much** saner ACPI without the x86 ugliness) that contains the board's required information that Linux needs to parse in order to load itself and init the board's components; then Linux and finally jumping to it, but it can do so _officially_ from 3 different places:

* eMMC storage
* Micro SD Card
* NVME drive

(The unofficial way would be to store it on the flash the board has, it's 16MiB after all, but that means you'll need to do some memory juggling because the SPL and the rest of u-boot/OpenSBI have predefined memory ranges on the flash and must not overlap for obvious reasons).

So once the boot media is decided, it does the exciting `jmp` (Or should I say `j`...?) to Linux.

Incidentally, Linux also _technically_ runs in S-mode; so we're missing one last stage; current event horizon is as follows:

{% mermaid() %}
graph LR
    UBOOT["u‑boot"] --> eMMC["eMMC"]
    UBOOT --> SDIO["SDIO<br/>(SD Card)"]
    UBOOT --> NVME["m.2 NVME"]
    
    eMMC --> Linux["Linux"]
    SDIO --> Linux
    NVME --> Linux
{% end %}

### RISC-V User-mode stage

Right after Linux finishes bootstraping all the required things for it, proceeds to setup user-mode registers (CSRs) and delegates the control to the least-privilged mode sometime after loading the required system services. So in a way, Linux _kinda_ lives in 2 separate privilege levels at the same time (Not that different from what you'd see on x86 _technically_).

{% mermaid() %}
graph LR
  %% -- Machine mode group
  subgraph "Machine mode"
    direction TB
    ZSBL["ZSBL<br/>(Zero stage bootloader)"]
    SPL["u‑boot SPL<br/>(Second program loader)"]
  end

  %% -- Supervisor mode group
  subgraph "Supervisor mode"
    direction TB
    OpenSBI["OpenSBI"]
    UBOOT2["u‑boot"]
    eMMC["eMMC"]
    SDIO["SDIO<br/>(SD Card)"]
    NVME["m.2 NVME"]
    LinuxSup["Linux supervisor mode"]
  end

  %% -- User mode group
  subgraph "User mode"
    direction TB
    LinuxUser["Linux user mode"]
  end

  %% -- flow arrows
  ZSBL    --> SPL
  SPL     --> OpenSBI
  OpenSBI --> UBOOT2
  UBOOT2  --> eMMC
  UBOOT2  --> SDIO
  UBOOT2  --> NVME
  eMMC    --> LinuxSup
  SDIO    --> LinuxSup
  NVME    --> LinuxSup
  LinuxSup--> LinuxUser

  %% -- styling
  classDef machine    fill:#FF9A00,stroke:#333,stroke-width:1px,color:#000
  classDef supervisor fill:#FF0000,stroke:#333,stroke-width:1px,color:#fff
  classDef device     fill:#B3E6B3,stroke:#333,stroke-width:1px,color:#000
  classDef usermode   fill:#A3CEF1,stroke:#333,stroke-width:1px,color:#000

  %% -- assign nodes to classes
  class ZSBL machine
  class SPL machine
  class OpenSBI device
  class UBOOT2 device
  class LinuxSup device
  class eMMC device
  class SDIO device
  class NVME device
  class LinuxUser usermode

{% end %}

That's it, that's the full chain.

There's been some developments lately that I had been following closely; but that'll also come later.

## Updating u-boot

In a similar fashion as Linux, u-boot also has the VisionFive 2's tidbits upstreamed; so you can pretty much download the source code, compile it and flash it (Both the SPL and u-boot itself) and you'll automatically have a much updated version; no big deal here...

...except if you want the VisionFive 2 to run UEFI.

## Fixing u-boot SPL to boot EDK2

StarFive employees pointed in the forums that a preview of EDK2 could be installed on our boards. It works well, but there's 2 minor catches for me:

* You must run their old u-boot fork with the SPL patches to get it to load EDK2
* You must run their old edk2 fork with VF2 patches

It's worth noting that even after 3 days of work I haven't had the time to upgrade the EDK2 version, but this'll do for the meantime (I'm actually working on that as of writing this blog, if I succeed I promise a future entry here!).

So I got my hands to work...

...though I couldn't progress much; apparently for some reason I've not had the time to investigate further (Other than finding the root issue) but the SPL can't figure out the FDT location inside the SPL binary and crashes on NULL address...

I made what is [probably one of my worst hacks ever](https://github.com/cakehonolulu/u-boot_vf2/commit/7c47c5c85bd0db430deae63eeb56bcd7cdbf0f0e#diff-434931895d55117620bd7f8ab9f55ada1d4510572a9750b6d13e985d93548bfaR778), I calculate the address in advance and just offset the base address accordingly; this is stupid (It means you have to `hexdump` the resulting binary searching where the the FDT header is to fix the offset everytime code size changes or different compilers... etc). But hey, it works; once I have the time to investigate this it'll probably end up somewhere in the u-boot code.

With this, we have StarFive's EDK2 running again, but I wasn't still satisfied; I wanted to be the one provisioning the board with my own binaries (Not that I don't trust StarFive or things you may be thinking, it's just personal preference purely for the funzies).

## Crying over EDK2 and fixing it

EDK2 sucks. Literally.

I cannot withstand how it's organized, but even less, how it's compiled.

It's reminiscent of my old days (2014~, I was barely 13 years old) when I started doing Linux kernel hacking to get a more recent version running on an old phone I had that used a MediaTek SoC.

They had a custom build system built around the kernel that was outdated by the time I tried to compile it (I even had to download 5~ year old Ubuntu versions at that time, 9.04, to satisfy the scripts...).

_(It's great actually, impressive project; but I wanted to vent)._

So yeah, expect environment variable _shenanigans_ and lots of trial and error; I've built EDK2 about 100~ times in the weekend I'm writing this entry and yet sometimes I still can't figure out what I'm missing to get it to compile.

Long story short; to make EDK2 work with my upstreamed u-boot SPL, I've had to update all the device tree information and misc. regarding the board else it wouldn't do anything. You can see the required changes [here](https://github.com/starfive-tech/edk2-platforms/commit/523d36a471dc7f7238176330e4cd38ebfa1e623a).

At some point EDK2 started booting again so I got all excited...

...but then it failed again (It always does).

This remains to be fixed, but since I personally don't use SDIO/eMMC anymore to boot the board (I just use an NVME I had laying around) I just went in and [disabled the MmcDxe from running](https://github.com/starfive-tech/edk2-platforms/commit/02294fd40e46378b8050f8a0c19ffafcf7a8d6f5).

<div style="text-align: center;">

![edk2](https://cakehonolulu.github.io/images/visionfive2_upstreaming/edk2.png)
_EDK2 running on updated VisionFive 2 board_
</div>

It's worth noting that I had some issues regarding Linux booting, I had to customize the `EFI/BOOT/startup.nsh` file a good bit to make it log correctly and so on (Also, to no try and find a initrd in memory failing miserably because I don't have one...).

## Debian sid

Debian Trixie appears to be supporting the `riscv64` arch so I figured, why not building an image out of it? `debootstrap` it was!

I built an ext4 image that I simply wrote over a partition on the NVME and Linux took care of it by specifying the `root=` and `rootwait` cmdline parameters on `startup.nsh`.

I'll probably end up writing a blog regarding `debootstrap` because it also gave me quite the headache...

But the end result was, very, very worth it:


<div style="text-align: center;">

![result](https://cakehonolulu.github.io/images/visionfive2_upstreaming/fastfetch.png)
_SSH connection to the board, showcasing fastfetch, true EFI and Trixie Debian_
</div>

All in all, a frustrating-yet-insanely cool experience.