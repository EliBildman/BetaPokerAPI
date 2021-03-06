from copy import deepcopy

class Event:

    def __init__(self, player, action, data = None):
        self.player = player
        self.action = action
        self.data = deepcopy(data)

    def __str__(self):
        return f"{self.player} {self.action}" + (f' {self.data}' if self.data else '')

class GameState:
    def __init__(self, game):
        self.his = []
        self.street_i = -1
        self.street = ''
        self.game = game
        self.takes = None

    def itt_street(self):
        streets = ['preflop', 'flop', 'turn', 'river']
        self.street_i += 1
        self.street = streets[self.street_i]

    def add_event(self, event):
        self.his.append(event)


