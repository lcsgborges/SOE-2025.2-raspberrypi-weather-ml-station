#include "SensorBME280.h"
#include <wiringPiI2C.h>
#include <unistd.h>
#include <iostream>

SensorBME280::SensorBME280() : fd(-1), t_fine(0) {}

bool SensorBME280::begin(uint8_t addr) {
    fd = wiringPiI2CSetup(addr);
    if (fd < 0) {
        std::cerr << "Erro ao inicializar I2C" << std::endl;
        return false;
    }

    uint8_t chip_id = read8(0xD0);
    if (chip_id != 0x60) {
        std::cerr << "BME280 não encontrado. ID: 0x" << std::hex << (int)chip_id << std::endl;
        return false;
    }

    // Reset
    write8(0xE0, 0xB6);
    usleep(10000);

    readCoefficients();

    // Configuração inicial (ordem importante!)
    write8(0xF2, 0x05); // umidade oversampling x16
    write8(0xF4, 0xB7); // temp/press oversampling x16, modo normal
    write8(0xF5, 0xA0); // config standby 1000ms, filter off

    usleep(100000); // Aguarda estabilização
    return true;
}

void SensorBME280::readCoefficients() {
    dig_T1 = read16(0x88);
    dig_T2 = readS16(0x8A);
    dig_T3 = readS16(0x8C);

    dig_P1 = read16(0x8E);
    dig_P2 = readS16(0x90);
    dig_P3 = readS16(0x92);
    dig_P4 = readS16(0x94);
    dig_P5 = readS16(0x96);
    dig_P6 = readS16(0x98);
    dig_P7 = readS16(0x9A);
    dig_P8 = readS16(0x9C);
    dig_P9 = readS16(0x9E);

    dig_H1 = read8(0xA1);
    dig_H2 = readS16(0xE1);
    dig_H3 = read8(0xE3);
    
    int8_t e4 = read8(0xE4);
    int8_t e5 = read8(0xE5);
    int8_t e6 = read8(0xE6);
    
    dig_H4 = (e4 << 4) | (e5 & 0x0F);
    dig_H5 = (e6 << 4) | ((e5 >> 4) & 0x0F);
    dig_H6 = (int8_t)read8(0xE7);
}

float SensorBME280::readTemperature() {
    int32_t var1, var2, adc_T;
    adc_T = read24(0xFA) >> 4;

    var1 = ((((adc_T >> 3) - ((int32_t)dig_T1 << 1))) * ((int32_t)dig_T2)) >> 11;
    var2 = (((((adc_T >> 4) - ((int32_t)dig_T1)) *
              ((adc_T >> 4) - ((int32_t)dig_T1))) >> 12) *
            ((int32_t)dig_T3)) >> 14;

    t_fine = var1 + var2;
    float T = (t_fine * 5 + 128) >> 8;
    return T / 100.0;
}

float SensorBME280::readPressure() {
    int64_t var1, var2, p;
    int32_t adc_P = read24(0xF7) >> 4;

    var1 = ((int64_t)t_fine) - 128000;
    var2 = var1 * var1 * (int64_t)dig_P6;
    var2 = var2 + ((var1 * (int64_t)dig_P5) << 17);
    var2 = var2 + (((int64_t)dig_P4) << 35);
    var1 = ((var1 * var1 * (int64_t)dig_P3) >> 8) +
           ((var1 * (int64_t)dig_P2) << 12);
    var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)dig_P1) >> 33;

    if (var1 == 0)
        return 0;

    p = 1048576 - adc_P;
    p = (((p << 31) - var2) * 3125) / var1;
    var1 = (((int64_t)dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (((int64_t)dig_P8) * p) >> 19;

    p = ((p + var1 + var2) >> 8) + (((int64_t)dig_P7) << 4);
    return (float)p / 256.0 / 100.0; // em hPa
}

float SensorBME280::readHumidity() {
    // Lê o valor ADC da umidade (16 bits)
    int32_t adc_H = (read8(0xFD) << 8) | read8(0xFE);
    
    if (adc_H == 0x8000) // Valor inválido
        return 0.0f;

    int32_t v_x1_u32r;

    v_x1_u32r = (t_fine - ((int32_t)76800));
    
    v_x1_u32r = (((((adc_H << 14) - (((int32_t)dig_H4) << 20) -
                    (((int32_t)dig_H5) * v_x1_u32r)) + ((int32_t)16384)) >> 15) *
                 (((((((v_x1_u32r * ((int32_t)dig_H6)) >> 10) *
                      (((v_x1_u32r * ((int32_t)dig_H3)) >> 11) +
                       ((int32_t)32768))) >> 10) + ((int32_t)2097152)) *
                   ((int32_t)dig_H2) + 8192) >> 14));

    v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) *
                               ((int32_t)dig_H1)) >> 4));

    v_x1_u32r = (v_x1_u32r < 0) ? 0 : v_x1_u32r;
    v_x1_u32r = (v_x1_u32r > 419430400) ? 419430400 : v_x1_u32r;
    
    float h = (float)(v_x1_u32r >> 12);
    return h / 1024.0f;
}

// Funções auxiliares
uint8_t SensorBME280::read8(uint8_t reg) {
    return wiringPiI2CReadReg8(fd, reg);
}

uint16_t SensorBME280::read16(uint8_t reg) {
    uint16_t value = wiringPiI2CReadReg8(fd, reg) |
                     (wiringPiI2CReadReg8(fd, reg + 1) << 8);
    return value;
}

int16_t SensorBME280::readS16(uint8_t reg) {
    return (int16_t)read16(reg);
}

uint32_t SensorBME280::read24(uint8_t reg) {
    uint32_t value = wiringPiI2CReadReg8(fd, reg);
    value <<= 8;
    value |= wiringPiI2CReadReg8(fd, reg + 1);
    value <<= 8;
    value |= wiringPiI2CReadReg8(fd, reg + 2);
    return value;
}

void SensorBME280::write8(uint8_t reg, uint8_t value) {
    wiringPiI2CWriteReg8(fd, reg, value);
}
