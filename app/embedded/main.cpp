#include "SensorBME280.h"
#include "CSVLogger.h"
#include "HTTPServer.h"
#include <iostream>
#include <unistd.h>
#include <thread>
#include <mutex>
#include <sstream>
#include <iomanip>

// Variáveis globais para compartilhar dados entre threads
float last_temp = 0.0;
float last_press = 0.0;
float last_hum = 0.0;
std::mutex data_mutex;

// Callback para fornecer dados via API
std::string getLatestData() {
    std::lock_guard<std::mutex> lock(data_mutex);
    std::ostringstream json;
    json << std::fixed << std::setprecision(2);
    json << "{\n";
    json << "  \"temperature\": " << last_temp << ",\n";
    json << "  \"pressure\": " << last_press << ",\n";
    json << "  \"humidity\": " << last_hum << "\n";
    json << "}";
    return json.str();
}

// Thread para leitura do sensor
void sensorThread() {
    SensorBME280 sensor;
    
    if (!sensor.begin()) {
        std::cout << "Falha ao iniciar BME280" << std::endl;
        return;
    }
    
    CSVLogger logger("../runtime-data/data.csv");
    
    while (true) {
        // IMPORTANTE: Ler temperatura primeiro (necessário para calibração da umidade)
        float temp = sensor.readTemperature();
        float press = sensor.readPressure();
        float hum = sensor.readHumidity();
        
        // Atualizar dados compartilhados
        {
            std::lock_guard<std::mutex> lock(data_mutex);
            last_temp = temp;
            last_press = press;
            last_hum = hum;
        }
        
        std::cout << "Temperatura: " << temp << " °C" << std::endl;
        std::cout << "Pressão: " << press << " hPa" << std::endl;
        std::cout << "Umidade: " << hum << " %" << std::endl;
        std::cout << "--------------------------" << std::endl;

        logger.writeLine(temp, press, hum);

        sleep(60);
    }
}

int main() {
    std::cout << "=== Servidor BME280 ===" << std::endl;
    std::cout << "Iniciando sensor e servidor HTTP..." << std::endl;
    
    // Iniciar thread do sensor em background
    std::thread sensor(sensorThread);
    sensor.detach();
    
    // Aguardar primeira leitura
    sleep(2);
    
    // Iniciar servidor HTTP na porta 8080
    HTTPServer server(8080);
    server.setDataCallback(getLatestData);
    
    std::cout << "Servidor iniciado!" << std::endl;
    std::cout << "Acesse: http://localhost:8080" << std::endl;
    
    server.start();
    
    return 0;
}
