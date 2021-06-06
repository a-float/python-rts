class StateMachine(object):
    """
    A generic state machine.
    """
    def __init__(self):
        self.done = False
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.now = None

    def setup_states(self, state_dict, start_state):
        """
        Given a dictionary of states and a state to start in,
        creates the self.state_dict.
        """
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.now, None)

    def update(self, keys, now):
        """
        Checks if a state is done or has called for a game quit.
        State is flipped if necessary and State.update is called.
        """
        self.now = now
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(keys, now)

    def draw(self, surface, interpolate):
        self.state.draw(surface, interpolate)

    def flip_state(self):
        """
        When a State changes to done necessary startup and cleanup functions
        are called and the current State is changed.
        """
        print('flipping from {} to {}'.format(self.state_name, self.state.next))
        persist = self.state.cleanup()
        previous, self.state_name = self.state_name, self.state.next
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.now, persist)
        self.state.previous = previous

    def get_event(self, event):
        """
        Pass events down to current State.
        """
        self.state.get_event(event)


class State(object):
    """
    This is a prototype class for States. All states should inherit from it.
    No direct instances of this class should be created. get_event and update
    must be overloaded in the child class. The startup and cleanup methods
    need to be overloaded when there is data that must persist between States.
    """
    def __init__(self):
        self.start_time = 0.0
        self.now = 0.0
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.persist = {}
        self.dirty = True

    def get_event(self, event):
        """
        Processes events that were passed from the main event loop.
        Must be overloaded in children.
        """
        pass

    def startup(self, now, persistent):
        """
        Add variables passed in persistent to the proper attributes and
        set the start time of the State to the current time.
        """
        self.persist = persistent
        self.start_time = now

    def cleanup(self):
        """
        Add variables that should persist to the self.persist dictionary.
        Then reset State.done to False.
        """
        self.dirty = True
        self.done = False
        return self.persist

    def update(self, keys, now):
        """Update function for state.  Must be overloaded in children."""
        pass
