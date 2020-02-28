import pickle

SAVE_ATTRIBUTES = [('gsd.hints'),
                   ('gsd.impossible_hints'),
                   ('gsd.auto_fills'),
                   ('timer.__absolute_start_time__'),
                   ('timer.tot_time'),
                   ]

def super_getattr (obj, attr):
    """getattr, following the dots."""
    attrs=attr.split('.')
    for a in attrs:
        obj = getattr(obj,a)
    return obj

def super_setattr (obj, attr, val):
    """setattr, following the dots."""
    attrs = attr.split('.')
    if len(attrs) > 1:
        sub_attrs = attrs[0:-1]
        attr = attrs[-1]
        for a in sub_attrs:
            obj = getattr(obj,a)
    setattr(obj,attr,val)

def jar_game (ui):
    jar = {} # what we will pickle
    #jar['undo_history']=ui.history
    jar['game']=ui.gsd.grid.to_string()
    jar['trackers']=ui.gsd.trackers
    jar['tracking']=ui.gsd.__trackers_tracking__
    for attr in SAVE_ATTRIBUTES:
        jar[attr]=super_getattr(ui,attr)
    #print 'saving ',jar
    return jar

def open_game (ui, jar):
    #ui.history = jar['undo_history']
    ui.gsd.load_game(jar['game'])
    # this is a bit easily breakable... we take advantage of the fact
    # that we create tracker IDs sequentially and that {}.items()
    # sorts by keys by default
    for tracker,tracked in jar['trackers'].items():
        # add 1 tracker per existing tracker...
        # print 'Tracker ',tracker,' adding tracker!'
        ui.tracker_ui.add_tracker()
        ui.tracker_ui.show()
        for x,y,val in tracked:
            #print 'Adding tracker ',x,y,val,tracker
            ui.gsd.add_tracker(x,y,tracker,val=val)
    for tracker,tracking in jar['tracking'].items():
        if tracking:
            #print tracker,' is tracking!'
            ui.tracker_ui.select_tracker(tracker)
    for attr in SAVE_ATTRIBUTES:
        super_setattr(ui,attr,jar.get(attr,None))
        
def pickle_game (ui, target):
    close_me = False
    if type(target)==str:
        target = file(target,'w')
        close_me = True
    to_dump = jar_game(ui)
    #print 'Dumping ',to_dump,' to ',target
    pickle.dump(to_dump,target)
    if close_me: target.close()
    
def unpickle_game (ui, target):
    close_me = False
    if type(target)==str:
        target = file(target, 'r')
        close_me = True
    open_game(ui,pickle.load(target))
    if close_me: target.close()
