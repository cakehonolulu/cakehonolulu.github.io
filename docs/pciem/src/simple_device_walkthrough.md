# Dummy Device Walkthrough

This walkthrough demonstrates how to create a minimal PCIe device using PCIem.

We'll build a simple "clock/counting device" with basic MMIO registers and MSI interrupt support.

## The dummy PCIe

Our dummy PCIe has:
- **One BAR** (BAR0, 4KB) with three 32-bit registers:
  - `REG_CONTROL` (0x00): Write 1 to increment counter
  - `REG_STATUS` (0x04): Status flags (IRQ pending bit)
  - `REG_COUNTER` (0x08): Current counter value (read-only)
- **MSI**: One interrupt vector
- **Interrupts**: Every 10 counts, an MSI is fired

## Prerequisites

Before starting, make sure you have:
1. PCIem kernel module loaded (see [Getting Started](getting_started.md))
2. A C compiler and kernel headers installed
3. Basic understanding of PCIe concepts (BARs, config space, interrupts)

## The Code

### Userspace Device Emulator

The userspace program creates the PCIe device and handles MMIO operations:

```c
/*
 * DummyClockPCIe userspace shim
 */

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>

#include "pciem_userspace.h"

/* Defines for the BAR0 register offsets */
#define REG_CONTROL  0x00
#define REG_STATUS   0x04
#define REG_COUNTER  0x08

#define STATUS_IRQ_PENDING (1 << 0)

/* DummyClockPCIe state */
struct counter_device {
    int fd;
    uint32_t counter;
    uint32_t status;
};
```

#### 1. Opening the PCIem Device

```c
fd = open("/dev/pciem", O_RDWR);
if (fd < 0) {
    perror("Failed to open /dev/pciem");
    return 1;
}
```

This opens the PCIem control device. All subsequent operations use this file descriptor.

#### 2. Creating the Device

```c
struct pciem_create_device create = {0};
ret = ioctl(fd, PCIEM_IOCTL_CREATE_DEVICE, &create);
```

This tells PCIem we're starting to configure a new virtual PCIe device.

#### 3. Adding BAR0

```c
struct pciem_bar_config bar = {
    .bar_index = 0,
    .size = 4096,
    .flags = PCI_BASE_ADDRESS_SPACE_MEMORY |
             PCI_BASE_ADDRESS_MEM_TYPE_32,
};
ret = ioctl(fd, PCIEM_IOCTL_ADD_BAR, &bar);
```

This creates a 4KB memory BAR at index 0. The flags specify:
- `PCI_BASE_ADDRESS_SPACE_MEMORY`: This is a memory BAR (not I/O)
- `PCI_BASE_ADDRESS_MEM_TYPE_32`: 32-bit addressable

#### 4. Adding MSI Capability

```c
struct pciem_cap_msi_userspace msi = {
    .num_vectors_log2 = 0,  /* 2^0 = 1 vector */
    .has_64bit = 1,
    .has_masking = 0,
};
struct pciem_cap_config cap = {
    .cap_type = PCIEM_CAP_MSI,
    .cap_size = sizeof(msi),
};
memcpy(cap.cap_data, &msi, sizeof(msi));

ret = ioctl(fd, PCIEM_IOCTL_ADD_CAPABILITY, &cap);
```

#### 5. Setting Config Space

```c
struct pciem_config_space cfg = {
    .vendor_id = 0x1234,
    .device_id = 0x5678,
    .subsys_vendor_id = 0x1234,
    .subsys_device_id = 0x5678,
    .revision = 0x01,
    .class_code = {0x00, 0x00, 0xFF},
    .header_type = 0x00,
};
ret = ioctl(fd, PCIEM_IOCTL_SET_CONFIG, &cfg);
```

This sets how the device identifies itself, one part important later is:
- **Vendor/Device ID pair**: Used by the kernel to look for drivers


#### 6. Setting Up Watchpoints

Watchpoints allow you to get immediate hardware-level notifications when the driver accesses specific registers:

```c
struct pciem_watchpoint_config wp = {
    .bar_index = 0,
    .offset = REG_CONTROL,  /* 0x00                         */
    .width = 4,             /* 4 bytes (32-bit register)    */
    .flags = PCIEM_WP_FLAG_BAR_KPROBES,
};

int ret = ioctl(dev.fd, PCIEM_IOCTL_SET_WATCHPOINT, &wp);
if (ret < 0) {
    perror("Failed to set watchpoint");
}
```

**Watchpoint flags:**
- `PCIEM_WP_FLAG_BAR_KPROBES`: PCIem automatically locates the BAR mapping (recommended)
- `PCIEM_WP_FLAG_BAR_MANUAL`: You develop your own heuristic (Or if the driver stores the BAR address somewhere on it's internal private driver data structure, you can query it in a hacky way using some offset magic)

**Note:** Watchpoints use hardware debug registers, so you can only have a limited number active (Don't assume there's loads...).

#### 7. Registering the Device

```c
ret = ioctl(fd, PCIEM_IOCTL_REGISTER, 0);
```

This is the moment your device shim becomes visible to the kernel and the local PCIe bus.

It's worth mentioning that every PCI shim has it's own private `fd` you can interact with (To map BARs the shim can alter and whatnot, think fault-injection and similar).

#### 8. Handling Events

Once registered, the kernel will send events when a driver accesses your card:

```c
static void handle_mmio_read(struct counter_device *dev, struct pciem_event *evt)
{
    struct pciem_response resp = {
        .seq = evt->seq,
        .status = 0,
    };

    switch (evt->offset) {
    case REG_COUNTER:
        resp.data = dev->counter;
        break;
    default:
        printf("Unimplemented read offset!: %d\n", evt->offset);
        /* You would gracefully exit here by calling the dtors and whatnot, but for brevity */
        exit(1);
    }

    write(dev->fd, &resp, sizeof(resp));
}
```

#### 9. Injecting Interrupts

When you want to signal the driver:

```c
struct pciem_irq_inject irq = { .vector = 0 };
ioctl(fd, PCIEM_IOCTL_INJECT_IRQ, &irq);
```

This triggers an MSI interrupt. In our DummyClockPCIe example, we fire one every 10 counter increments.

### Kernel Driver

The driver is a standard PCIe driver, it's basically unaware that PCIem exists at all.

```c
static int dummyclockpcie_probe(struct pci_dev *pdev, const struct pci_device_id *id)
{
    ...

    ret = pci_enable_device(pdev);
    
    /* We map BAR0 */
    bar0 = pci_iomap(pdev, 0, 0);
    
    /* We enable MSIs */
    ret = pci_enable_msi(pdev);
}
```

Then, this, would for instance, generate events:

```c
    iowrite32(1, bar0 + REG_CONTROL);
    val = ioread32(bar0 + REG_COUNTER);
```

Anything that accesses the watchpoint will trigger events that your shim will be able to consume and respond accordingly.

When the driver does `iowrite32()` or `ioread32()`, PCIem intercepts it and adds the event to it's per-device ring-buffer that you can manually poll or use the `eventfd` API enabled to not busywait.

### Eventfd

Instead of busy-polling the device for events, you can use Linux's `eventfd` mechanism for efficient notification, support is baked in on the `pciem_userspace` module of the framework:

```c
setup_eventfd(struct counter_device *dev)
{
    struct pciem_eventfd_config efd_cfg;
    
    ...
    
    event_fd = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);

    if (dev->event_fd < 0)
    {
        perror("Failed to create eventfd");
        ...
    }

    efd_cfg.eventfd = dev->event_fd;
    efd_cfg.reserved = 0;
    
    if (ioctl(dev->fd, PCIEM_IOCTL_SET_EVENTFD, &efd_cfg) < 0)
    {
        perror("Failed to set eventfd");
        close(dev->event_fd);
        dev->event_fd = -1;
        ...
    }

    ...
}
```
