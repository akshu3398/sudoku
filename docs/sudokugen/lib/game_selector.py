import gtk, gobject, time
from gettext import gettext as _
from timer import format_time
from defaults import *

class GameSelector:

    def __init__ (self, sudoku_tracker):
        self.sudoku_tracker = sudoku_tracker

    def setup_dialog (self):
        self.glade = gtk.glade.XML(self.glade_file)
        self.dialog = self.glade.get_widget('dialog1')
        self.dialog.hide()
        self.tv = self.glade.get_widget('treeview1')        
        self.setup_tree()

    def setup_up_tree (self): raise NotImplementedError
    def get_puzzle (self): raise NotImplementedError
    
    def run_dialog (self):
        self.setup_dialog()
        self.dialog.show()
        ret = self.dialog.run()
        self.dialog.hide()
        if ret==gtk.RESPONSE_OK:
            return self.get_puzzle()
        else:
            return None

class NewGameSelector (GameSelector):
    glade_file = os.path.join(GLADE_DIR,'new_game.glade')
    difficulty = 0

    def setup_dialog (self):
        GameSelector.setup_dialog(self)
        self.dialog.set_default_response(gtk.RESPONSE_CANCEL)
        self.setup_hscale()

    def setup_hscale (self):
        self.hscale = self.glade.get_widget('hscale1')
        self.adj = self.hscale.get_adjustment()
        self.adj.set_value(self.difficulty)
        bounds = (0.0,0.9)
        real_bounds = self.sudoku_tracker.sudoku_maker.get_difficulty_bounds()
        if real_bounds[1]>bounds[1]: bounds[1]=real_bounds[1]
        if real_bounds[0]<bounds[0]: bounds[0]=real_bounds[0]
        self.adj.lower,self.adj.upper = bounds
        self.adj.step_increment = (bounds[1]-bounds[0])/20
        self.adj.page_increment = self.adj.step_increment*10

    def setup_tree (self):
        # puzzle / difficulty / diff value / name
        self.model = gtk.TreeStore(str, gobject.TYPE_PYOBJECT, str, str, float, str)
        for puzzobj in self.sudoku_tracker.list_new_puzzles():
            p,d = puzzobj
            if not self.sudoku_tracker.sudoku_maker.names.has_key(p):
                self.sudoku_tracker.sudoku_maker.names[p]=self.sudoku_tracker.sudoku_maker.get_puzzle_name(
                    _('Puzzle'))
            self.sudoku_tracker.sudoku_maker.names[p]
            itr = self.model.append(None,
                                    [p, # puzzle
                                     d, # difficulty                                     
                                     d.value_string(),
                                     None,
                                     d.value,
                                     self.sudoku_tracker.sudoku_maker.names[p]
                                     ])
            # now we enumerate some details...
            for label,prop in [('Squares instantly fillable by filling: ',
                                d.instant_fill_fillable),
                               ('Squares instantly fillable by elimination: ',
                                d.instant_elimination_fillable),
                               ('Number of guesses necessary to solve: ',
                                len(d.guesses)),
                               ]:
                self.model.append(itr, [None,None,str(prop),None,0,label])
        col0 = gtk.TreeViewColumn('Name',gtk.CellRendererText(),text=5)
        col0.set_sort_column_id(5)
        col1 = gtk.TreeViewColumn("Difficulty",gtk.CellRendererText(),text=2)
        col1.set_sort_column_id(4)
        #col2 = gtk.TreeViewColumn("Detail",gtk.CellRendererText(),text=3)
        #col2.set_sort_column_id(4)
        self.tv.append_column(col0)
        self.tv.append_column(col1)
        #self.tv.append_column(col2)
        self.tv.set_model(self.model)
        self.tv.get_selection().connect('changed',self.selection_changed_cb)

    def get_puzzle (self):
        diff = self.hscale.get_value()
        return self.sudoku_tracker.get_new_puzzle(diff)
        
        
    def selection_changed_cb (self, selection):
        mod,itr = selection.get_selected()
        while mod.iter_parent(itr):
            itr = mod.iter_parent(itr)
        difficulty = mod.get_value(itr,4)
        self.adj.set_value(difficulty)


class OldGameSelector (GameSelector):
    glade_file = os.path.join(GLADE_DIR,'open_game.glade')

    def setup_tree (self):
        rend = gtk.CellRendererText()
        col0 = gtk.TreeViewColumn('Name',rend,text=8)
        col0.set_sort_column_id(8)
        self.tv.append_column(col0)
        col1=gtk.TreeViewColumn("Difficulty",rend,text=2)
        col1.set_sort_column_id(3)
        self.tv.append_column(col1)
        self.tv.insert_column_with_data_func(1, # position
                                             _('Started'),# title
                                             gtk.CellRendererText(), # renderer,
                                             self.cell_data_func,
                                             4) # column
        self.tv.get_column(1).set_sort_column_id(4)
        self.tv.insert_column_with_data_func(2, # position
                                             _('Last Played'),# title
                                             gtk.CellRendererText(), # renderer,
                                             self.cell_data_func,
                                             5) # column
        self.tv.get_column(2).set_sort_column_id(5)
        col2 = gtk.TreeViewColumn("Status",rend,text=6)
        self.tv.append_column(
            col2
            )
        col2.set_sort_column_id(7)
        self.setup_model()
        self.tv.set_model(self.model)
        self.tv.get_selection().connect('changed',self.selection_changed_cb)
        self.selection_changed_cb(self.tv.get_selection())

    def selection_changed_cb (self, selection):
        self.dialog.set_response_sensitive(gtk.RESPONSE_OK,
                                           selection.get_selected() and True or False)
                              
    def setup_model (self):
        # game, jar, difficulty, diffval, start date, finish date, status, status val, names
        self.model = gtk.TreeStore(str, gobject.TYPE_PYOBJECT, str, float,
                                   float, float, str, float, str)
        for game,jar in self.sudoku_tracker.playing.items():
            diff = self.sudoku_tracker.get_difficulty(game)
            start_time = jar['timer.__absolute_start_time__']
            finish_time = jar.get('saved_at',time.time())
            status = "Played for %s"%format_time(jar['timer.tot_time'],round_at=2)
            if not self.sudoku_tracker.sudoku_maker.names.has_key(game):
                self.sudoku_tracker.sudoku_maker.names[game]=self.sudoku_tracker.sudoku_maker.get_puzzle_name(
                    _('Puzzle')
                    )
            name = self.sudoku_tracker.sudoku_maker.names[game]
            self.model.append(None,
                              [game,
                               jar,
                               diff and diff.value_string() or None,
                               diff and diff.value or 0,
                               start_time,
                               finish_time,
                               status,
                               jar['timer.tot_time'],
                               name
                               ])

    def cell_data_func (self, tree_column, cell, model, titer, data_col):
        val = model.get_value(titer,data_col)
        curtime = time.time()
        # within 18 hours, return in form 4 hours 23 minutes ago or some such
        if curtime - val < 18 * 60 * 60:
            cell.set_property('text',
                              "%s ago"%format_time(curtime-val,round_at=1))
            return
        tupl=time.localtime(val)
        if curtime - val <  7 * 24 * 60 * 60:
            cell.set_property('text',
                              time.strftime('%A %T',tupl))
            return
        else:
            cell.set_property('text',
                              time.strftime('%D %T',tupl))
            return

    def get_puzzle (self):
        mod,itr = self.tv.get_selection().get_selected()
        jar = mod.get_value(itr,1)
        return jar

    
    
class HighScores (GameSelector):
    glade_file = os.path.join(GLADE_DIR,'high_scores.glade')

    highlight_newest = False
    
    def setup_tree (self):
        self.setup_treemodel()
        rend = gtk.CellRendererText()
        rend.connect('edited',self.player_edited_cb)
        col = gtk.TreeViewColumn(_('Player'),rend,text=0,
                                 editable=6,
                                 weight=6)
        col.set_sort_column_id(0)
        self.tv.append_column(col)
        col2 = gtk.TreeViewColumn(_('Score'),rend,text=1)
        col2.set_sort_column_id(2)
        self.tv.append_column(col2)
        col3 = gtk.TreeViewColumn(_('Date'),rend,text=3)
        col3.set_sort_column_id(4)
        self.tv.append_column(col3)
        self.tv.set_model(self.model)

    def run_dialog (self):
        self.setup_dialog()
        self.dialog.show()
        # we have to do our highlighting *after* we're shown
        self.highlight()
        ret = self.dialog.run()
        self.dialog.hide()
        if ret==gtk.RESPONSE_OK:
            return self.get_puzzle()

    def setup_treemodel (self):
        # Name, Score, Score (float), Date, Date(float), Puzzle (str), Highlighted, Finisher (PYOBJ)
        self.model = gtk.TreeStore(str,str, float, str, float,str,int,gobject.TYPE_PYOBJECT)
        most_recent = (None,None)
        for game,finishers in self.sudoku_tracker.finished.items():
            for finisher in finishers:
                score=self.calculate_score(game,finisher)
                finish_time = finisher['finish_time']                
                itr=self.model.append(None,
                                  [finisher['player'],
                                   str(score),
                                   score,
                                   time.strftime("%A",time.localtime(finisher['finish_time'])),
                                   finish_time,
                                   game,
                                   0,
                                   finisher
                                   ])
                if finish_time > most_recent[0]: most_recent = (finish_time,itr)
                for label,detail in [(_('Hints'),'hints'),
                                     (_('Warnings about unfillable squares'),
                                      'impossible_hints'),
                                     (_('Auto-fills'),'auto_fills'),
                                     (_('Finished in'),format_time(finisher['time']))]:
                    if finisher.has_key(detail):
                        detail = finisher[detail]
                    self.model.append(itr,
                                      [label, detail, 0, None, 0,None,0,None])
        self.model.set_sort_column_id(2,gtk.SORT_DESCENDING)
        if self.highlight_newest:
            self.model.set_value(itr,6,1)
            self.highlight_path = self.model.get_path(itr)

    def highlight (self):
        if hasattr(self,'highlight_path'):
            self.glade.get_widget('replay').hide()
            self.glade.get_widget('you_win_label').show()
            self.image = self.glade.get_widget('image')
            self.image.set_from_file(os.path.join(IMAGE_DIR,'Winner.svg'))
            self.image.show()
            self.tv.expand_row(self.highlight_path,True)
            self.tv.set_cursor(self.highlight_path,
                               focus_column=self.tv.get_column(0),
                               start_editing=True)
            self.tv.grab_focus()
            

    def calculate_score (self, puzzl, finisher):
        diff = self.sudoku_tracker.get_difficulty(puzzl)
        time_bonus = (60*60*3.5/(finisher['auto_fills']+1))/finisher['time']
        if time_bonus < 1: time_bonus = 1
        score = diff.value * 100 * time_bonus
        score = score - finisher['auto_fills']*10
        score = score - finisher['impossible_hints']*3
        score = score - finisher['hints']*3
        return score

    def player_edited_cb (self, renderer, path_string, text):
        self.model[path_string][0]=text
        self.model[path_string][7]['player']=text
        
    def get_puzzle (self):
        mod,itr = self.tv.get_selection().get_selected()
        while mod.iter_parent(itr):
            itr = mod.iter_parent(itr)
        return mod.get_value(itr,5)

if __name__ == '__main__':
    IMAGE_DIR='/usr/local/share/gnome-sudoku/'
    from gnome_sudoku import sudoku_maker
    st = sudoku_maker.SudokuTracker(sudoku_maker.SudokuMaker(pickle_to='/tmp/foo'))
    hs=HighScores(st)
    hs.highlight_newest=True
    hs.run_dialog()
    st.save()
