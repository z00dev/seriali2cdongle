#ifndef __VBOARD__
#define __VBOARD__


#define VBOARD_SLEEP_MICRO_COMPENSATION	50

extern uint8_t __ramvectors__[];

#if defined(VM_FEAT_nrf52_ble) && VM_FEAT_nrf52_ble==1
#define CORTEX_FLASH_VTABLE 0x1f000
#else
#define CORTEX_FLASH_VTABLE 0x00000
#endif
#define CORTEX_VTOR_INIT ((uint32_t)(&__ramvectors__))
#define CORTEX_VECTOR_COUNT	39


#define PORT_PRIO_BITS 3
#define PORT_PRIO_MASK(n) ((n) << (8 - PORT_PRIO_BITS))
#define PORT_PRIO_DEFAULT_VALUE 6


// Nordic SDK Defines
#define __VFP_FP__ 1
#define __FPU_PRESENT 1
#undef __SOFTFP__


#endif
