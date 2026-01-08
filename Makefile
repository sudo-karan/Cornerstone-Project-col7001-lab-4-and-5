CC = gcc
CFLAGS = -Wall -Wextra -O2
TARGET = vm
OBJS = vm.o jit.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TARGET) $(OBJS) *.bin
