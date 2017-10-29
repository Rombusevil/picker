#!/usr/bin/python

# This code is available for use under CC0 (Creative Commons 0 - universal).
# You can copy, modify, distribute and perform the work, even for commercial
# purposes, all without asking permission. For more information, see LICENSE.md or
# https://creativecommons.org/publicdomain/zero/1.0/

# usage:
# opts = Picker(
#    title = 'Delete all files',
#    options = ["Yes", "No"]
# ).getSelected()

# returns a simple list
# cancel returns False

import curses
import curses.wrapper

class Picker:
    """Allows you to select from a list with curses"""
    stdscr = None
    win = None
    title = ""
    arrow = ""
    footer = ""
    more = ""
    c_selected = ""
    c_empty = ""

    cursor = 0
    offset = 0
    selected = 0
    selcount = 0
    aborted = False
    highlighted_row = None
    commit = False
    revert = False

    window_height = 25
    window_width = 100
    all_options = []
    length = 0

    def curses_start(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.win = curses.newwin(
            5 + self.window_height,
            self.window_width,
            2,
            4
        )

    def curses_stop(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def getSelected(self):
        if self.aborted == True:
            return( False )

        ret_s = filter(lambda x: x["selected"], self.all_options)
        ret = map(lambda x: x["label"], ret_s)

        # Retuns array with highlighted path as first element and selected list as last (checked)
        return({"highlighted":self.highlighted_row, "commit":self.commit, "revert":self.revert, "checked":ret})

    def redraw(self):
        self.win.clear()
        self.win.border(
            self.border[0], self.border[1],
            self.border[2], self.border[3],
            self.border[4], self.border[5],
            self.border[6], self.border[7]
        )
        self.win.addstr(
            self.window_height + 4, 5, " " + self.footer + " "
        )

        position = 0
        range = self.all_options[self.offset:self.offset+self.window_height+1]
        for option in range:
            if option["selected"] == True:
                line_label = self.c_selected + " "
            else:
                line_label = self.c_empty + " "

            self.win.addstr(position + 2, 5, line_label + option["label"])
            position = position + 1

        # hint for more content above
        if self.offset > 0:
            self.win.addstr(1, 5, self.more)

        # hint for more content below
        if self.offset + self.window_height <= self.length - 2:
            self.win.addstr(self.window_height + 3, 5, self.more)

        self.win.addstr(0, 5, " " + self.title + " ")
        self.win.addstr(
            0, self.window_width - 8,
            " " + str(self.selcount) + "/" + str(self.length) + " "
        )
        self.win.addstr(self.cursor + 2,1, self.arrow)
        self.win.refresh()

    def check_cursor_up(self):
        if self.cursor < 0:
            self.cursor = 0
            if self.offset > 0:
                self.offset = self.offset - 1

    def check_cursor_down(self):
        if self.cursor >= self.length:
            self.cursor = self.cursor - 1

        if self.cursor > self.window_height:
            self.cursor = self.window_height
            self.offset = self.offset + 1

            if self.offset + self.cursor >= self.length:
                self.offset = self.offset - 1

    def curses_loop(self, stdscr):
        self.selected = self.cursor + self.offset
        while 1:
            self.redraw()
            c = stdscr.getch()
            self.revert = False
            self.commit = False
            self.highlighted_row = None

            # Quit
            if c == ord('q') or c == ord('Q'):
                self.aborted = True
                break
            # Navigation
            elif c == curses.KEY_UP or c == ord('k'):
                self.cursor = self.cursor - 1
            elif c == curses.KEY_DOWN or c == ord('j'):
                self.cursor = self.cursor + 1
            # Show diff
            elif c == curses.KEY_RIGHT:
                self.highlighted_row = self.cursor
                break
            # Revert file
            elif c == curses.KEY_LEFT:
                self.highlighted_row = self.cursor
                self.revert = True
                break
			# Mark file
            elif c == ord(' '):
                self.all_options[self.selected]["selected"] = \
                    not self.all_options[self.selected]["selected"]
            # Commit
            elif c == 10:
                self.commit = True
                break

            # deal with interaction limits
            self.check_cursor_up()
            self.check_cursor_down()

            # compute selected position only after dealing with limits
            self.selected = self.cursor + self.offset

            temp = self.getSelected()
            self.selcount = len(temp)

    def __init__(
            self,
            options,
            title='Select',
            arrow="-->",
            footer="Space = toggle, Enter = accept, q = cancel",
            more="...",
            border="||--++++",
            c_selected="[X]",
            c_empty="[ ]",
            options_selected=None,
            cursor_pos=0
    ):
        self.title = title
        self.arrow = arrow
        self.footer = footer
        self.more = more
        self.border = border
        self.c_selected = c_selected
        self.c_empty = c_empty
        self.cursor = cursor_pos

        self.all_options = []

        for i, option in enumerate(options):
            self.all_options.append({
                "label": option,
                "selected": False
            })
            self.length = len(self.all_options)

            # If I have indexes to mark as selected I do that
            if options_selected is not None:
                if option in options_selected:
                    self.all_options[i]["selected"] = True

        self.curses_start()
        curses.wrapper(self.curses_loop)
        self.curses_stop()
