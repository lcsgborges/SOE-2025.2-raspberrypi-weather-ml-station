#ifndef CSVLOGGER_H
#define CSVLOGGER_H

#include <string>
#include <fstream>
#include <ctime>
#include <iomanip>
#include <chrono>
#include <mutex>

// Mutex global para sincronizar acesso ao arquivo CSV
extern std::mutex csv_file_mutex;

class CSVLogger {
    private:
        std::ofstream file;
        std::string path;
        bool writtenHeader;

    public:
        CSVLogger(const std::string& fileName);
        ~CSVLogger();

        void writeHeader(const std::string& header);
        void writeLine(float temperature, float pressure, float humidity);
        
        // Método estático para ler o arquivo CSV de forma thread-safe
        static std::string readCSVFile(const std::string& filePath);
};

#endif