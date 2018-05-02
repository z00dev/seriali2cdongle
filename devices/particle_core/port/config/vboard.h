#ifndef __VBOARD__
#define __VBOARD__


#define STM32F10X_MD

extern uint8_t __ramvectors__[];

#define CORTEX_FLASH_VTABLE 0x8005000
#define CORTEX_VTOR_INIT ((uint32_t)(&__ramvectors__))
#define CORTEX_VECTOR_COUNT	46

#define CORTEX_ENABLE_WFI_IDLE          TRUE

#define PORT_PRIO_BITS 4
#define PORT_PRIO_MASK(n) ((n) << (8 - PORT_PRIO_BITS))


#if !VHAL_ADC_PRESCALER
#define VHAL_ADC_PRESCALER 6
#endif

#if !STM32_ADCPRE
#define STM32_ADCPRE	(2<<14)
#endif


#define STM32_DMA_REQUIRED FALSE

#define VBOARD_SLEEP_MICRO_COMPENSATION	55

#endif