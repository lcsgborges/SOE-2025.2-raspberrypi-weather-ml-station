CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -pthread
LDFLAGS = -lwiringPi -lpthread

SRC = main.cpp SensorBME280.cpp CSVLogger.cpp HTTPServer.cpp
OUT = bme280_server

all: $(OUT)

$(OUT):
	$(CXX) $(CXXFLAGS) $(SRC) -o $(OUT) $(LDFLAGS)

clean:
	rm -f $(OUT)
