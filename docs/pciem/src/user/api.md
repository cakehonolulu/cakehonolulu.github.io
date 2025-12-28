<meta name="pciem-doc-version" content="0.0.1">

# API

PCIem exposes a userspace-facing API that enables the developer to do PCIe configuration and handling in an easy manner.

One of the main benefits of doing this entirely in userspace, is that it enables you to do iterations on the shim card virtually for free.

Detailed below, are the definitions for the `ioctl` and `struct` PCIem uses to let you configure your shim.

## Structures

### pciem_create_device
```c
enum pciem_mode
{
    /*
        DEPRECATED!

        PCIEM_MODE_INTERNAL = 0,
        PCIEM_MODE_QEMU = 1,
    */
    PCIEM_MODE_USERSPACE = 2,
};

struct pciem_create_device
{
    uint32_t flags;
    uint32_t mode;
};
```

### pciem_bar_config
```c
/*
    DEPRECATED!

    #define PCIEM_BAR_INTERCEPT_NONE 0
    #define PCIEM_BAR_INTERCEPT_ALL 1
    #define PCIEM_BAR_INTERCEPT_WRITE 2
    #define PCIEM_BAR_INTERCEPT_FAULT 3
*/

struct pciem_bar_config
{
    uint32_t bar_index;
    uint32_t flags;
    uint64_t size;
    uint32_t intercept; // DEPRECATED
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

```c
#define PCIEM_IOCTL_CREATE_DEVICE _IOWR(PCIEM_IOCTL_MAGIC, 10, struct pciem_create_device)
```
```c
#define PCIEM_IOCTL_ADD_BAR _IOW(PCIEM_IOCTL_MAGIC, 11, struct pciem_bar_config)
```
```c
#define PCIEM_IOCTL_ADD_CAPABILITY _IOW(PCIEM_IOCTL_MAGIC, 12, struct pciem_cap_config)
```
```c
#define PCIEM_IOCTL_SET_CONFIG _IOW(PCIEM_IOCTL_MAGIC, 13, struct pciem_config_space)
```
```c
#define PCIEM_IOCTL_REGISTER _IO(PCIEM_IOCTL_MAGIC, 14)
```
```c
#define PCIEM_IOCTL_INJECT_IRQ _IOW(PCIEM_IOCTL_MAGIC, 15, struct pciem_irq_inject)
```
```c
#define PCIEM_IOCTL_DMA _IOWR(PCIEM_IOCTL_MAGIC, 16, struct pciem_dma_op)
```
```c
#define PCIEM_IOCTL_DMA_ATOMIC _IOWR(PCIEM_IOCTL_MAGIC, 17, struct pciem_dma_atomic)
```
```c
#define PCIEM_IOCTL_P2P _IOWR(PCIEM_IOCTL_MAGIC, 18, struct pciem_p2p_op_user)
```
```c
#define PCIEM_IOCTL_GET_BAR_INFO _IOWR(PCIEM_IOCTL_MAGIC, 19, struct pciem_bar_info_query)
```
```c
#define PCIEM_IOCTL_SET_WATCHPOINT _IOW(PCIEM_IOCTL_MAGIC, 20, struct pciem_watchpoint_config)
```
```c
#define PCIEM_IOCTL_SET_EVENTFD _IOW(PCIEM_IOCTL_MAGIC, 21, struct pciem_eventfd_config)
```
