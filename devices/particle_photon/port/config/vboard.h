#ifndef __VBOARD__
#define __VBOARD__

extern uint8_t __ramvectors__[];

#define CORTEX_FLASH_VTABLE 0x8020000

#define CORTEX_VTOR_INIT ((uint32_t)(&__ramvectors__))
#define CORTEX_VECTOR_COUNT	81


#define CORTEX_ENABLE_WFI_IDLE          TRUE
#define CORTEX_SIMPLIFIED_PRIORITY		FALSE
#define CORTEX_USE_FPU					FALSE

#define PORT_PRIO_BITS 4
#define PORT_PRIO_MASK(n) ((n) << (8 - PORT_PRIO_BITS))

#define VHAL_ADC_PRESCALER 4
#define VBOARD_SLEEP_MICRO_COMPENSATION	20

#define CDC_USB_VERSION 0x0200
#define CDC_ID_VENDOR 0x2b04
#define CDC_ID_PRODUCT 0xc006

#define CDC_VENDOR_STRING {'P', 0, 'a', 0, 'r', 0, 't', 0, 'i', 0, 'c', 0, 'l', 0, 'e', 0}
#define CDC_VENDOR_STRING_LEN 18

#define CDC_DESC_STRING \
{ 'P', 0, 'a', 0, 'r', 0, 't', 0, 'i', 0, 'c', 0, 'l', 0, 'e', 0, \
  ' ', 0, 'P', 0, 'h', 0, 'o', 0, 't', 0,'o', 0,'n', 0, ' ', 0, 'V', 0, 'i', 0, \
  'r', 0, 't', 0, 'u', 0, 'a', 0, 'l', 0, 'z', 0, 'e', 0, 'd', 0, \
  ' ', 0 }

#define CDC_DESC_STRING_LEN 56

#define CDC_USE_OTG_HS 1
#define CDC_PACK_SIZE 64
#define CDC_PUMP_THREAD_SIZE 256

#endif