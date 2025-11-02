+++
title = "Introducing PCIem"
date = 2025-11-02
description = "A framework enabling in-host driver development thanks to Linux and QEMU"
[extra]
summary = "Detailing a free & open-source method to develop PCIe drivers"
author = "cakehonolulu"
[taxonomies]
tags = ["c", "linux", "kernel", "pcie", "qemu"]
+++

## First of all, why

When we try to look at how companies/groups/whoever try to do PCIe driver development it usually goes in 2 possible ways:

1.- They don't care about PCIe

Which is the sanest way. Honestly if you care about you and your teams sanity this is the way to go. Usually involves building a shim or some sort of abstraction layer that avoids the hassle of going down the driver level to do some general useability tests.

2.- They care about PCIe

They chose violence. Usually requires complex co-simulation/co-emulation models. We're talking multiple-people efforts right here. Sometimes commercial solutions can be used but they can be pricey. There's also SimBricks (Which is open-source and works great!) but if you care a bit about speed and not so much about tight timings it can be costly.

--------

What if I told you that you, in fact, can model your PCIe card with QEMU as a standalone device and get your *host* Linux instance to recognize it in it's PCI bus?

Bonkers.

## PCIem (or a speedrun on getting Linus mad)

I've been experimenting for a while on how to convince Linux's PCI subsystem functions that there's a PCI device attached to the host bus without one being attached. Sounds crazy but I thought it could be something worth experimenting.

My initial impression was that I would have to go and hack Linux from within and have custom kernels and whatnot to have this (Mainly getting rid of sanity checks and whatnot to let this work) but it turns out you can do one trick that'll let you do that from a kernel module w/o ever touching the kernel's source code.

## memmap cmdline argument

Turns out you can provide a commandline argument to Linux so that it "reserves" a physical memory chunk from the ```"System RAM"``` resource node.

Let's say your ```/proc/iomem``` tells you that your "System RAM" node is ```0x10000000-0x1FFFFFFF```. If we instruct Linux to boot with: ```memmap=64K$0x1FFEFFFF``` it'll carve the last ```0x10000``` and not assign it to ```"System RAM"```. This means that we have a "free" and "unused" region we can work with. This is, in part, the root of the mechanism we exploit for PCIem.

## Adding a Synthetic PCIe device

Using ```pci_scan_root_bus()``` and having a specially-prepared ```struct pci_ops``` with the ```read``` and ```write``` handlers containing some cool code makes it so that Linux props up a new PCI device on the bus as if it physically existed there.

When the kernel probes the new device, it ends up calling those functions on the struct; by carefully setting the parameters, we can specify the PCI device properties. From ```VENDOR_ID``` to ```DEVICE_ID```, to extended capabilities, to ```MSI``` configuration, ```DMA```... and whatnot.

You can take a closer look on the source code of [pciem.c](https://github.com/cakehonolulu/pciem/blob/main/pciem.c) (```vph_read_config()```, ```vph_write_config()```, ```vph_fill_config()```).

## BAR remapping

When we have to back the BAR0 memory we can use the carved region from ```memmap``` because when it tries to take ownership of it the PCI subsystem won't complain as it won't see it belonging to ```"System RAM"``` and thus won't return ```"-EBUSY"```.

This enables your usual PCIe driver to do ```"pci_iomap()"``` as if nothing.

```"ioreadX()"``` and ```"iowriteX()"``` functions also work just fine (Which was kinda expected since it basically works at the memory-barrier levels and whatnot).

## MSIs

For MSIs, what I did was find the assigned synthetic PCIe MSI number and I queued the handler with ```irq_work_queue()```. From the safe(r) kernel context where ```"pciem_msi_irq_work_func"``` gets called it just does ```"generic_handle_irq(num)"``` which should run all the registered handlers. Which in turn runs the actual PCIe driver's ```"pci_irq_handler"```.

Based on my testing it's completely indistinguishable from a real, hardware-triggered MSI for the driver; but feel free to try and make it explode :)

## DMA

The gist of it is to basically setup a communication flow between the userspace proxy that handles kernel<->proxy<->QEMU transactions so that when actual DMA needs to happen (Writes from and to DMA allocated buffers) everything gets proxied.

The real driver usually does ```"dma_alloc_coherent()"``` which returns both a virtual address and a physical address (```dma_addr_t```).

Those values move across the framework, when QEMU "initiates" the DMA it has to ask PCIem to do the reading from the ```dma_addr_t``` (Since we can't do that from userspace...), it effectively proxies the DMA request up to the kernel basically.

PCIem then becomes sort of a "DMA engine"; when the IOMMU is off, we're just a ```phys_to_virt()``` call away to be able to copy the data directly to the proxy's "virtual DMA buffer".

If the IOMMU is on, ```dma_addr_t``` is an **IOVA** (I/O Virtual Address), not a physical one. I found out about this doing lots of debugging and observing that the phys address returned by ```dma_alloc_coherent()``` being ```0xFFFF0000``` always (Without ```amd_iommu=off```). Is it some sort of software-controlled trampoline?

Anyhow, for IOVA handling, I had to loop page-by-page for the DMA's ```len``` doing ```iommy_iova_to_phys()``` to get the IOMMU to handle the translations for me. Then the ```phys_to_virt()``` and subsequent ```copy_to_user()```.

## Handling PCI commands

I had to resort to a poller (Which runs on a kernel thread monitoring for a changed value in the BAR)... yeah, less than optimal but hey, it works!

I've been experimenting with "sequential" ways of handling this, but couldn't figure something that works good enough and doesn't look ugly (I tried memory watchpoints but they apparently don't work on physical addresses which we use for BAR stuff).

Anyhow, I can get stable output from DOOM and Quake at 640x480@120 (8BPP).


<div style="text-align: center;">

![doom](https://cakehonolulu.github.io/images/pciem/doom.png)
_DOOM_
</div>


<div style="text-align: center;">

![quake](https://cakehonolulu.github.io/images/pciem/quake.png)
_Quake_
</div>
