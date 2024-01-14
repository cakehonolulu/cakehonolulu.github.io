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

<div style="text-align: center;">

![Metal Slug](https://i.blogs.es/juegos/9648/metal_slug_2/fotos/noticias/metal_slug_2-5218501.jpg)
_Metal Slug, an impressive 2D game; developed for SNK's Neo-Geo_
</div>

A few years ago, I started to ask myself how an emulator works; I initially believed it *had* to be some sort of magic, but at the end of the day, code is just that, _code_ (_Technically_, you _can_ develop an emulator from an ECE-perspective; look up [Verilog](https://en.wikipedia.org/wiki/Verilog) or really, any [Hardware-Description-Language](https://en.wikipedia.org/wiki/Hardware_description_language), but that's beyond the scope for this post).

# What is an emulator?

<br>

Let's start by defining what an emulator (Not to be confused with simulator) really is.

According to [Wikipedia](https://en.wikipedia.org/wiki/Emulator):

{{< highlight html >}}
In computing, an emulator is hardware or software that
enables one computer  system (called the host) to behave
like another computer system (called the guest).

An emulator typically enables the host system to run software or 
use peripheral devices designed for the guest system.
Emulation refers to the ability of a computer program in
an electronic device to emulate (or imitate) another program or device. 
{{< /highlight >}}

The key takeaway here, is the _ability_ to run code that is designed for one system on another one.

Examples of this could be, running aarch64 code on your shiny new Intel/AMD PC (Playing a videogame designed for Android, for example); the technique Apple employs for their newer M-line of processors (Which are 64-bit ARM chips) but they are able to maintain backwards compatibility to a degree with macOS software designed for their older Intel machines (And doing so in a fast and efficient manner, using [Rosetta 2](https://en.wikipedia.org/wiki/Rosetta_(software)#Rosetta_2))...

But how can _we_, as individuals, tackle this problem?

Well, there's lots of ways of doing so.

# Types of emulation

<br>

The following paragraph contains information about a type of emulators that have lately emerged; they're more state-of-the-art in comparison with good-old already-existing emulators, it's meant to illustrate, it can be confusing for newbies so you can skip to the [HLE vs LLE](#hle-vs-lle) chapter if you want.


---

A brief paragraph: As of recent times, a new way to experience retro systems has appeared, not to confuse you, but I'll give a brief explanation as to what FPGA-based emulation is and not.

[FPGAs](https://en.wikipedia.org/wiki/Field-programmable_gate_array) are integrated circuits whose behaviour can be repgrogrammed at the logic level after manufacturing, they can be programmed using HDL's (Hardware description languages) which goes through a series of steps before getting executed by the development board.

<div style="text-align: center;">

![Spartan FPGA](https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Xerox_ColorQube_8570_-_Main_controller_-_Xilinx_Spartan_XC3S400A-0205.jpg/220px-Xerox_ColorQube_8570_-_Main_controller_-_Xilinx_Spartan_XC3S400A-0205.jpg)

_The Xilinx Spartan FPGA_
</div>

What this basically means is, that you can effectively replicate any existing chip on an FPGA.

In comparison with traditional emulators (Which, run on top of an operating system), FPGA-based emulators have a bunch of neat advantages due do the nature of the technology itself.

For example, operating systems tend not to give you a fine-grained scheduling; let's say your emulator wants to handle keypad inputs; you need to somehow interact with the underlying OS to perform such task, but the OS itself can then assign the priority it sees fitting so the latency (Normally in miliseconds) can fluctuate making accurate emulation really difficult. Worth mentioning, that normally, the more accurate it needs to be, the more power-hungry the emulator will end up.

FPGAs benefit from the parallelism they can archieve due to their nature, and also can maintain the components clocked much more accurately again, due to their nature; doing so while not requiring as much power as a normal, PC emulator.

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

It's also important to note, that nowadays (Moreso with more recent consoles), there's a trend to mix both LLE and HLE techniques to get thehe benefits of both approaches. There's some components that you can HLE to reduce the processing hurdle of more complex subsystems a machine can have.

# Defining the target

<br>

Now that we finally have laid down the concepts related to emulation; let's find a target that has a CPU that has a relatively easy implementation in software.

We'll focus for example on the Amstrad GX4000. A 3rd generation, PAL home console that was launched in the 80s.


<div style="text-align: center;">

![Amstrad GX000](https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Amstrad-GX4000-Console-Set.png/1280px-Amstrad-GX4000-Console-Set.png)
_The Amstrad GX4000_
</div>

The specs are very straightforward; an 8-bit Zilog Z80A at 4 MHz a custom chip that handled sprites, Sound DMAs and Interrupts.

Sound-wise; a 3-channel stereo, AY-3-8912 chip.

As for space, 64 KiB of RAM, 16 KiB of Video RAM and 32 KiB of ROM.

Really simple.

We'll focus on CPU emulation and we'll ignore the rest of the peripherals for now.

# Emulation loop

<br>

Once you find the detailed specs for the machine you want to target; it's time to work.

The usual recommendation is to find on the Internet as much documentation as you can; but depending on the target, you may find less stuff; so be prepared to reverse-engineer if needed.

For the major players in the market, there's popular resources online that give a very detailed explanation of the entire system; but again, your mileage may vary.

The basics for emulating a CPU are, knowing how a CPU works, here's a pretty simple diagram:

<div style="text-align: center;">

![FDE Cycle](https://i.pinimg.com/originals/d7/f0/29/d7f0297a06f5f6e36f8cbd50a77a1fc9.png)
_The fetch-decode-execute cycle_
</div>

Basically, we need to fetch data from the memory, decode it and execute it; profit.


<div style="text-align: center;">

![Owl](https://i.kym-cdn.com/photos/images/newsfeed/000/572/078/d6d.jpg)

_2 simple steps!_
</div>

In all seriousness; it's really that *simple*¹

<p style="font-size: 0.7rem"> ¹.- Depending on the CPU, it may be less simple (Think of possible address modes, the straightforward-ness of the opcode decoding, the pipeline it may have, the timings...) </p>

Let's get down

# CPU emulation techniques

<br>

## Interpreter

<br>

We'll start with the more easier type of technique; an Interpreter.

Let's have some pseudocode explain the rest, we'll do some assumptions that don't map to the real Z80A, to simplify the explanation and the code (We assume opcode size == 1 byte, no addressing modes, no banked register set...):


{{< highlight c >}}
// Ignoring the boilerplate code, such as headers, irrelevant functions and such

struct Bus {
    byte ram[64 KiB];
    ....
}

struct Cpu {
    byte A, B, C, D, E, H, L; // General-Prupose Registers
    byte F; // Special Flags Register
    byte IX, IY; // Index Registers
    byte SP; // Stack Pointer Register
    byte PC; // Program Counter Register
    ...
}

/*
    Bus and Cpu are initialized by main() or another function,
    the ram array has the target binary already loaded at a
    specific offset and the PC (Which effectively acts as a
    pointer to memory) is set to that memory offset.

    That way once we read from ram we can just do ram[cpu->PC]
    to get the opcode.
*/
void cpu_fde(Bus *bus, Cpu *cpu)
{
    // Get the cpu instruction from memory pointed by the PC register
    byte opcode = bus->ram[cpu->PC];

    switch(opcode)
    {
        // ADD A, B Instruction
        case 0x00:
            // Add B to A
            cpu->A += cpu->B;
            // Increment PC
            cpu->PC++;
            break;

        case ...:
            ...

        ...

        default:
            printf("Opcode unimplemented! 0x%02X\n", opcode);
            exit(1);
    }

}

{{< /highlight >}}

This is the skeleton for an emulator; think of the PC (Program Counter, sometimes also called IP, Instruction Pointer) register as a pointer to memory from where we'll read instructions from.

Normally, the PC then will get incremented by 1 at the end of the opcode processing (But some opcodes that handle PC relocation, such as JUMPs or CALLs may add an offset to it or straight up setting it to a determinate value).

In reality, PC will increment ```sizeof(opcode)```, but there may be some exceptions to that in some architectures; be always mindful when designing the main loop.

And that's it, you've just designed a primitive interpreter loop.

This is one of the many ways to implement the fetch-decode-execute loop; and one of the slowest ones too; think the amount of instructions per second you need to decode and execute in 8MHz's worth of time.

It adds up.


## Cached Interpreter

<br>

So far we've covered the basis for an Interpreter; but there's other techniques to gain an advantage, speed-wise.

For instance, you could cache the instructions you're translating in blocks so that it alleviates the fetch-decode hotspot a bit; as it'd only need to process it once (Ignoring that code can be self-modifying and in that case you'd need to invalidate and recompile the affected block; but that's for another day).


## Dynamic Recompiler

<br>

By far, one of the most efficient ways to tackle emulation is by developing a Dynamic Recompiler (Just-in-Time compiler); which interprets the target, arch-uncompatible instructions; and translates them to host instructions. For example, [Rosetta 2](https://en.wikipedia.org/wiki/Rosetta_(software)#Rosetta_2) converts x86_64 instructions to aarch64 ones and runs them in a efficient and fast manner.

It's one of the most complex ones, but also, one of the most rewarding ones; there's several challenges to tackle when developing a Dynamic Recompiler; such as deciding how to to the actual recompilation:

Do we want an emitter that directly translates the instructions? Maybe we want instead to use some sort of IL (Intermediate language) so that a compiler backend (Think, LLVM) can introduce code optimizations and do the translation? How do we handle self-modifying code? And what about register spilling (Imagine targetting an arch that has more registers than your host one, you may need to use some stack trickery or another technique to decide the least used registers and swap them into the host ones as needed)?

As you can see, there are many more challenges when trying to go the Dynamic Recompilation route; but it's a really interesting path to go down.


<div style="text-align: center;">

![JIT](https://static.wixstatic.com/media/0ca71f_1a3d7cffee16433db44fb5155c7e225a.png/v1/fill/w_1132,h_818,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/0ca71f_1a3d7cffee16433db44fb5155c7e225a.png)

_A simple JIT diagram, it also needs a cache for the compiled blocks_

</div>

# Peripherals

<br>

There's also the added challenge of handling peripherals; there's cases where you'll find I/O operations CPU-wise that interact with the peripherals on the system; or some other times, they can be memory-mapped.

In any case, there's some food for thought involved into deciding the best way to tackle both of the systems.

A simple, pseudocode example that explains the memory-mapped approach:

{{< highlight c >}}

/*
    This can be called with opcodes like LOAD ($A), $0x20
    (Loads 0x20 to the address pointed by A)
*/
void memory_write_byte(Bus *bus, Cpu *cpu, long address, byte value)
{
    switch (address)
    {
        // Main RAM
        case 0x0 ... 0x1000:
            bus->ram[address] = value;
            break;
        cd 
        // Memory-mapped I/O
        case 0xFF10:
            bus->set_sprite_a_register(value);
            break;

        default:
            printf("Unhandled address! 0x%04X\n", address);
            exit(1);
    }
}

{{< /highlight >}}

There's also some other considerations to have; think about how you want to plot graphics; or play audio, or read from a filesystem... there's some design choices to be made in order to properly handle the rest of the system aside from the CPU and presenting it to the user (Or letting him interact with the emulated environment!).

# Bonus Track

<br>

## AoT

<br>

There's also a thing called Ahead-of-Time recompilation which, as you have probably already guessed; recompiles the entire target binary before running it to host-compatible machine code.

It's not purely emulation, but it's still a form of recompilation; it's incredibly difficult because it shares a problem that Dynamic Recompilators have; self-modifying code. If you AoT recompile a target code but it ends up self modifying, you can end up with some interesting results.

# Credits

<br>

With all this being said, I hope the reader finds some understanding in what emulation is about!

Feel free to reach out to me in case you need more resources!

You can also join us @ the [EmuDev](https://discord.gg/7nuaqZ2) Discord; there's plenty of knowledgeable people that will help you in your journey!
