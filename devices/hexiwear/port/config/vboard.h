#ifndef __VBOARD__
#define __VBOARD__


#define CORTEX_M4 1

#define VBOARD_SLEEP_MICRO_COMPENSATION 50

extern uint8_t __ramvectors__[];

#if !defined(CORTEX_FLASH_VTABLE)
#define CORTEX_FLASH_VTABLE 0x00000
#endif
#define CORTEX_VTOR_INIT ((uint32_t)(&__ramvectors__))
#define CORTEX_VECTOR_COUNT 86

#define PORT_PRIO_BITS 4
#define PORT_PRIO_MASK(n) ((n) << (8 - PORT_PRIO_BITS))
#define PORT_PRIO_DEFAULT_VALUE 6


#endif
