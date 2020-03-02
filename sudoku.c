/****************************************************************************
 * sudoku.c
 *
 * Computer Science 50
 * Problem Set 4
 *
 * Implements the game of Sudoku.
 ***************************************************************************/

#include "sudoku.h"
#include "helpers.h"

/*
 * Main driver for the game.
 */

int
main(int argc, char *argv[])
{
    // define usage
    const char *usage = "Usage: sudoku n00b|l33t [#]\n";

    // ensure that number of arguments is as expected
    if (argc != 2 && argc != 3)
    {
        fprintf(stderr, "%s", usage);
        return 1;
    }

    // ensure that level is valid
    if (strcmp(argv[1], "debug") == 0)
        g.level = "debug";
    else if (strcmp(argv[1], "n00b") == 0)
        g.level = "n00b";
    else if (strcmp(argv[1], "l33t") == 0)
        g.level = "l33t";
    else
    {
        fprintf(stderr, "%s", usage);
        return 2;
    }

    // n00b and l33t levels have 1024 boards; debug level has 9
    int max = (strcmp(g.level, "debug") == 0) ? 9 : 1024;

    // ensure that #, if provided, is in [1, max]
    if (argc == 3)
    {
        // ensure n is integral
        char c;
        if (sscanf(argv[2], " %d %c", &g.number, &c) != 1)
        {
            fprintf(stderr,"%s", usage);
            return 3;
        }

        // ensure n is in [1, max]
        if (g.number < 1 || g.number > max)
        {
            fprintf(stderr, "That board # does not exist!\n");
            return 4;
        }

        // seed PRNG with # so that we get same sequence of boards
        srand(g.number);
    }
    else
    {
        // seed PRNG with current time so that we get any sequence of boards
        srand(time(NULL));

        // choose a random n in [1, max]
        g.number = rand() % max + 1;
    }

    // start up ncurses
    if (!startup())
    {
        fprintf(stderr, "Error starting up ncurses!\n");
        return 5;
    }

    // register handler for SIGWINCH (SIGnal WINdow CHanged)
    signal(SIGWINCH, (void (*)(int)) handle_signal);

    // start the first game
    if (!restart_game())
    {
        shutdown();
        fprintf(stderr, "Could not load board from disk!\n");
        return 6;
    }
    redraw_all();

    // start the clock
    g.start = time(NULL);

    // let the user play!
    int ch;
    do
    {
        // refresh and update the screen
        redraw_all();

        // get user's input
        ch = getch();

        // capitalize input to simplify cases
        ch = toupper(ch);

        // play game if it is yet to be won
        if (!won() || 
            tolower(ch) == 'q' || 
            ch == KEY_UP || ch == KEY_DOWN || 
            ch == KEY_LEFT || ch == KEY_RIGHT)
        {
            // process user's input
            switch (ch)
            {
                // start a new game
                case 'N': 
                    g.number = rand() % max + 1;
                    if (!restart_game())
                    {
                        shutdown();
                        fprintf(stderr, "Could not load board from disk!\n");
                        return 6;
                    }
                    break;

                // restart current game
                case 'R': 
                    if (!restart_game())
                    {
                        shutdown();
                        fprintf(stderr, "Could not load board from disk!\n");
                        return 6;
                    }
                    break;

                // move the cur upwards one unit if it doesn't reach edge
                case KEY_UP:
                case 'W':
                    g.y = !(g.y-1 <= 0) ? g.y-1: 0;
                    break;

                // move the cur downwards one unit if it doesn't reach edge
                case KEY_DOWN:
                case 'S':
                    g.y = !(g.y+1 >= 8) ? g.y+1: 8;
                    break;

                // move the cur leftwards one unit if it doesn't reach edge
                case KEY_LEFT:
                case 'A':
                    g.x = !(g.x-1 <= 0) ? g.x-1: 0;
                    break;

                // move the cur rightwards one unit if it doesn't reach edge
                case KEY_RIGHT:
                case 'D':
                    g.x = !(g.x+1 >= 8) ? g.x+1: 8;
                    break;

                // clear the cell where the cur is at, if possible otherwise alert the player of a wrong move
                case KEY_BACKSPACE:
                case KEY_DC:
                case '0':
                case '.':
                    if (!g.locked[g.y][g.x])
                        g.board[g.y][g.x] = 0;
                    else
                    {
                        // enable color if possible and if the cell is locked
                        if (has_colors())
                            attron(COLOR_PAIR(PAIR_BANNER));
                        show_banner("invalid operation!");
                        // enable color if possible and if the cell is locked
                        if (has_colors())
                            attroff(COLOR_PAIR(PAIR_BANNER));
                        refresh();
                        
                        sleep(3);
                        hide_banner();
                    }
                    break;

                // update board via number passed by player if possible to where cursor is at, otherwise alert the player of a wrong move
                case '1':
                case '2':
                case '3':
                case '4':
                case '5':
                case '6':
                case '7':
                case '8':
                case '9':
                    if (!g.locked[g.y][g.x])
                    {
                        // check, update & display move validity
                        if (valid_move(g.y, g.x, (int)(ch - '0')))
                        {
                            g.board[g.y][g.x] = ch - '0';
                            // enable color if possible
                            if (has_colors())
                                attron(COLOR_PAIR(PAIR_LOGO));
                            show_banner("nice move!");
                            // enable color if possible
                            if (has_colors())
                                attroff(COLOR_PAIR(PAIR_LOGO));
                        }
                        else
                        {
                            // enable color if possible
                            if (has_colors())
                                attron(COLOR_PAIR(PAIR_BANNER));
                            show_banner("err, try again!");
                            // enable color if possible
                            if (has_colors())
                                attroff(COLOR_PAIR(PAIR_BANNER));
                        }
                    }
                    else
                    {
                        // enable color if possible and if the cell is locked
                        if (has_colors())
                            attron(COLOR_PAIR(PAIR_BANNER));
                        show_banner("invalid operation!");
                        // enable color if possible and if the cell is locked
                        if (has_colors())
                            attroff(COLOR_PAIR(PAIR_BANNER));
                    }
                    refresh();
                    sleep(3);
                    hide_banner();
                    break;

                // fills in a blank (with a correct number) on behalf of the player
                case 'H':
                    // display a rough hint
                    hint();
                    break;
                
                case 'U':
                case CTRL('z'):
                    // todo: undo last change
                    break;

                // let user manually redraw screen with ctrl-L
                case CTRL('l'):
                default:
                    redraw_all();
                    break;
            }
            g.current = time(NULL);
        }

        // log input (and board's state) if any was received this iteration
        if (ch != ERR)
            log_move(ch);
    }
    while (ch != 'Q');

    // shut down ncurses
    shutdown();

    // tidy up the screen (using ANSI escape sequences)
    printf("\033[2J");
    printf("\033[%d;%dH", 0, 0);

    // that's all folks
    printf("\nkthxbai!\n\n");
    return 0;
}