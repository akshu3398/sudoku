#
# Makefile
#
# Computer Science 50
# Problem Set 4
#

sudoku: Makefile sudoku.c sudoku.h
	gcc -ggdb -std=c11 -Wall -Werror -Wno-unused-but-set-variable -o sudoku sudoku.c helpers.c -lncurses

clean:
	rm -f *.o a.out core log.txt sudoku