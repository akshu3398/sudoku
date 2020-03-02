#include "sudoku.h"
#include "helpers.h"

/*
 * Draw's the game's board.
 */

void
draw_grid(void)
{
    // get window's dimensions
    int maxy, maxx;
    getmaxyx(stdscr, maxy, maxx);

    // determine where top-left corner of board belongs 
    g.top = maxy/2 - 7;
    g.left = maxx/2 - 30;

    // enable color if possible
    if (has_colors())
        attron(COLOR_PAIR(PAIR_GRID));

    // print grid
    for (int i = 0 ; i < 3 ; ++i )
    {
        mvaddstr(g.top + 0 + 4 * i, g.left, "+-------+-------+-------+");
        mvaddstr(g.top + 1 + 4 * i, g.left, "|       |       |       |");
        mvaddstr(g.top + 2 + 4 * i, g.left, "|       |       |       |");
        mvaddstr(g.top + 3 + 4 * i, g.left, "|       |       |       |");
    }
    mvaddstr(g.top + 4 * 3, g.left, "+-------+-------+-------+" );

    // remind user of level and # and also the time elapsed since beginning of the game.
    char reminder[maxx+1];
    sprintf(reminder, "playing %s #%d, time elapsed: %d:%d:%d", 
            g.level, g.number, 
            (int)ceil((g.current - g.start)/3600),
            ((int)ceil((g.current - g.start)/60))%60, 
            (int)(g.current - g.start)%60);
    mvaddstr(g.top + 14, g.left + 50 - strlen(reminder), reminder);

    // disable color if possible
    if (has_colors())
        attroff(COLOR_PAIR(PAIR_GRID));
}


/*
 * Draws game's borders.
 */

void
draw_borders(void)
{
    // get window's dimensions
    int maxy, maxx;
    getmaxyx(stdscr, maxy, maxx);

    // enable color if possible (else b&w highlighting)
    if (has_colors())
    {
        attron(A_PROTECT);
        attron(COLOR_PAIR(PAIR_BORDER));
    }
    else
        attron(A_REVERSE);

    // draw borders
    for (int i = 0; i < maxx; i++)
    {
        mvaddch(0, i, ' ');
        mvaddch(maxy-1, i, ' ');
    }

    // draw header
    char header[maxx+1];
    sprintf(header, "%s by %s", TITLE, AUTHOR);
    mvaddstr(0, (maxx - strlen(header)) / 2, header);

    // draw footer
    mvaddstr(maxy-1, 1, "[N]ew Game   [R]estart Game, [H]int");
    mvaddstr(maxy-1, maxx-13, "[Q]uit Game");

    // disable color if possible (else b&w highlighting)
    if (has_colors())
        attroff(COLOR_PAIR(PAIR_BORDER));
    else
        attroff(A_REVERSE);
}


/*
 * Draws game's logo.  Must be called after draw_grid has been
 * called at least once.
 */

void
draw_logo(void)
{
    // enable color if possible
    if (has_colors())
        attron(COLOR_PAIR(PAIR_LOGO));

    if (!won())
    {
        // determine top-left coordinates of logo
        int top = g.top + 2;
        int left = g.left + 30;

        // draw logo
        mvaddstr(top + 0, left, "               _       _          ");
        mvaddstr(top + 1, left, "              | |     | |         ");
        mvaddstr(top + 2, left, " ___ _   _  __| | ___ | | ___   _ ");
        mvaddstr(top + 3, left, "/ __| | | |/ _` |/ _ \\| |/ / | | |");
        mvaddstr(top + 4, left, "\\__ \\ |_| | (_| | (_) |   <| |_| |");
        mvaddstr(top + 5, left, "|___/\\__,_|\\__,_|\\___/|_|\\_\\\\__,_|");

        // sign logo
        char signature[3+strlen(AUTHOR)+1];
        sprintf(signature, "by %s", AUTHOR);
        mvaddstr(top + 7, left + 35 - strlen(signature) - 1, signature);
    }
    else
    {
        // determine top-left coordinates of logo
        int top = g.top + 1;
        int left = g.left + 25;

        // draw logo
        mvaddstr(top + 0,  left, " _| || |_       / // / | | | |         ");
        mvaddstr(top + 1,  left, "|_  __  _|_   _| |/ /  | |_| |__   ___ ");
        mvaddstr(top + 2,  left, " _| || |_| | | | < <   | __| '_ \\ / _ \\");
        mvaddstr(top + 3,  left, "|_  __  _| |_| | |\\ \\  | |_| | | |  __/");
        mvaddstr(top + 4,  left, "  |_||_|  \\__,_| | \\_\\  \\__|_| |_|\\___|");
        mvaddstr(top + 5,  left, "          _     \\_\\   _   _            ");
        mvaddstr(top + 6,  left, "         | |         | | | |           ");
        mvaddstr(top + 7,  left, " _      _| |__   __ _| |_| |           ");
        mvaddstr(top + 8,  left, "\\ \\ /\\ / / '_ \\ / _` | __| |           ");
        mvaddstr(top + 9,  left, " \\ V  V /| | | | (_| | |_|_|           ");
        mvaddstr(top + 10, left, "  \\_/\\_/ |_| |_|\\__,_|\\__(_)           ");
    }

    // disable color if possible
    if (has_colors())
        attroff(COLOR_PAIR(PAIR_LOGO));
}


/*
 * Draw's game's numbers.  Must be called after draw_grid has been
 * called at least once.
 */

void
draw_numbers(void)
{
    // iterate over board's numbers
    for (int i = 0; i < 9; i++)
    {
        for (int j = 0; j < 9; j++)
        {
            // determine char
            char c = (g.board[i][j] == 0) ? '.' : g.board[i][j] + '0';
            // enable color if possible and if the cell is locked
            if (has_colors() && g.locked[i][j])
                attron((!won()) ? COLOR_PAIR(PAIR_BANNER) : COLOR_PAIR(PAIR_LOGO));
            // enable game winning texture if won
            else if(!g.locked[i][j] && won())
                attron(COLOR_PAIR(PAIR_LOGO));
            mvaddch(g.top + i + 1 + i/3, g.left + 2 + 2*(j + j/3), c);
            // enable color if possible and if the cell is locked
            if (has_colors() && g.locked[i][j])
                attroff((!won()) ? COLOR_PAIR(PAIR_BANNER) : COLOR_PAIR(PAIR_LOGO));
            // enable game winning texture if won
            else if(!g.locked[i][j] && won())
                attroff(COLOR_PAIR(PAIR_LOGO));
            refresh();
        }
    }
}


/*
 * Designed to handles signals (e.g., SIGWINCH).
 */

void
handle_signal(int signum)
{
    // handle a change in the window (i.e., a resizing)
    if (signum == SIGWINCH)
        redraw_all();

    // re-register myself so this signal gets handled in future too
    signal(signum, (void (*)(int)) handle_signal);
}


/*
 * Hides banner.
 */

void
hide_banner(void)
{
    // get window's dimensions
    int maxy, maxx;
    getmaxyx(stdscr, maxy, maxx);

    // overwrite banner with spaces
    for (int i = 0; i < maxx; i++)
        mvaddch(g.top + 16, i, ' ');

    refresh();
}


/*
 * Loads current board from disk, returning true iff successful.
 */

bool
load_board(void)
{
    // open file with boards of specified level
    char filename[strlen(g.level) + 5];
    sprintf(filename, "%s.bin", g.level);
    FILE *fp = fopen(filename, "rb");
    if (fp == NULL)
        return false;

    // determine file's size
    fseek(fp, 0, SEEK_END);
    int size = ftell(fp);

    // ensure file is of expected size
    if (size % (81 * INTSIZE) != 0)
    {
        fclose(fp);
        return false;
    }

    // compute offset of specified board
    int offset = ((g.number - 1) * 81 * INTSIZE);

    // seek to specified board
    fseek(fp, offset, SEEK_SET);

    // read board into memory
    if (fread(g.board, 81 * INTSIZE, 1, fp) != 1)
    {
        fclose(fp);
        return false;
    }

    // lock the cells in the board that came pre-filled
    for (__uint8_t i = 0; i < 9; i++)
        for (__uint8_t j = 0; j < 9; j++)
            g.locked[i][j] = (g.board[i][j] != 0) ? true : false;
    

    // w00t
    fclose(fp);
    return true;
}


/*
 * Logs input and board's state to log.txt to facilitate automated tests.
 */

void
log_move(int ch)
{
    // open log
    FILE *fp = fopen("log.txt", "a");
    if (fp == NULL)
        return;

    // log input
    fprintf(fp, "%d\n", ch);

    // log board
    for (int i = 0; i < 9; i++)
    {
        for (int j = 0; j < 9; j++)
            fprintf(fp, "%d", g.board[i][j]);
        fprintf(fp, "\n");
    }

    // that's it
    fclose(fp);
}


/*
 * (Re)draws everything on the screen.
 */

void
redraw_all(void)
{
    // reset ncurses
    endwin();

    // clear screen
    clear();

    // re-draw everything
    draw_borders();
    draw_grid();
    draw_logo();
    draw_numbers();

    // show cursor
    show_cursor();
    
    // update display
    refresh();
}


/*
 * (Re)starts current game, returning true if succesful.
 */

bool
restart_game(void)
{
    // reload current game
    if (!load_board())
        return false;

    // redraw board
    draw_grid();
    draw_numbers();

    // get window's dimensions
    int maxy, maxx;
    getmaxyx(stdscr, maxy, maxx);

    // move cursor to board's center
    g.y = g.x = 4;
    show_cursor();

    // remove log, if any
    remove("log.txt");

    // w00t
    return true;
}


/*
 * Shows cursor at (g.y, g.x).
 */

void
show_cursor(void)
{
    // restore cursor's location
    move(g.top + g.y + 1 + g.y/3, g.left + 2 + 2*(g.x + g.x/3));
}


/*
 * Shows a banner.  Must be called after show_grid has been
 * called at least once.
 */

void
show_banner(char *b)
{
    // determine where top-left corner of board belongs 
    mvaddstr(g.top + 16, g.left + 64 - strlen(b), b);
}


/*
 * Shuts down ncurses.
 */

void
shutdown(void)
{
    endwin();
}


/*
 * Starts up ncurses.  Returns true iff successful.
 */

bool
startup(void)
{
    // initialize ncurses
    if (initscr() == NULL)
        return false;

    // prepare for color if possible
    if (has_colors())
    {
        // enable color
        if (start_color() == ERR || attron(A_PROTECT) == ERR)
        {
            endwin();
            return false;
        }

        // initialize pairs of colors
        if (init_pair(PAIR_BANNER, FG_BANNER, BG_BANNER) == ERR ||
            init_pair(PAIR_GRID, FG_GRID, BG_GRID) == ERR ||
            init_pair(PAIR_BORDER, FG_BORDER, BG_BORDER) == ERR ||
            init_pair(PAIR_LOGO, FG_LOGO, BG_LOGO) == ERR)
        {
            endwin();
            return false;
        }
    }

    // don't echo keyboard input
    if (noecho() == ERR)
    {
        endwin();
        return false;
    }

    // disable line buffering and certain signals
    if (raw() == ERR)
    {
        endwin();
        return false;
    }

    // enable arrow keys
    if (keypad(stdscr, true) == ERR)
    {
        endwin();
        return false;
    }

    // wait 1000 ms at a time for input
    timeout(1000);

    // w00t
    return true;
}

/* 
* check given move validity 
* return false if cell-number's twin found else return true
* input: (int)y ∈ [0, 9), (int)x ∈ [0, 9), (int)num ∈ [1, 9]
*/
bool valid_move(int y, int x, int num)
{ 
    // check inside cell-box
    for (__uint8_t j = 3*ceil(y/3), m = 3*ceil(y/3); j < m+3; j++)
        for (__uint8_t i = 3*ceil(x/3), n = 3*ceil(x/3); i < n+3; i++)
            if (g.board[j][i] == num && i != x && j != y)
                return false;
    
    // check cell-row wise
    for (__uint8_t i = 0; i < 9; i++)
        if (g.board[i][x] == num && i != y)
            return false;

    // check cell-col wise
    for (__uint8_t i = 0; i < 9; i++)
        if (g.board[y][i] == num && i != x)
            return false;
    
    return true;
}

/* 
* check if the given board is completed and game is won 
*/
bool won(void)
{
    for (size_t i = 0; i < 9; i++)
        for (size_t j = 0; j < 9; j++)
            if (!g.locked[i][j])
                if (!g.board[i][j] || !valid_move(i, j, g.board[i][j]))
                    return false;

    return true;
}

/* 
* [H]int feature: whereby hitting 'H' fills in a blank(with a correct number) on behalf of the player each time that its called during play 
*/
void hint(void)
{
    char message[60];
    // for every playable number find the possible places where it can & can't be inserted
    bool numPlaces[9][9][9];
    __uint8_t numCntr;
    // for every cell in the board check if the num is playable & 
    // update its possibility into numPlaces
    for (__uint8_t num = 1; num <= 9; num++)
        for (__uint8_t i = 0; i < 9; i++)
            for (__uint8_t j = 0; j < 9; j++)
                numPlaces[num-1][i][j] = (!g.board[i][j] && valid_move(i, j, num));

    // for every cell in the board
    for (__uint8_t k = 1; k <= 9; k++)
    {
        // find and display hint for this num block wise
        for (__uint8_t num = 1; num <= 9; num++)
            if (pos_asPer_probability(numPlaces[num-1], num))
                return;
        

        // find and display hint for this num row-col wise
        for (__uint8_t i = 0; i < 9; i++)
            for (__uint8_t j = 0; j < 9; j++)
            {
                // find and display a place where minimum number of solutions exists
                numCntr = 0;
                for (__uint8_t num = 0; num < 9; num++)
                    numCntr += (numPlaces[num][i][j] != 0 && !g.board[i][j]) ? 1 : 0;
                
                if (numCntr <= k && numCntr > 0)
                {
                    // enable color if possible
                    if (has_colors())
                        attron(COLOR_PAIR(PAIR_LOGO));
                    sprintf(message, "only %d number/s possible in the cell(%d, %d)", numCntr, i+1, j+1);
                    show_banner(message);
                    // enable color if possible
                    if (has_colors())
                        attroff(COLOR_PAIR(PAIR_LOGO));
                    refresh();
                    sleep(3);
                    hide_banner();
                    return;
                }
            }
    }
}

/* 
* display the position of num as per the it's probability 
* input: (bool[9][9] array)probability space, (uint)num for hint
*/
bool pos_asPer_probability(bool numPlaces[9][9], __uint8_t num)
{
    char message[40];
    // for each sub box/block
    __uint8_t numPossibilities = 0;
    for (__uint8_t i = 0; i < 3; i++)
        for (__uint8_t j = 0; j < 3; j++)
        {
            // find first box/block which has only one possible place for our number
            numPossibilities = 0;
            for (__uint8_t x = 3*i + 0; x < 3*i + 3; x++)
                for (__uint8_t y = 3*j + 0; y < 3*j + 3; y++)
                    numPossibilities += (int)numPlaces[x][y];

            // if the subbox contains exactly probability number of places for our number
            // hint the player the last position of this number by printing to the screen
            if (numPossibilities == 1)
            {
                // enable color if possible
                if (has_colors())
                    attron(COLOR_PAIR(PAIR_LOGO));
                sprintf(message, "place %d in the box(%d, %d)", num, i+1, j+1);
                show_banner(message);
                // enable color if possible
                if (has_colors())
                    attroff(COLOR_PAIR(PAIR_LOGO));
                refresh();
                sleep(3);
                hide_banner();
                return true;
            }
        }
    return false;
}