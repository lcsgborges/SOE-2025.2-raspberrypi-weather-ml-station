#ifndef SENSOR_BME280_H
#define SENSOR_BME280_H

#include <stdint.h>

#define BME280_ADDRESS 0x76

class SensorBME280 {
public:
    SensorBME280();
    bool begin(uint8_t addr = BME280_ADDRESS);
    float readTemperature();
    float readPressure();
    float readHumidity();

private:
    int fd;
    uint8_t read8(uint8_t reg);
    uint16_t read16(uint8_t reg);
    int16_t readS16(uint8_t reg);
    uint32_t read24(uint8_t reg);
    void write8(uint8_t reg, uint8_t value);
    void readCoefficients();

    // Coeficientes de calibração
    uint16_t dig_T1;
    int16_t dig_T2, dig_T3;
    uint16_t dig_P1;
    int16_t dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9;
    uint8_t  dig_H1, dig_H3;
    int16_t  dig_H2, dig_H4, dig_H5, dig_H6;

    int32_t t_fine;
};

#endif
