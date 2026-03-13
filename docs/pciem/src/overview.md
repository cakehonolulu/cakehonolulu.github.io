# Overview

PCIem is a Linux framework that enables software developers to write PCIe card drivers on the host to target unexisting PCIe cards on the bus.

This helps model a driver if the developers don't have a physical PCIe card to test it on, effectively enabling pre-silicon engineering on the
software side of things for the prototype card.

Initially, PCIem was thought after enabling communications from/to a QEMU instance; but has ever since been evolving to support a wide variety
of use-cases.

You can think of the framework as a MITM (Man-in-the-Middle) that sits between the untouched, production drivers (Which are, unaware of PCIem's
existence) and the Linux kernel.

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
graph TB
    subgraph Kernel ["Host Linux Kernel"]
        direction TB
        RealDriver["Real PCIe Driver"]
        subgraph Framework ["PCIem Framework"]
            direction TB
            Config["PCI Config Space"]
            BARs["BARs"]
            IRQ["Interrupts"]
            DMA["DMA / IOMMU"]
        end
    end
    Interface(("/dev/pciem"))
    subgraph User ["Linux Userspace"]
        direction TB
        Shim["Device Emulation"]
    end
    Framework <==> Interface
    Interface <==> Shim
```