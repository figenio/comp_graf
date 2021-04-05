CC = g++

GLLIBS = -lglut -lGLEW -lGL

all: projection.cpp projection2.cpp projection3.cpp
	$(CC) projection.cpp ../lib/utils.cpp -o projection $(GLLIBS)
	$(CC) projection2.cpp ../lib/utils.cpp -o projection2 $(GLLIBS)
	$(CC) projection3.cpp ../lib/utils.cpp -o projection3 $(GLLIBS)

clean:
	rm -f projection projection2 projection3
