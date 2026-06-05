#ifndef HTTP_SERVER_H
#define HTTP_SERVER_H

#include <string>
#include <map>

class HTTPServer {
public:
    HTTPServer(int port);
    ~HTTPServer();
    
    void start();
    void setDataCallback(std::string (*callback)());
    
private:
    int port;
    int server_fd;
    std::string (*dataCallback)();
    
    void handleClient(int client_socket);
    std::string readFile(const std::string& path);
    std::string getContentType(const std::string& path);
    void sendResponse(int client_socket, int status_code, const std::string& content_type, const std::string& body);
};

#endif
