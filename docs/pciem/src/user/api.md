<meta name="pciem-doc-version" content="0.2">

# API

PCIem exposes a userspace-facing API that enables the developer to do PCIe configuration and handling in an easy manner.

One of the main benefits of doing this entirely in userspace, is that it enables you to do iterations on the shim card virtually for free.

Detailed below, are the definitions for the `ioctl` and `struct` PCIem uses to let you configure your shim.

## Structures

### pciem_create_device
```c
struct pciem_create_device
{
    uint32_t flags;
    uint32_t mode;
};
```

### pciem_bar_config
```c
struct pciem_bar_config
{
    uint32_t bar_index;
    uint32_t flags;
    uint64_t size;
    uint32_t reserved;
};
```

### pciem_cap_config
```c
struct pciem_cap_config
{
    uint32_t cap_type;
    uint32_t cap_size;
    uint8_t cap_data[256];
};
```

### pciem_cap_msi_userspace
```c
struct pciem_cap_msi_userspace
{
    uint8_t num_vectors_log2;
    uint8_t has_64bit;
    uint8_t has_masking;
    uint8_t reserved;
};
```

### pciem_cap_msix_userspace
```c
struct pciem_cap_msix_userspace
{
    uint8_t bar_index;
    uint8_t reserved[3];
    uint32_t table_offset;
    uint32_t pba_offset;
    uint16_t table_size;
    uint16_t reserved2;
};
```

### pciem_config_space
```c
struct pciem_config_space
{
    uint16_t vendor_id;
    uint16_t device_id;
    uint16_t subsys_vendor_id;
    uint16_t subsys_device_id;
    uint8_t revision;
    uint8_t class_code[3];
    uint8_t header_type;
    uint8_t reserved[7];
};
```

### pciem_event
```c
#define PCIEM_EVENT_MMIO_READ 1
#define PCIEM_EVENT_MMIO_WRITE 2
#define PCIEM_EVENT_CONFIG_READ 3
#define PCIEM_EVENT_CONFIG_WRITE 4
#define PCIEM_EVENT_MSI_ACK 5
#define PCIEM_EVENT_RESET 6

struct pciem_event
{
    uint64_t seq;
    uint32_t type;
    uint32_t bar;
    uint64_t offset;
    uint32_t size;
    uint32_t reserved;
    uint64_t data;
    uint64_t timestamp;
};
```

### pciem_response
```c
struct pciem_response
{
    uint64_t seq;
    uint64_t data;
    int32_t status;
    uint32_t reserved;
};
```

### pciem_irq_inject
```c
struct pciem_irq_inject
{
    uint32_t vector;
    uint32_t reserved;
};
```

### pciem_dma_op
```c
#define PCIEM_DMA_FLAG_READ 0x1
#define PCIEM_DMA_FLAG_WRITE 0x2

struct pciem_dma_op
{
    uint64_t guest_iova;
    uint64_t user_addr;
    uint32_t length;
    uint32_t pasid;
    uint32_t flags;
    uint32_t reserved;
};
```

### pciem_dma_atomic
```c
#define PCIEM_ATOMIC_FETCH_ADD 1
#define PCIEM_ATOMIC_FETCH_SUB 2
#define PCIEM_ATOMIC_SWAP 3
#define PCIEM_ATOMIC_CAS 4
#define PCIEM_ATOMIC_FETCH_AND 5
#define PCIEM_ATOMIC_FETCH_OR 6
#define PCIEM_ATOMIC_FETCH_XOR 7

struct pciem_dma_atomic
{
    uint64_t guest_iova;
    uint64_t operand;
    uint64_t compare;
    uint32_t op_type;
    uint32_t pasid;
    uint64_t result;
};
```

### pciem_p2p_op_user
```c
struct pciem_p2p_op_user
{
    uint64_t target_phys_addr;
    uint64_t user_addr;
    uint32_t length;
    uint32_t flags;
};
```

### pciem_bar_info_query
```c
struct pciem_bar_info_query
{
    uint32_t bar_index;
    uint64_t phys_addr;
    uint64_t size;
    uint32_t flags;
};
```

### pciem_watchpoint_config
```c
#define PCIEM_WP_FLAG_BAR_KPROBES  (1 << 0)
#define PCIEM_WP_FLAG_BAR_MANUAL   (1 << 1)

struct pciem_watchpoint_config
{
    uint32_t bar_index;
    uint32_t offset;
    uint32_t width;
    uint32_t flags;
};
```

### pciem_eventfd_config
```c
struct pciem_eventfd_config
{
    int32_t eventfd;
    uint32_t reserved;
};
```

## IOCTLs

```c
#define PCIEM_IOCTL_MAGIC 0xAF
```

### `create_device()`

```c
#define PCIEM_IOCTL_CREATE_DEVICE _IOWR(PCIEM_IOCTL_MAGIC, 10, struct pciem_create_device)
```

This is the first `ioctl` you should issue. Assuming you've already done an `open()` on `/dev/pciem`, you can issue `create_device` to
notify PCIem a new PCIe shim is being crafted from userspace.

It takes the [pciem_create_device](#pciem_create_device) `struct` as param, but you can basically send a zero-filled one and it'll work.

### `add_bar()`

```c
#define PCIEM_IOCTL_ADD_BAR _IOW(PCIEM_IOCTL_MAGIC, 11, struct pciem_bar_config)
```

Whenever you want to add `BAR` definitions, you should issue this `ioctl`.

It takes the [pciem_bar_config](#pciem_bar_config) `struct` as param and you can initializate it in a myriad of ways, but the main fields you need to properly fill are:

`bar_index`: Basically, which is the BAR number it'll represent within PCIem

`size`: Which size this BAR will occupy

`flags`: What PCI flags this BAR will hold (Ex. `PCI_BASE_ADDRESS_SPACE_MEMORY`, `PCI_BASE_ADDRESS_MEM_PREFETCH`, `PCI_BASE_ADDRESS_MEM_TYPE_64`...).

Issue `add_bar` when you are ready to push a new BAR to your PCIem shim device `fd`.

### `add_capability()`

```c
#define PCIEM_IOCTL_ADD_CAPABILITY _IOW(PCIEM_IOCTL_MAGIC, 12, struct pciem_cap_config)
```

Use this `ioctl` to add PCIe capabilities to your shim device.

It takes the [pciem_cap_config](#pciem_cap_config) `struct` as param. The main fields you'll care about are:

`cap_type`: What type of capability you're adding (Ex. `PCIEM_CAP_MSI`, `PCIEM_CAP_MSIX`, `PCIEM_CAP_PCIE`...)

`cap_size`: How many bytes of `cap_data` you're providing

`cap_data`: The actual capability data itself. For MSI/MSI-X, you'd typically fill this with [pciem_cap_msi_userspace](#pciem_cap_msi_userspace) or [pciem_cap_msix_userspace](#pciem_cap_msix_userspace) structs.

### `set_config()`

```c
#define PCIEM_IOCTL_SET_CONFIG _IOW(PCIEM_IOCTL_MAGIC, 13, struct pciem_config_space)
```

Sets the PCI configuration space for your device.

This is where you define how your device identifies itself to the system.

It takes the [pciem_config_space](#pciem_config_space) `struct` as param.

You'll want to set:

`vendor_id`: Your vendor ID

`device_id`: The device ID

`class_code`: 3-byte PCI class code that tells the system what type of device this is

Issue this after you've added all your BARs and capabilities, but before calling `register()`.

### `register()`

```c
#define PCIEM_IOCTL_REGISTER _IO(PCIEM_IOCTL_MAGIC, 14)
```

This is the final step in setting up your PCIem device.

Once you call `register()`, your device configuration is locked and the device becomes visible to the system.

Returns an instance file descriptor that you can use to `mmap()` your BARs into userspace for direct access.

### `inject_irq()`

```c
#define PCIEM_IOCTL_INJECT_IRQ _IOW(PCIEM_IOCTL_MAGIC, 15, struct pciem_irq_inject)
```

Issue this to inject an interrupt (After your shim completes some work, for instance).

It takes the [pciem_irq_inject](#pciem_irq_inject) `struct` as param:

`vector`: Which MSI/MSI-X vector to fire. If you've got MSI configured for 4 vectors, valid values are 0-3.

### `dma()`

```c
#define PCIEM_IOCTL_DMA _IOWR(PCIEM_IOCTL_MAGIC, 16, struct pciem_dma_op)
```

This lets you read from or write to guest physical addresses.

It takes the [pciem_dma_op](#pciem_dma_op) `struct` as param:

`guest_iova`: The guest physical address you want to access

`user_addr`: Your userspace buffer address

`length`: How many bytes to transfer

`flags`: Either `PCIEM_DMA_FLAG_READ` or `PCIEM_DMA_FLAG_WRITE`

This is IOMMU-aware so, in case your system has one; the translations get handled by PCIem.

### `dma_atomic()`

```c
#define PCIEM_IOCTL_DMA_ATOMIC _IOWR(PCIEM_IOCTL_MAGIC, 17, struct pciem_dma_atomic)
```

It takes the [pciem_dma_atomic](#pciem_dma_atomic) `struct` as param:

`guest_iova`: Target address in guest memory

`op_type`: What atomic operation (Ex. `PCIEM_ATOMIC_CAS`, `PCIEM_ATOMIC_FETCH_ADD`...)

`operand`: The value to use for the operation

`result`: Where the previous value gets returned

Useful if you're building something that needs lock-free synchronization with the guest since it implements what's needed to do atomic operations on guest memory.

### `p2p()`

```c
#define PCIEM_IOCTL_P2P _IOWR(PCIEM_IOCTL_MAGIC, 18, struct pciem_p2p_op_user)
```

Peer-to-peer DMA between PCIe devices. Your PCIem device can directly access another physical device's memory space.

It takes the [pciem_p2p_op_user](#pciem_p2p_op_user) `struct` as param:

`target_phys_addr`: Physical address of the target device (Another device's BAR, see the p2p_regions module argument!)

`user_addr`: Your buffer in userspace

`length`: How many bytes to transfer

`flags`: Similar to regular DMA flags

### `get_bar_info()`

```c
#define PCIEM_IOCTL_GET_BAR_INFO _IOWR(PCIEM_IOCTL_MAGIC, 19, struct pciem_bar_info_query)
```

Call this after `register()` if you need to know the actual physical addresses.

It takes the [pciem_bar_info_query](#pciem_bar_info_query) `struct` as param. Set the `bar_index` going in, and it'll fill in:

`phys_addr`: The physical address where this BAR lives

`size`: The BAR size

`flags`: The BAR flags

### `set_watchpoint()`

```c
#define PCIEM_IOCTL_SET_WATCHPOINT _IOW(PCIEM_IOCTL_MAGIC, 20, struct pciem_watchpoint_config)
```

Sets up hardware watchpoints on specific BAR offsets. When the guest writes to these locations, you'll get notified immediately via the event mechanism (Or your hand-rolled one, if you have done it).

It takes the [pciem_watchpoint_config](#pciem_watchpoint_config) `struct` as param:

`bar_index`: Which BAR to watch

`offset`: Offset within the BAR

`width`: How many bytes (1, 2, 4, or 8)

`flags`: Either `PCIEM_WP_FLAG_BAR_KPROBES` or `PCIEM_WP_FLAG_BAR_MANUAL` to control how PCIem locates the BAR mapping.

### `set_eventfd()`

```c
#define PCIEM_IOCTL_SET_EVENTFD _IOW(PCIEM_IOCTL_MAGIC, 21, struct pciem_eventfd_config)
```

This sets up a userspace `eventfd` which gets notified whenever events arrive from PCIem.

It takes the [pciem_eventfd_config](#pciem_eventfd_config) `struct` as param:

`eventfd`: Your eventfd file descriptor

Once set up, the kernel will signal your eventfd whenever new events land in the ring buffer.