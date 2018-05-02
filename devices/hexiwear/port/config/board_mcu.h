#ifndef __BOARD_MCU__
#define __BOARD_MCU__


#define PLATFORM_ARMCMx

//#define EXT_INTERRUPTS_NEEDED   8


//VHAL Drivers
#define VHAL_GPIO 1
#define VHAL_EXT 1
#define VHAL_SER 1
#define VHAL_NFO 1
#define VHAL_FLASH 1
// #define VHAL_RNG 0
// #define VHAL_SPI 0
// #define VHAL_ADC 0
// #define VHAL_I2C 0
// #define VHAL_DAC 0
// #define VHAL_CAN 0
#define BOARD_HAS_RNG 0


#define VHAL_SER_TXFIFO_LEN 64
#define VHAL_SER_RXFIFO_LEN 64



#endif
