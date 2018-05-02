#ifndef __VBOARD__
#define __VBOARD__


#define ATSAM3X8E
#define VBOARD_SLEEP_MICRO_COMPENSATION	50

extern uint8_t __ramvectors__[];

#if !defined(CORTEX_FLASH_VTABLE)
#   define CORTEX_FLASH_VTABLE 0x80000
#endif

#define CORTEX_VTOR_INIT ((uint32_t)(&__ramvectors__))
#define CORTEX_VECTOR_COUNT	45

#define CORTEX_ENABLE_WFI_IDLE          TRUE
#define CORTEX_SIMPLIFIED_PRIORITY		FALSE
#define CORTEX_USE_FPU					FALSE

#define PORT_PRIO_BITS 4
#define PORT_PRIO_MASK(n) ((n) << (8 - PORT_PRIO_BITS))

#define VHAL_SER_RXFIFO_LEN 128
#define VHAL_SER_TXFIFO_LEN 128


#endif