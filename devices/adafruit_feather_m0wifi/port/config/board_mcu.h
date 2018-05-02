#ifndef __BOARD_MCU__
#define __BOARD_MCU__


#if !defined(__ATSAMD21G18AU__)
#define __ATSAMD21G18AU__
#endif

#define PLATFORM_ARMCMx

#define EXT_INTERRUPTS_NEEDED   16


//VHAL Drivers
#define VHAL_GPIO 1
#define VHAL_EXT 1
#define VHAL_SER 1
#define VHAL_CDC 1
#define VHAL_NFO 1
#define VHAL_FLASH 1
#define VHAL_RNG 0
#define VHAL_SPI 0
#define VHAL_ADC 0
#define VHAL_I2C 0
#define VHAL_DAC 0
#define VHAL_CAN 0
#define BOARD_HAS_RNG 0



#endif