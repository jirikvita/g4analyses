G4BIN   := /home/qitek/install/geant4-v11.1.1-install/bin
G4CONF  := $(G4BIN)/geant4-config

CXX      ?= g++
CXXFLAGS := -O2 -std=c++17 $(shell $(G4CONF) --cflags)
LDFLAGS  := $(shell $(G4CONF) --libs)

TARGET := timepix
SRC    := timepix.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

run: $(TARGET)
	. $(G4BIN)/geant4.sh && ./$(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all run clean
