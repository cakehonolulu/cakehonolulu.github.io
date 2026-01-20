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

The userspace program creates the PCIe device, establishes the event channel, and handles MMIO operations.

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
#include <sys/eventfd.h>
#include <unistd.h>
#include <stdatomic.h>
#include <poll.h>

#include "pciem_userspace.h"

/* Defines for the BAR0 register offsets */
#define REG_CONTROL  0x00
#define REG_STATUS   0x04
#define REG_COUNTER  0x08

#define STATUS_IRQ_PENDING (1 << 0)

/* DummyClockPCIe state */
struct counter_device {
    int fd;
    int instance_fd;
    uint32_t counter;
    uint32_t status;
    struct pciem_shared_ring *ring;
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

This opens the PCIem control device. All configuration happens on this file descriptor.

#### 2. Creating the Device

```c
struct pciem_create_device create = {0};
ret = ioctl(fd, PCIEM_IOCTL_CREATE_DEVICE, &create);
if (ret < 0) {
    perror("Failed to create device");
    return 1;
}
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

This creates a 4KB memory BAR at index 0.

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

ret = ioctl(fd, PCIEM_IOCTL_SET_WATCHPOINT, &wp);
if (ret < 0) {
    perror("Failed to set watchpoint");
}

```

**Watchpoint flags:**

-- `PCIEM_WP_FLAG_BAR_KPROBES`: PCIem automatically locates the BAR mapping (recommended).
-- `PCIEM_WP_FLAG_BAR_MANUAL`: You provide the virtual address manually (advanced usage).

**Note:** Watchpoints use hardware debug registers, so you can only have a limited number active (Don't assume there's loads...).

#### 7. Registering the Device

```c
ret = ioctl(fd, PCIEM_IOCTL_REGISTER, 0);
if (ret < 0) {
    perror("Failed to register device");
    return 1;
}
printf("Device registered! Instance FD: %d\n", ret);
```

This makes the device visible to the kernel. It returns a new `instance_fd` which represents the synthetic device on the bus.

#### 8. Setting up the Event Ring

To receive events efficiently, we map a shared atomic ring buffer and set up an `eventfd` for notifications. This avoids busy polling.

```c
int efd = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
struct pciem_eventfd_config efd_cfg = { .eventfd = efd };

if (ioctl(fd, PCIEM_IOCTL_SET_EVENTFD, &efd_cfg) < 0) {
    perror("Failed to set eventfd");
    return 1;
}

struct pciem_shared_ring *ring = mmap(NULL, sizeof(struct pciem_shared_ring),
                                      PROT_READ | PROT_WRITE, MAP_SHARED,
                                      fd, 0);
uint32_t head = atomic_load(&ring->head);

struct pciem_bar_info_query bar0_info = { .bar_index = 0 };
ioctl(fd, PCIEM_IOCTL_GET_BAR_INFO, &bar0_info);

volatile uint32_t *bar0 = mmap(NULL, bar0_info.size,
                               PROT_READ | PROT_WRITE,
                               MAP_SHARED, instance_fd, 0);
```

#### 9. The Event Loop

Now we enter the main loop. If the ring is empty, we `poll()` on the `eventfd` to sleep until the kernel wakes us up.

```c
struct pollfd pfd = {
    .fd = efd,
    .events = POLLIN
};

struct counter_device dev = { .fd = fd, .counter = 0 };

while (1) {
    uint32_t tail = atomic_load(&ring->tail);

    if (head == tail) {
        if (poll(&pfd, 1, -1) > 0) {
            uint64_t count;
            read(efd, &count, sizeof(count));
        }
        continue;
    }

    while (head != tail) {
        atomic_thread_fence(memory_order_acquire);

        struct pciem_event *evt = &ring->events[head];

        switch (evt->type) {
            case PCIEM_EVENT_MMIO_WRITE:
                handle_mmio_write(fd, evt, &dev, bar0);
                break;

            case PCIEM_EVENT_MMIO_READ:
                printf("Driver read offset 0x%lx\n", evt->offset);
                break;
        }

        head = (head + 1) % PCIEM_RING_SIZE;
        atomic_store(&ring->head, head);
    }
}
```

#### 10. Processing Events

Since PCIem uses a shared memory model, you **do not** send a response to the kernel for events.

* **For Reads:** The driver reads directly from the BAR memory you mapped.
* **For Writes:** The driver writes to memory and posts a notification event. You update your internal state and the BAR memory immediately.

```c
static void handle_mmio_write(int fd, struct pciem_event *evt,
                              struct counter_device *dev,
                              volatile uint32_t *bar0)
{
    if (evt->bar == 0 && evt->offset == REG_CONTROL) {
        if (evt->data & 1) {
            dev->counter++;

            bar0[REG_COUNTER / 4] = dev->counter;

            if (dev->counter % 10 == 0) {
                struct pciem_irq_inject irq = { .vector = 0 };
                ioctl(fd, PCIEM_IOCTL_INJECT_IRQ, &irq);
            }
        }
    }
}
```

#### 11. Injecting Interrupts

As shown in the handler above, when you want to signal the driver asynchronously (like when the counter reaches a threshold), you use the IRQ injection IOCTL:

```c
struct pciem_irq_inject irq = { .vector = 0 };
ioctl(fd, PCIEM_IOCTL_INJECT_IRQ, &irq);
```