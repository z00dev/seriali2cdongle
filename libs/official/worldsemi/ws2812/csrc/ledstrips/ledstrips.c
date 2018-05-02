#include "zerynth.h"

#define MUL_DIV_APPROX(x,mul,div) (((x)*(mul))/(div))

#if defined(ESP32_VHAL) || defined(ESP8266_VHAL)
static uint32_t _getTicks(void) __attribute__((always_inline));
static inline uint32_t _getTicks(void) {
  uint32_t _ticks;
  __asm__ __volatile__("rsr %0,ccount":"=a" (_ticks));
  return _ticks;
}
#define GETTIME_MICROS() _getTicks()
#else
#define GETTIME_MICROS() *now
#endif

//#define printf(...) vbl_printf_stdout(__VA_ARGS__)
#define printf(...)

C_NATIVE(ws2812_ledstrip_on) {
    C_NATIVE_UNWARN();
    
    register uint32_t cyc, time, t;
    uint8_t *p;
    int32_t n;
    int32_t pin;

    if (parse_py_args("is", nargs, args, &pin, &p, &n) != 2)
        return ERR_TYPE_EXC;
    uint32_t UTICKS = _system_frequency / 1000000;
    uint32_t TIME_800_0 = MUL_DIV_APPROX(UTICKS, 200, 1000);
    uint32_t TIME_800_1 = MUL_DIV_APPROX(UTICKS, 700, 1000);
    uint32_t PERIOD_800 = MUL_DIV_APPROX(UTICKS, 1200, 1000);
    uint8_t pix, mask;
    uint32_t i;
    // printf("uticks: %d, th0: %d, th1: %d, period: %d \n", UTICKS, TIME_800_0, TIME_800_1, PERIOD_800);
    #if !defined(ESP32_VHAL) && !defined(ESP8266_VHAL)
        volatile uint32_t *now = vosTicks();
    #endif
    void *port = vhalPinGetPort(pin);
    int pad = vhalPinGetPad(pin);
    #if defined(ESP8266_VHAL)
        if (pad == 16) return VHAL_UNSUPPORTED_ERROR;
    #endif
    //FORMAT is GRB!!!
    //debug("ws2812_ledstrip_on: pin %x n %i t0: %i t1: %i tp: %i now:%x %x\n", pin, n, TIME_800_0, TIME_800_1, PERIOD_800, *now, now);
    vosSysLock();
    // time = *vosTicks();
    // while (*vosTicks() - time < MUL_DIV_APPROX(UTICKS, 50000, 1000));
    time = GETTIME_MICROS();
    for (i = 0; i < n; i++) {
        pix = p[i];
        vhalPinFastClear(port, pad);
        while (mask) {
            t = (pix & mask) ? TIME_800_1 : TIME_800_0;
            //TH
            time = GETTIME_MICROS();
            vhalPinFastSet(port, pad);
            while (GETTIME_MICROS() - time < t);
            //TL
            vhalPinFastClear(port, pad);
            mask = mask >> 1;
            while (GETTIME_MICROS() - time < (PERIOD_800));
        }
        mask = 128;
        //while (*now - time < PERIOD_800);
    }
    vosSysUnlock();
    vhalPinFastClear(port, pad);
    time = GETTIME_MICROS();
    while (GETTIME_MICROS() - time < MUL_DIV_APPROX(UTICKS, 50000, 1000));
    return ERR_OK;
}
