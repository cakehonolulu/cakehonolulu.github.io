+++
author = "cakehonolulu"
title = "How Emulators Work?"
date = "2024-01-09"
description = "How emulators work"
tags = [
    "emulator",
]
toc = true
+++

<br>

I, as many more, grew up playing retro videogames on emulators (And the original hardware!): from sprite-based machines, to more complex, 3D-capable monsters.

![Metal Slug](https://i.blogs.es/juegos/9648/metal_slug_2/fotos/noticias/metal_slug_2-5218501.jpg)
_Metal Slug, an impressive 2D game; developed for SNK's Neo-Geo_
<br>

A few years ago, I started to ask myself how an emulator works; I initially belived it *had* to be some sort of magic, at the end of the day, code is just that, _code_.

There are no transistors or chips or CPUs you can design with code _per se_ (Well, if we ignore programs like LogiSim exist, of course) ... So how do they exactly work?

# What is an emulator?

<br>

Let's start by defining what an emulator (Not to be confused with Simulator) really is.

According to [Wikipedia](https://en.wikipedia.org/wiki/Emulator)'s definition for it:

{{< highlight html >}}
In computing, an emulator is hardware or software that
enables one computer  system (called the host) to behave
like another computer system (called the guest).

An emulator typically enables the host system to run software or 
use peripheral devices designed for the guest system.
Emulation refers to the ability of a computer program in
an electronic device to emulate (or imitate) another program or device. 
{{< /highlight >}}

The key takeaway here, is the _ability_ to run code that is designed for another architecture on our host one.

Examples of this could be, running aarch64 code on your shiny new Intel/AMD PC (Playing a videogame designed for Android, for example); the technique Apple employs for their newer M-line of processors (Which are 64-bit ARM chips) but they are able to maintain backwards compatibility to a degree with macOS software designed for their older Intel machines (And doing so in a fast and efficient manner, using [Rosetta 2](https://en.wikipedia.org/wiki/Rosetta_(software)#Rosetta_2))...

But how can _we_, as individuals, tackle this problem?

Well, there's lots of ways of doing so.

# Types of emulation

<br>

The primary types of emulators that exist can be divided in 2 categories.

A brief paragraph: As of recent times, a new way to experience retro systems has appeared, not to confuse you, but I'll give a brief explanation as to what FPGA-based emulation is and not.

[FPGAs](https://en.wikipedia.org/wiki/Field-programmable_gate_array) are ICs whose behaviour can be repgrogrammed at the logic level after manufacturing.

![Spartan FPGA](https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Xerox_ColorQube_8570_-_Main_controller_-_Xilinx_Spartan_XC3S400A-0205.jpg/220px-Xerox_ColorQube_8570_-_Main_controller_-_Xilinx_Spartan_XC3S400A-0205.jpg)

What this basically means is, that you can effectively replicate any existing chip on an FPGA provided that you have the required schematics for it.

But here comes the thing; is it really emulation if it yields the same 1:1 behaviour (Timings, instructions... wise) as the original chip?

Well, this is a hot area of debate; but once you reprogram the FPGA to fit your needs, you don't have to think of it as an "alive" machine, it's _effectively_ the same as the chip it's trying to mimick; down to the pins and address lines, and it'll stay that way _physically_ unless reprogrammed.

So in my opinion, no, it's not "emulation" _per se_ but still a cool technique that gives the utter best results.

Anyhow, back to the main topic.

# HLE vs LLE

<br>

There's two ways to understand emulation; and this varies by the level of closeness to the hardware you decide to entangle yourself with.

## LLE

<br>

LLE stands for Low-level Emulation. What this means is, closely replicating the target hardware at the bare-metal level.

You must emulate every bit of the system to make it work; that means implementing a CPU core that can execute the foreign instructions; providing an interface for it to send/recieve data to/from peripherals and respecting the timings of all the components to make it as accurate as possible (You can read further on this topic if you look up [Cycle Accuracy](https://retrocomputing.stackexchange.com/a/1195)).

## HLE

<br>

HLE on the other hand, can be understood as a MITM between the target library calls and mapping them to host-compatible ones; let's say we have _System A_ which, somewhere on it's code, does this:

{{< highlight c >}}
// System A function responsible of init-ing the FB
int libGfxInitFramebuffer()
{
    if (libGfxSetupFramebuffer())
        goto fail;

    if (libGfxClearFramebuffer())
        goto fail;

    return 0;

fail:
    libDebugPrint("Failed to initialize the framebuffer!");
    return 1;
}
{{< /highlight >}}

If we're trying to HLE System A, we need to figure out a way to first, detect that this function is being called (Normally, there's a piece of code responsible for intercepting, for example, syscalls) and instead of executing the target code, executing a function written for the host architecture that archieves the same but without relying on the target-specific hardware details.

We could for example, intercept it and call the following code in a PC:

{{< highlight c >}}
// Host system function responsible of init-ing the FB
// Assuming we're using SDL and renderer is a SDL_Renderer
int libGfxInitFramebuffer()
{
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
    SDL_RenderClear(renderer);
    SDL_RenderPresent(renderer);

    // We do not handle error-checking for simplicity's sake
}
{{< /highlight >}}

And that's the basic principle behind HLE. You also need a way to intercept those library calls; for example, let's say we're interpreting target (System A) CPU instructions, and suddenly, we encounter a ```syscall``` instruction.

Let's assume this ```syscall``` instruction in System A works by specifying the ```syscall``` type on register ```A``` and the required arguments on registers ```B``` and ```C```.

Imagine we find this:

{{< highlight asm >}}
move 3, $A
syscall
{{< /highlight >}}

This basically would call syscall number 3 on the syscall table, which, for example, could be our previously explained ```libGfxInitFramebuffer()```.

You'd then need to detect this behaviour whilst executing the target code, intercept it and redirect execution and adjust the emulation state accordingly (Maybe adjusting cycle count to account for the original length of the syscall function... etc).
