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

## PCIem parameters

### pciem_phys_region module argument

Let's start with the preface that, we're obviously going to use `insmod` to load `pciem.ko`, but the way we do it changes the behaviour of the framework.

Starting from PCIem 0.1, one can specify kernel module arguments to alter/instruct certain logic on the code.

`pciem_phys_region`: This basically specifies what physically-contiguous memory region is reserved and free to use by PCIem.

#### Reserving memory with memmap command line argument

This is attained by passing the `memmap=` argument to Linux's `cmdline`.

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
sudo insmod kernel/pciem.ko pciem_phys_region="0x1bf000000:0x8000000"
```

What this does is, tell PCIem that it basically has 128MBs to play starting from physical ```0x1bf000000```:

> **Note:** On some AArch64/riscv platforms (such as the Raspberry Pi 4B or VisionFive 2), `memmap=` may not be honoured by the bootloader or may not be available at all. In those cases, the preferred alternative is to reserve memory via a [Device Tree overlay](#reserving-memory-with-a-custom-device-tree-overlay) instead. If platform doesn't have `dtoverlay` access/support in an easy way, [an alternate method is possible](#reserving-memory-with-fully-replaced-device-tree).

#### Reserving memory with a custom device tree overlay

Create a file named `reserve-mem.dts` with the following contents, adjusting the base address and size to match your desired reservation:

##### reserved-memory node

```dts
/dts-v1/;
/plugin/;
/ {
    compatible = "brcm,bcm2711";
    fragment@0 {
        target-path = "/";
        __overlay__ {
            #address-cells = <2>;
            #size-cells = <1>;
            reserved-memory {
                #address-cells = <2>;
                #size-cells = <1>;
                ranges;
                pciem_reservation@50000000 {
                    reg = <0x0 0x50000000 0x10000000>;
                    no-map;
                    status = "okay";
                };
            };
        };
    };
};
```

In this example, `0x50000000` is the base address and `0x10000000` is the size (256MB). Adjust these to fit your target platform's memory layout.

Compile the overlay and install it:

```bash
dtc -@ -I dts -O dtb -o reserve-mem.dtbo reserve-mem.dts
sudo cp reserve-mem.dtbo /boot/firmware/overlays/
```

Then enable it by appending the following line to `/boot/firmware/config.txt`:

```
dtoverlay=reserve-mem
```

> **Note:** For RPi 4B (Or similar) boards you should add the line within the `[all]` node.

Reboot for the reservation to take effect. You can verify it was applied by checking:

```bash
cat /proc/iomem | grep -i reserved
```

Once confirmed, load PCIem pointing at the same region specified in the overlay:

```bash
sudo insmod kernel/pciem.ko pciem_phys_region="0x50000000:0x10000000"
```

> **Note:** The method written above has been tested on a Raspberry Pi 4B with the stock Raspbian distribution and a VisionFive 2 running Debian sid (64-bit version). Some aarch64/riscv kernels/boards may be fine with `memmap=` or even `mem=` (Even though the latest hasn't been tested) but it's best to try and decide which one works.

#### Reserving memory with fully replaced device tree

If the platform doesn't have `dtoverlay` support you can, instead, dump the device-tree from the live-running system and include/modify the [reserved-memory](#reserved-memory-node) node on it.

There's a bunch of ways of having the firmware load a prebuilt device-tree instead of the default (Probably built-in) one.

This is left up as an exercise for the reader as it varies wildly from device to device; but for the VisionFive 2, what worked is:

* Assuming your device is using `GRUB` as bootloader you can modify your menuentry to point to the modified `dtb` file, which is placed alongside the `vmlinuz-*`, `initrd-*` files so that it can locate it. Then just add below everything on the menuentry: `devicetree /path/to/modified.dtb` and that'll do it.

### p2p_regions

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

## General functionality

PCIem exposes an interface at `/dev/pciem` which you can freely call into to construct your PCIe shim from within the userspace.

One can see the documented interface on [the API page](user/api.md).