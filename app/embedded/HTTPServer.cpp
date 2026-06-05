#include "HTTPServer.h"
#include "CSVLogger.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

HTTPServer::HTTPServer(int port) : port(port), server_fd(-1), dataCallback(nullptr) {}

HTTPServer::~HTTPServer() {
    if (server_fd >= 0) {
        close(server_fd);
    }
}

void HTTPServer::setDataCallback(std::string (*callback)()) {
    dataCallback = callback;
}

std::string HTTPServer::readFile(const std::string& path) {
    std::string fullPath = "../web/" + path;
    std::ifstream file(fullPath, std::ios::binary);
    
    if (!file.is_open()) {
        return "";
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

std::string HTTPServer::getContentType(const std::string& path) {
    if (path.find(".html") != std::string::npos) return "text/html";
    if (path.find(".css") != std::string::npos) return "text/css";
    if (path.find(".js") != std::string::npos) return "application/javascript";
    if (path.find(".json") != std::string::npos) return "application/json";
    if (path.find(".csv") != std::string::npos) return "text/csv";
    return "text/plain";
}

void HTTPServer::sendResponse(int client_socket, int status_code, const std::string& content_type, const std::string& body) {
    std::string status_text = (status_code == 200) ? "OK" : "Not Found";
    
    std::ostringstream response;
    response << "HTTP/1.1 " << status_code << " " << status_text << "\r\n";
    response << "Content-Type: " << content_type << "\r\n";
    response << "Content-Length: " << body.length() << "\r\n";
    response << "Access-Control-Allow-Origin: *\r\n";
    response << "Cache-Control: no-cache, no-store, must-revalidate\r\n";
    response << "\r\n";
    response << body;
    
    std::string resp = response.str();
    send(client_socket, resp.c_str(), resp.length(), 0);
}

void HTTPServer::handleClient(int client_socket) {
    char buffer[4096] = {0};
    read(client_socket, buffer, 4096);
    
    std::string request(buffer);
    std::istringstream iss(request);
    std::string method, path, version;
    iss >> method >> path >> version;
    
    // Remove a barra inicial
    if (path == "/" || path.empty()) {
        path = "/index.html";
    }
    
    // Remove a primeira barra
    if (path[0] == '/') {
        path = path.substr(1);
    }
    
    std::cout << "Requisição: " << method << " " << path << std::endl;
    
    // Endpoint especial para dados em tempo real
    if (path == "api/data") {
        if (dataCallback) {
            std::string data = dataCallback();
            sendResponse(client_socket, 200, "application/json", data);
        } else {
            sendResponse(client_socket, 404, "text/plain", "Data callback not set");
        }
    }
    // Servir arquivo CSV de forma thread-safe
    else if (path.find("data.csv") != std::string::npos) {
        std::string csvContent = CSVLogger::readCSVFile("../runtime-data/data.csv");
        if (!csvContent.empty()) {
            sendResponse(client_socket, 200, "text/csv", csvContent);
        } else {
            sendResponse(client_socket, 404, "text/plain", "CSV file not found or empty");
        }
    }
    // Servir arquivos estáticos
    else {
        std::string content = readFile(path);
        if (!content.empty()) {
            sendResponse(client_socket, 200, getContentType(path), content);
        } else {
            sendResponse(client_socket, 404, "text/plain", "File not found");
        }
    }
    
    close(client_socket);
}

void HTTPServer::start() {
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    
    // Criar socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        std::cerr << "Falha ao criar socket" << std::endl;
        return;
    }
    
    // Permitir reutilizar a porta
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        std::cerr << "Falha no setsockopt" << std::endl;
        return;
    }
    
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);
    
    // Bind
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        std::cerr << "Falha no bind" << std::endl;
        return;
    }
    
    // Listen
    if (listen(server_fd, 10) < 0) {
        std::cerr << "Falha no listen" << std::endl;
        return;
    }
    
    std::cout << "Servidor HTTP rodando na porta " << port << std::endl;
    std::cout << "Acesse: http://localhost:" << port << std::endl;
    
    // Loop principal
    while (true) {
        int client_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
        if (client_socket < 0) {
            std::cerr << "Falha no accept" << std::endl;
            continue;
        }
        
        handleClient(client_socket);
    }
}
