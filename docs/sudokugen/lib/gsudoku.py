# GUI to Sudoku
import gtk, sudoku, math, gobject
import pango, random

class ParallelDict (dict):
    """A handy new sort of dictionary for tracking conflicts.

    pd = ParallelDict()
    pd[1] = [2,3,4] # 1 is linked with 2,3 and 4
    pd -> {1:[2,3,4],2:[1],3:[1],4:[1]}
    pd[2] = [1,3,4] # 2 is linked with 3 and 4 as well as 1
    pd -> {1: [2,3,4],2:[3,4],3:[1,2],4:[1,2]}
    Now for the cool part...
    del pd[1]
    pd -> {2: [2,3],3:[2],4:[2]}
    
    Pretty neat, no?
    """
    def __init__ (self, *args):
        dict.__init__(self,*args)

    def __setitem__ (self, k, v):
        dict.__setitem__(self,k,set(v))
        for i in v:
            if i == k: continue
            if self.has_key(i):
                self[i].add(k)
            else:
                dict.__setitem__(self,i,set([k]))
            
    def __delitem__ (self, k):
        v=self[k]
        dict.__delitem__(self,k)
        for i in v:
            print 'i',i
            if i==k: continue
            if k in self[i]: self[i].remove(k)
            if not self[i]:
                dict.__delitem__(self,i)

class Fonts:
    read_only_font = pango.FontDescription()
    read_only_font.set_weight(pango.WEIGHT_BOLD)
    read_only_font.set_size(pango.SCALE * 16)
    normal_font = pango.FontDescription()
    normal_font.set_weight(pango.WEIGHT_NORMAL)
    normal_font.set_size(pango.SCALE * 16)
    error_color = "#FF0000"
    normal_color = "#000000"
    colors = ["#%02x%02x%02x"%(r,b,g) for r,b,g in [(0,0,255), #blue
                                                    (0,255,0), # green
                                                    (255,0,255),#purple
                                                    (255,128,0),#orange
                                                    #(0,255,128),#turquoise-ish
                                                    (128,0,255),#dark purple
                                                    (128,128,128),#grey
                                                    (165,25,25),#maroon-ish
                                                    (0,128,0), #dark green
                                                    (0,0,128), #dark blue
                                                    (139,105,20),#muddy
                                                    ]
              ]

def change_font_size (size):
    Fonts.normal_font.set_size(size)
    Fonts.read_only_font.set_size(size)

class NumberEntry (gtk.Entry):
    conversions = {10:'A',
                   11:'B',
                   12:'C',
                   13:'D',
                   14:'E',
                   15:'F',
                   16:'G',
                   }
    def __init__ (self, upper=9):
        gtk.Entry.__init__(self)
        for k,v in self.conversions.items(): self.conversions[v]=k
        self.color = None
        self.upper = upper
        self.set_width_chars(2)
        self.set_alignment(0.5)
        self.set_max_length(1)
        self.modify_font(Fonts.normal_font)
        self.read_only=False
        self.__internal_change__ = False
        self.connect('focus-out-event',self.focus_out_cb)
        self.connect('key-press-event',self.keypress_cb)
        self.connect('changed',self.changed_cb)
        self.color = None
        self.show()

    def changed_cb (self, *args):
        if self.__internal_change__:
            self.emit_stop_by_name('changed')
            return True

    def set_read_only (self, val):
        self.set_editable(not val)
        self.set_sensitive(not val)
        self.read_only = val
        if val: self.modify_font(Fonts.read_only_font)
        else:
            self.modify_font(Fonts.normal_font)

    def _set_color_ (self, color):
        color = self.get_colormap().alloc_color(color)
        self.modify_text(gtk.STATE_NORMAL,color)

    def set_color (self, color):
        self.color = color
        self._set_color_(color)

    def unset_color (self):
        self.color = None
        self._set_color_(Fonts.normal_color)

    def set_error_highlight (self, val):
        if val:
            self._set_color_(Fonts.error_color)
            self.set_sensitive(True)
        else:
            if self.read_only: self.set_sensitive(False)
            if self.color:
                self._set_color_(self.color)
            else:
                self.unset_color()
        
    def set_value (self, val):
        if val > self.upper:
            raise ValueError("Too large a number!")
        if val >= 10:
            self.__internal_change__ = True
            self.set_text(self.conversions[val])
            self.__internal_change__ = False
        else:
            self.__internal_change__ = True
            if val: self.set_text(str(val))
            else: self.set_text("")
            self.__internal_change__ = False            
            
    def get_value (self):
        txt = self.get_text()
        if self.conversions.has_key(txt.capitalize()):
            val = self.conversions[txt.capitalize()]
        else:
            try:
                val = int(txt)
            except:
                val = None
        if val > self.upper:
            self.set_text("")
            raise ValueError("Too large a number!")
        return val

    def set_impossible (self, val):
        if val:
            try:
                self.__internal_change__=True
                self.set_text('X')
                self.__internal_change__=False
            except: pass
        else:
            if self.get_text()=='X':
                self.__internal_change__=True
                self.set_text('')
                self.__internal_change__=False
        self.impossible = val
        self.set_error_highlight(val)


    def focus_out_cb (self, widget, event):
        widget.select_region(0,0)

    def keypress_cb (self, widget, event):
        name = gtk.gdk.keyval_name(event.keyval)
        parent = widget.get_parent()
        while parent and not isinstance(parent,gtk.Window) :
            parent = parent.get_parent()
        if name == 'Left':
            #widget.emit('focus-out-event',event)
            parent.emit('move-focus',gtk.DIR_LEFT)
            return True
        elif name == 'Right':
            #widget.emit('focus-out-event',event)
            parent.emit('move-focus',gtk.DIR_RIGHT)
            return True
        
        
class EntryGrid (gtk.Table):
    def __init__ (self, group_size=9):
        gtk.Table.__init__(self,rows=group_size,columns=group_size,homogeneous=True)
        self.group_size = int(group_size)
        box_side = int(math.sqrt(self.group_size))
        for n in range(1,box_side):
            self.set_row_spacing(box_side*n-1,4)
            self.set_col_spacing(box_side*n-1,4)
        self.__entries__ = {}
        for x in range(self.group_size):
            for y in range(self.group_size):
                e = NumberEntry(upper=self.group_size)
                e.x = x
                e.y = y
                self.attach(e,x,x+1,y,y+1,
                            xoptions=gtk.SHRINK,
                            yoptions=gtk.SHRINK,
                            xpadding=0,
                            ypadding=0)
                self.__entries__[(x,y)]=e
        self.show_all()

    def get_focused_entry (self):
        for e in self.__entries__.values():
            if e.is_focus(): return e

    def change_font_size (self, size=None, multiplier=1):
        if not size and not multiplier: raise "No size given you dumbass"
        if multiplier:
            size = multiplier * (Fonts.normal_font.get_size() or pango.SCALE * 12)
        change_font_size(size)
        for e in self.__entries__.values():
            if e.read_only: e.modify_font(Fonts.read_only_font)
            else: e.modify_font(Fonts.normal_font)

class SudokuGridDisplay (EntryGrid, gobject.GObject):

    __gsignals__ = {
        'puzzle-finished':(gobject.SIGNAL_RUN_LAST,gobject.TYPE_NONE,())
        }
    
    def __init__ (self,grid=None,group_size=9,
                  show_impossible_implications=False):
        self.hints = 0
        self.auto_fills = 0
        self.show_impossible_implications = show_impossible_implications
        self.impossible_hints = 0
        self.impossibilities = []
        self.trackers = {}
        self.__trackers_tracking__ = {}
        self.__colors_used__ = [Fonts.error_color, Fonts.normal_color]
        gobject.GObject.__init__(self)
        EntryGrid.__init__(self,group_size=group_size)
        self.setup_grid(grid,group_size)
        for e in self.__entries__.values():
            e.show()
            e.connect('changed',self.entry_callback)
            e.connect('focus-in-event',self.focus_callback)
            #e.connect('clicked',self.focus_callback)

    def focus_callback (self, e, event):
        if hasattr(self,'hint_in_label') and self.hint_in_label: self.hint_in_label.set_text('')
        self.focused = e
        if hasattr(self,'label'):
            self.show_hint(self.label)

    def show_hint (self, label):
        self.hints += 1
        self.hint_in_label = label
        entry = self.focused
        if entry.read_only:
            label.set_text('')
        else:
            vals=self.grid.possible_values(entry.x,entry.y)
            vals = list(vals)
            vals.sort()
            if vals:
                label.set_text("Possible values " + ",".join(self.num_to_str(v) for v in vals))
            elif not entry.get_text():
                label.set_text("No values are possible!")
            else:
                label.set_text("")

    def num_to_str (self, n):
        if n >= 10: return NumberEntry.conversions[n]
        else: return str(n)

    def reset_grid (self):
        """Reset grid to its original setup.

        Return a list of items we removed so that callers can handle
        e.g. Undo properly"""
        removed = []
        for x in range(self.group_size):
            for y in range(self.group_size):
                if not self.grid.virgin._get_(x,y):
                    val = self.grid._get_(x,y)
                    if val:
                        #print 'Removing ',x,y,val
                        removed.append((x,y,val,self.trackers_for_point(x,y,val)))
                        self.remove(x,y)
                        self.grid.remove(x,y)
        return removed
    
    def blank_grid (self):
        for x in range(self.group_size):
            for y in range(self.group_size):
                self.remove(x,y)                
                e=self.__entries__[(x,y)]
                e.set_read_only(False)                
        self.grid = None

    def change_grid (self, grid, group_size):
        self.blank_grid()
        self.setup_grid(grid,group_size)
        self.auto_fills = 0
        self.hints = 0
        self.impossible_hints = 0
        self.trackers = {}
        self.__trackers_tracking__ = {}
        self.__colors_used__ = [Fonts.error_color, Fonts.normal_color]

    def load_game (self, game):
        """Load a game.

        A game is simply a two lined string where the first line represents our
        virgin self and line two represents our game-in-progress.
        """
        self.blank_grid()
        virgin,in_prog = game.split('\n')
        group_size=math.sqrt(len(virgin.split()))
        self.change_grid(virgin,group_size=group_size)
        # This int() will break if we go to 16x16 grids...
        values = [int(c) for c in in_prog.split()]
        for row in range(group_size):
            for col in range(group_size):
                index = row * 9 + col
                if values[index] and not self.grid._get_(col,row):
                    self.add(col,row,values[index])

    def setup_grid (self, grid, group_size):
        self.doing_initial_setup = True
        self.__error_pairs__ = ParallelDict()
        if isinstance(grid,sudoku.SudokuGrid):
            self.grid = sudoku.InteractiveSudoku(grid.grid,group_size=grid.group_size)
        else:
            self.grid = sudoku.InteractiveSudoku(grid,group_size=group_size)
        for x in range(group_size):
            for y in range(group_size):
                val=self.grid._get_(x,y)
                if val: self.add(x,y,val)
        self.doing_initial_setup = False

    def entry_callback (self, widget, *args):
        if not widget.get_text():
            if self.grid and self.grid._get_(widget.x,widget.y):
                self.grid.remove(widget.x,widget.y)
            self.remove(widget.x,widget.y)
        else:
            self.entry_validate(widget)
        if self.show_impossible_implications:
            self.mark_impossibile_implications(widget.x,widget.y)

    def entry_validate (self, widget, *args):
        val = widget.get_value()
        try:
            self.add(widget.x,widget.y,val)
            if self.grid.check_for_completeness():
                self.emit('puzzle-finished')
        except sudoku.ConflictError, err:
            conflicts=[self.grid.find_conflict(err.x,err.y,err.value,err.type)]
            # We check for more than one conflict...  We count on the
            # order conflicts are checked for in our initial script in
            # sudoku.py -- ROW then COLUMN then BOX
            if err.type==sudoku.TYPE_ROW:
                print 'check for col...'
                if err.value in self.grid.cols[err.x]:
                    conflicts.append(self.grid.find_conflict(err.x,err.y,err.value,sudoku.TYPE_COLUMN))
            if err.type in [sudoku.TYPE_COLUMN,sudoku.TYPE_ROW]:
                print 'check for box...'
                if err.value in self.grid.boxes[self.grid.box_by_coords[(err.x,err.y)]]:
                    conflicts.append(self.grid.find_conflict(err.x,err.y,err.value,sudoku.TYPE_BOX))
            for conflict in conflicts:
                widget.set_error_highlight(True)
                self.__entries__[conflict].set_error_highlight(True)
            self.__error_pairs__[(err.x,err.y)]=conflicts

    def add (self, x, y, val, trackers=[]):
        """Add value val at position x,y.

        If tracker is True, we track it with tracker ID tracker.

        Otherwise, we use any currently tracking trackers to track our addition.

        Providing the tracker arg is mostly useful for e.g. undo/redo
        or removed items.

        To specify NO trackers, use trackers=[-1]
        """
        self.__entries__[(x,y)].set_value(val)
        if self.doing_initial_setup:
            self.__entries__[(x,y)].set_read_only(True)
        self.grid.add(x,y,val,True)
        if trackers:
            for tracker in trackers:
                if tracker==-1: pass
                self.__entries__[(x,y)].set_color(self.get_tracker_color(tracker))
                self.trackers[tracker].append((x,y,val))
        elif True in self.__trackers_tracking__.values():        
            for k,v in self.__trackers_tracking__.items():
                if v:
                    self.__entries__[(x,y)].set_color(self.get_tracker_color(k))
                    self.trackers[k].append((x,y,val))

    def remove (self, x, y):
        """Remove x,y.
        """
        e=self.__entries__[(x,y)]
        if self.__error_pairs__.has_key((x,y)):
            e.set_error_highlight(False)
            errors_removed = self.__error_pairs__[(x,y)]
            del self.__error_pairs__[(x,y)]
            for coord in errors_removed:
                # If we're not an error by some other pairing...
                if not self.__error_pairs__.has_key((x,y)):
                    linked_entry = self.__entries__[coord]
                    linked_entry.set_error_highlight(False)
                    # Its possible this highlighted error was never
                    # added to our internal grid, in which case we'd
                    # better make sure it is...
                    if not self.grid._get_(linked_entry.x,linked_entry.y):
                        self.grid.add(linked_entry.x,linked_entry.y,linked_entry.get_value())
        # remove trackers
        for t in self.trackers_for_point(x,y):
            remove = []
            for crumb in self.trackers[t]:
                if crumb[0]==x and crumb[1]==y:
                    remove.append(crumb)
            for r in remove:
                self.trackers[t].remove(r)
        if e.get_text(): e.set_value(0)
        e.unset_color()

    def auto_fill (self):
        #changed=self.grid.auto_fill()
        #changed=self.grid.fill_must_fills        
        changed=self.grid.fill_deterministically()
        retval = []
        for coords,val in changed:
            self.add(coords[0],coords[1],val)
            retval.append((coords[0],coords[1],val))
        if retval: self.auto_fills += 1
        return retval
    
    def mark_impossibile_implications (self, x, y):
        implications = self.grid.find_impossible_implications(x,y)
        if implications:
            for x,y in implications:
                self.__entries__[(x,y)].set_impossible(True)
                if not (x,y) in self.impossibilities:
                    self.impossible_hints += 1
        for x,y in self.impossibilities:
            if not (x,y) in implications:
                self.__entries__[(x,y)].set_impossible(False)
        self.impossibilities = implications

    def create_tracker (self, identifier=0):
        if not identifier: identifier = 0
        while self.trackers.has_key(identifier): identifier+=1
        self.trackers[identifier]=[]
        #self.__trackers_tracking__[identifier]=True
        return identifier

    def trackers_for_point (self, x, y, val=None):
        if val:
            # if we have a value we can do this a simpler way...
            track_for_point = filter(
                lambda t: (x,y,val) in t[1],
                self.trackers.items()
                )
        else:
            track_for_point = filter(
                lambda tkr: True in [t[0]==x and t[1]==y for t in tkr[1]],
                self.trackers.items())
        return [t[0] for t in track_for_point]

    def get_tracker_color (self, identifier):
        if len(Fonts.colors)>identifier:
            return Fonts.colors[identifier]
        else:
            Fonts.colors.append("#%02x%02x%02x"%(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            return self.get_tracker_color(identifier)

    def toggle_tracker (self, identifier, value):
        """Toggle tracking for tracker identified by identifier."""
        self.__trackers_tracking__[identifier]=value

    def delete_by_tracker (self, identifier):
        """Delete all cells tracked by tracker ID identifer."""
        ret = []
        while self.trackers[identifier]:
            x,y,v = self.trackers[identifier][0]
            ret.append((x,y,v,self.trackers_for_point(x,y,v)))
            self.remove(x,y)
            self.grid.remove(x,y)
        return ret

    def delete_except_for_tracker (self, identifier):
        tracks = self.trackers[identifier]
        removed = []
        for x in range(self.group_size):
            for y in range(self.group_size):
                val = self.grid._get_(x,y)
                if (val
                    and (x,y,val) not in tracks 
                    and not self.grid.virgin._get_(x,y)
                    ):
                    removed.append((x,y,val,self.trackers_for_point(x,y,val)))
                    self.remove(x,y)
                    self.grid.remove(x,y)
        return removed

    def add_tracker (self, x, y, tracker, val=None):
        self.__entries__[(x,y)].set_color(self.get_tracker_color(tracker))
        if not val: val = self.grid._get_(x,y)
        self.trackers[tracker].append((x,y,val))

    def remove_tracker (self, x, y, tracker, val=None):
        if not val: val = self.grid._get_(x,y)
        self.trackers[tracker].remove((x,y,val))
        

gobject.type_register(SudokuGridDisplay)

if __name__ == '__main__':
    #eg = EntryGrid()
    size = 4
    sg = SudokuGridDisplay(
        #grid=sudoku.fiendish_sudoku,
        #grid=sudoku.hard_hex_sudoku,
        group_size=size,
        )
    w = gtk.Window()
    vb = gtk.VBox()
    vb.add(sg)
    hint = gtk.Label()
    vb.add(hint)
    b = gtk.Button("New Sudoku")
    db = gtk.SpinButton()
    adj=db.get_adjustment()
    adj.lower=0
    adj.upper=25
    adj.step_increment=1
    adj.page_increment=10
    def new_sudoku (*args):
        v=db.get_value()
        sgen = sudoku.SudokuGenerator(group_size=size,
                                      clues=int((size*0.608)**2)
                                      )
        pp=sgen.generate_puzzles(25)
        if len(pp) > v: puz,d=pp[int(v)]
        else: puz,d = pp[-1]
        sg.blank_grid()
        sg.setup_grid(puz.grid,9)
    def test_filler_up (*args):
        sg.blank_grid()
        sg.doing_initial_setup=True
        sg.add(1,2,3)
        sg.add(2,3,4)
        sg.add(3,4,5)
        sg.add(4,5,6)
        sg.doing_initial_setup=False
    sg.label = hint
    b3 = gtk.Button('test')
    b3.connect('clicked',test_filler_up)
    b2 = gtk.Button('Blank')
    b2.connect('clicked',lambda *args: sg.blank_grid())
    b.connect('clicked',new_sudoku)
    w.add(vb)
    vb.add(db)
    vb.add(b)
    vb.add(b2)
    vb.add(b3)
    #sg.change_font_size(multiplier=3)
    hb = gtk.HBox()
    vb.add(hb)
    zib = gtk.Button(stock=gtk.STOCK_ZOOM_IN)
    zib.connect('clicked',lambda *args: sg.change_font_size(multiplier=1.1))
    zob = gtk.Button(stock=gtk.STOCK_ZOOM_OUT)
    zob.connect('clicked',lambda *args: sg.change_font_size(multiplier=0.9))
    hb.add(zib)
    hb.add(zob)
    w.show_all()
    w.connect('delete-event',lambda *args: gtk.main_quit())
    gtk.main()
