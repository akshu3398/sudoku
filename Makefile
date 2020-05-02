#
# Makefile
#

sudoku: Makefile sudoku.c sudoku.h
	gcc -ggdb -std=c11 -Wall -Werror -Wno-unused-but-set-variable -o sudoku sudoku.c helpers.c -lncurses -lm

clean:
	rm -f *.o a.out core log.txt sudoku
