# Getting started

## Cloning the repository

In order to use PCIem, we'll first clone the repository:

```bash
git clone https://github.com/cakehonolulu/pciem
```

With the repository already cloned, we'll enter it:

```bash
cd pciem/
```

## Compiling the code

To compile PCIem, it should be enough to have `make`, a C compiler & the Linux headers for your currently-running kernel.

Depending on the amount of features your userspace-PCI shim has, you may need further requirements (Think of, displaying a framebuffer the driver writes on with `SDL3` or alike); but for a simple one, the aforementioned ones will suffice.

Issuing a compilation is as simple as:

```bash
make all
```

## Using PCIem

After we compile everything, we'll end up with a bunch of object files, an executable and a kernel module.

In short, the way this framework works is by loading the `pciem.ko` kernel driver (With a certain set of parameters that'll be discussed below), then loading the userspace-shim that actually creates the device using the exported functionalities of PCIem, and finally; you load the actual (Untouched!) PCIe driver you want to test.

```c
┌───────┐     ┌──────────┐     ┌────────────┐
│ Linux ├─────► pciem.ko ├─────► User-space │
└───────┘     └──────────┘     │    shim    │
                               └────────────┘
```

### PCIem parameters

#### pciem_phys_regions

Let's start with the preface that, we're obviously going to use `insmod` to load `pciem.ko`, but the way we do it changes the behaviour of the framework.

Starting from PCIem 0.1, one can specify kernel module arguments to alter/instruct certain logic on the code.

`pciem_phys_regions`: This basically specifies what physically-contiguous memory regions are reserved and free to use by PCIem. This is attained by passing the `memmap=` argument to Linux's `cmdline`.

As per kernel.org's [`memmap`](https://www.kernel.org/doc/html/latest/admin-guide/kernel-parameters.html):

```
memmap=nn[KMG]$ss[KMG]
                        [KNL,ACPI,EARLY] Mark specific memory as reserved.
                        Region of memory to be reserved is from ss to ss+nn.
                        Example: Exclude memory from 0x18690000-0x1869ffff
                                 memmap=64K$0x18690000
                                 or
                                 memmap=0x10000$0x18690000
                        Some bootloaders may need an escape character before '$',
                        like Grub2, otherwise '$' and the following number
                        will be eaten.
```

This effectively means that, if we append the following to the `cmdline`:

`memmap=128M$0x1bf000000`

Linux is going to carve 128M starting from physical address `0x1bf000000` out of the `System RAM` and mark it as `Reserved` so PCIem can use it.

With that exact setup, we'd then load PCIem as follows:

```bash
sudo insmod kernel/pciem.ko pciem_phys_regions="bar0:0x1bf000000:0x10000,bar2:0x1bf100000:0x100000"
```

What this does is, tell PCIem that, out of the reserved memory region, we'll do (In terms of BAR assignation):


```bash
                   memmap=128M$0x1bf000000      
┌────────────┬─────────────────────────────────┐ Start of reserved
│0x1bf000000 │              BAR0               │
│0x1bf010000 │                                 │
└────────────┼─────────────────────────────────┤
      .      │              Free               │
┌────────────┼─────────────────────────────────┤
│0x1bf100000 │                                 │
│            │              BAR2               │
│0x1bf200000 │                                 │
└────────────┼─────────────────────────────────┤
      .      │                                 │
             │                                 │
      .      │                                 │
             │              Free               │
      .      │                                 │
             │                                 │
 0x1c7000000 │                                 │
             └─────────────────────────────────┘ End of reserved
```

#### p2p_regions

The `p2p_regions` argument is a bit more complex; think of it as a whitelist for DMA accesses within PCIem.

The framework supports Peer-to-Peer DMA, but in order to add a little bit of security; one has to manually whitelist the target BAR region of the device we want to P2P from/to.

To know what to "share", you need to obtain the device's desired bar start and end address:

```bash
$ lspci -vvv
...
f147:00:00.0 System peripheral: Red Hat, Inc. Virtio 1.0 file system (rev 01)
        Subsystem: Red Hat, Inc. Device 0040
        Physical Slot: 2113372925
        Control: I/O- Mem+ BusMaster+ SpecCycle- MemWINV- VGASnoop- ParErr- Stepping- SERR- FastB2B- DisINTx+
        Status: Cap+ 66MHz- UDF- FastB2B- ParErr- DEVSEL=fast >TAbort- <TAbort- <MAbort- >SERR- <PERR- INTx-
        Latency: 64
        NUMA node: 0
        Region 0: Memory at e00000000 (64-bit, non-prefetchable) [size=4K]
        Region 2: Memory at e00001000 (64-bit, non-prefetchable) [size=4K]
        Region 4: Memory at c00000000 (64-bit, non-prefetchable) [size=8G]
        Capabilities: <access denied>
        Kernel driver in use: virtio-pci
```

If we were to share BAR0 of this particular device, we'd instruct PCIem as follows:

```bash
sudo insmod kernel/pciem.ko p2p_regions="0xe00000000:0x1000"
```

This will, in turn, give PCIem access to that BAR so PCIe shims can do P2P DMA.

### General functionality

PCIem exposes an interface at `/dev/pciem` which you can freely call into to construct your PCIe shim from within the userspace.

One can see the documented interface on [the API page](user/api.md).