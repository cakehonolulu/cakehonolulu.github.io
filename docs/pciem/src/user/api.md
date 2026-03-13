<meta name="pciem-doc-version" content="dev">

# API Reference

This page is **auto-generated** from the PCIem kernel headers. Do not edit it by hand — run `make docs` to regenerate.

PCIem exposes a userspace-facing API through `/dev/pciem` that lets developers configure and emulate PCIe devices entirely from userspace.

## Contents

- [Constants](#constants)
- [IOCTLs](#ioctls)
  - [`PCIEM_IOCTL_CREATE_DEVICE`](#ioctl-pciem-ioctl-create-device)
  - [`PCIEM_IOCTL_ADD_BAR`](#ioctl-pciem-ioctl-add-bar)
  - [`PCIEM_IOCTL_ADD_CAPABILITY`](#ioctl-pciem-ioctl-add-capability)
  - [`PCIEM_IOCTL_SET_CONFIG`](#ioctl-pciem-ioctl-set-config)
  - [`PCIEM_IOCTL_REGISTER`](#ioctl-pciem-ioctl-register)
  - [`PCIEM_IOCTL_INJECT_IRQ`](#ioctl-pciem-ioctl-inject-irq)
  - [`PCIEM_IOCTL_DMA`](#ioctl-pciem-ioctl-dma)
  - [`PCIEM_IOCTL_DMA_ATOMIC`](#ioctl-pciem-ioctl-dma-atomic)
  - [`PCIEM_IOCTL_P2P`](#ioctl-pciem-ioctl-p2p)
  - [`PCIEM_IOCTL_GET_BAR_INFO`](#ioctl-pciem-ioctl-get-bar-info)
  - [`PCIEM_IOCTL_SET_EVENTFD`](#ioctl-pciem-ioctl-set-eventfd)
  - [`PCIEM_IOCTL_SET_IRQFD`](#ioctl-pciem-ioctl-set-irqfd)
  - [`PCIEM_IOCTL_DMA_INDIRECT`](#ioctl-pciem-ioctl-dma-indirect)
  - [`PCIEM_IOCTL_TRACE_BAR`](#ioctl-pciem-ioctl-trace-bar)
  - [`PCIEM_IOCTL_START`](#ioctl-pciem-ioctl-start)

## Constants

### `PCIEM_CAP_*`

| Name | Value | Description |
|------|-------|-------------|
| `PCIEM_CAP_MSI` | `0` |  |
| `PCIEM_CAP_MSIX` | `1` |  |
| `PCIEM_CAP_PASID` | `5` |  |
| `PCIEM_CAP_PCIE` | `3` |  |
| `PCIEM_CAP_PM` | `2` |  |
| `PCIEM_CAP_VSEC` | `4` |  |

### `PCIEM_EVENT_*`

| Name | Value | Description |
|------|-------|-------------|
| `PCIEM_EVENT_CONFIG_READ` | `3` |  |
| `PCIEM_EVENT_CONFIG_WRITE` | `4` |  |
| `PCIEM_EVENT_MMIO_READ` | `1` |  |
| `PCIEM_EVENT_MMIO_WRITE` | `2` |  |
| `PCIEM_EVENT_MSI_ACK` | `5` |  |
| `PCIEM_EVENT_RESET` | `6` |  |

### `PCIEM_TRACE_*`

| Name | Value | Description |
|------|-------|-------------|
| `PCIEM_TRACE_READS` | `(1 << 0)` |  |
| `PCIEM_TRACE_STOP_WRITES` | `(1 << 2)` |  |
| `PCIEM_TRACE_WRITES` | `(1 << 1)` |  |

### `PCIEM_ATOMIC_*`

| Name | Value | Description |
|------|-------|-------------|
| `PCIEM_ATOMIC_CAS` | `4` |  |
| `PCIEM_ATOMIC_FETCH_ADD` | `1` |  |
| `PCIEM_ATOMIC_FETCH_AND` | `5` |  |
| `PCIEM_ATOMIC_FETCH_OR` | `6` |  |
| `PCIEM_ATOMIC_FETCH_SUB` | `2` |  |
| `PCIEM_ATOMIC_FETCH_XOR` | `7` |  |
| `PCIEM_ATOMIC_SWAP` | `3` |  |

### `PCIEM_DMA_FLAG_*`

| Name | Value | Description |
|------|-------|-------------|
| `PCIEM_DMA_FLAG_READ` | `0x1` |  |
| `PCIEM_DMA_FLAG_WRITE` | `0x2` |  |

### `PCIEM_IRQFD_FLAG_*`

| Name | Value | Description |
|------|-------|-------------|
| `PCIEM_IRQFD_FLAG_DEASSERT` | `(1 << 1)` |  |
| `PCIEM_IRQFD_FLAG_LEVEL` | `(1 << 0)` |  |

### `PCIEM_WP_FLAG_BAR_*`

| Name | Value | Description |
|------|-------|-------------|
| `PCIEM_WP_FLAG_BAR_KPROBES` | `(1 << 0)` |  |
| `PCIEM_WP_FLAG_BAR_MANUAL` | `(1 << 1)` |  |

### `PCIEM_CREATE_FLAG_BUS_MODE_*`

| Name | Value | Description |
|------|-------|-------------|
| `PCIEM_CREATE_FLAG_BUS_MODE_ATTACH` | `0x00000001` |  |
| `PCIEM_CREATE_FLAG_BUS_MODE_MASK` | `0x00000003` |  |
| `PCIEM_CREATE_FLAG_BUS_MODE_VIRTUAL` | `0x00000000` |  |

### Miscellaneous

| Name | Value | Description |
|------|-------|-------------|
| `PCIEM_MAX_IRQFDS` | `32` |  |
| `PCIEM_RING_SIZE` | `256` |  |

## IOCTLs

> All ioctls are issued on the `/dev/pciem` file descriptor unless noted otherwise.

### `PCIEM_IOCTL_CREATE_DEVICE` {#ioctl-pciem-ioctl-create-device}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_CREATE_DEVICE _IOWR(PCIEM_IOCTL_MAGIC, 10, struct pciem_create_device)
```

**Direction:** read/write (both directions)

**Parameter struct:** `pciem_create_device`

### `PCIEM_IOCTL_ADD_BAR` {#ioctl-pciem-ioctl-add-bar}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_ADD_BAR _IOW(PCIEM_IOCTL_MAGIC, 11, struct pciem_bar_config)
```

**Direction:** write (userspace → kernel)

**Parameter struct:** `pciem_bar_config`

### `PCIEM_IOCTL_ADD_CAPABILITY` {#ioctl-pciem-ioctl-add-capability}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_ADD_CAPABILITY _IOW(PCIEM_IOCTL_MAGIC, 12, struct pciem_cap_config)
```

**Direction:** write (userspace → kernel)

**Parameter struct:** `pciem_cap_config`

### `PCIEM_IOCTL_SET_CONFIG` {#ioctl-pciem-ioctl-set-config}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_SET_CONFIG _IOW(PCIEM_IOCTL_MAGIC, 13, struct pciem_config_space)
```

**Direction:** write (userspace → kernel)

**Parameter struct:** `pciem_config_space`

### `PCIEM_IOCTL_REGISTER` {#ioctl-pciem-ioctl-register}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_REGISTER _IO(PCIEM_IOCTL_MAGIC, 14)
```

**Direction:** none (no data transfer)

### `PCIEM_IOCTL_INJECT_IRQ` {#ioctl-pciem-ioctl-inject-irq}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_INJECT_IRQ _IOW(PCIEM_IOCTL_MAGIC, 15, struct pciem_irq_inject)
```

**Direction:** write (userspace → kernel)

**Parameter struct:** `pciem_irq_inject`

### `PCIEM_IOCTL_DMA` {#ioctl-pciem-ioctl-dma}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_DMA _IOWR(PCIEM_IOCTL_MAGIC, 16, struct pciem_dma_op)
```

**Direction:** read/write (both directions)

**Parameter struct:** `pciem_dma_op`

### `PCIEM_IOCTL_DMA_ATOMIC` {#ioctl-pciem-ioctl-dma-atomic}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_DMA_ATOMIC _IOWR(PCIEM_IOCTL_MAGIC, 17, struct pciem_dma_atomic)
```

**Direction:** read/write (both directions)

**Parameter struct:** `pciem_dma_atomic`

### `PCIEM_IOCTL_P2P` {#ioctl-pciem-ioctl-p2p}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_P2P _IOWR(PCIEM_IOCTL_MAGIC, 18, struct pciem_p2p_op_user)
```

**Direction:** read/write (both directions)

**Parameter struct:** `pciem_p2p_op_user`

### `PCIEM_IOCTL_GET_BAR_INFO` {#ioctl-pciem-ioctl-get-bar-info}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_GET_BAR_INFO _IOWR(PCIEM_IOCTL_MAGIC, 19, struct pciem_bar_info_query)
```

**Direction:** read/write (both directions)

**Parameter struct:** `pciem_bar_info_query`

### `PCIEM_IOCTL_SET_EVENTFD` {#ioctl-pciem-ioctl-set-eventfd}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_SET_EVENTFD _IOW(PCIEM_IOCTL_MAGIC, 21, struct pciem_eventfd_config)
```

**Direction:** write (userspace → kernel)

**Parameter struct:** `pciem_eventfd_config`

### `PCIEM_IOCTL_SET_IRQFD` {#ioctl-pciem-ioctl-set-irqfd}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_SET_IRQFD _IOW(PCIEM_IOCTL_MAGIC, 22, struct pciem_irqfd_config)
```

**Direction:** write (userspace → kernel)

**Parameter struct:** `pciem_irqfd_config`

### `PCIEM_IOCTL_DMA_INDIRECT` {#ioctl-pciem-ioctl-dma-indirect}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_DMA_INDIRECT _IOWR(PCIEM_IOCTL_MAGIC, 24, struct pciem_dma_indirect)
```

**Direction:** read/write (both directions)

**Parameter struct:** `pciem_dma_indirect`

### `PCIEM_IOCTL_TRACE_BAR` {#ioctl-pciem-ioctl-trace-bar}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_TRACE_BAR _IOWR(PCIEM_IOCTL_MAGIC, 25, struct pciem_trace_bar)
```

**Direction:** read/write (both directions)

**Parameter struct:** `pciem_trace_bar`

### `PCIEM_IOCTL_START` {#ioctl-pciem-ioctl-start}

> *Defined in `pciem_api.h`*

```c
#define PCIEM_IOCTL_START _IO(PCIEM_IOCTL_MAGIC, 26)
```

**Direction:** none (no data transfer)
