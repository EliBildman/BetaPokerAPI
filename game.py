from re import S
from tty import CFLAG
from representation import GameState, Event
from pokerface import FixedLimitTexasHoldEm, Stakes, parse_cards
from cfr_agent import CFRAgent
from pickle import load

game_config = {
    'blinds': [0.5, 1],
    'starting_stacks': [100, 100]
}

cfr_config = {
    'wrs': [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
}

strat_file = './strats/strat_50.dic'
with open(strat_file, 'rb') as f:
    strat = load(f)

agent = CFRAgent(strat, cfr_config)

# hist ex: 'N-DP-As5h4c8d_P0-R_P1-C_N-DB-Ac3h7h'
def create_state(history_str):
    stakes = Stakes(0, game_config['blinds'])
    starting_stacks = game_config['starting_stacks']

    game = FixedLimitTexasHoldEm(stakes, starting_stacks)

    p1, p2 = game.players
    nature = game.nature

    gamestate = GameState(game)

    events = history_str.split('_')
    for event in events:

        info = event.split('-')
        actor = info[0]

        # print(p1.is_actor(), p2.is_actor(), nature.is_actor())

        if actor == 'N':

            deal = info[1]
            if deal == 'DP':
                if not nature.can_deal_hole():
                    raise Exception('Cannot deal hole') #deal with bad input issues

                p1_cards = parse_cards(info[2][:4])
                p2_cards = parse_cards(info[2][4:])

                nature.deal_hole(p1_cards)
                gamestate.add_event(Event('nature', 'deal_p1', p1.hole))

                nature.deal_hole(p2_cards)
                gamestate.add_event(Event('nature', 'deal_p2', p2.hole))

            if deal == 'DB':
                if not nature.can_deal_board():
                    raise Exception('Cannot deal board')
                
                cards = parse_cards(info[2])
                nature.deal_board(cards)
                gamestate.add_event(Event('nature', "deal_board", game.board))

            gamestate.itt_street()

        elif actor == 'P0' or actor == 'P1':
            
            player, p_str = (p1, 'p1') if actor == 'P0' else (p2, 'p2')
            action = info[1]

            if action == 'F':
                if not player.can_fold():
                    raise Exception('Cannot fold')

                player.fold()
                gamestate.add_event(Event(p_str, 'fold'))

            elif action == 'C':
                if not player.can_check_call():
                    raise Exception('Cannot check/call')

                player.check_call()
                gamestate.add_event(Event(p_str, 'call'))

            elif action == 'R':
                if not player.can_bet_raise():
                    raise Exception('Cannot bet/raise')

                player.bet_raise()
                gamestate.add_event(Event(p_str, 'raise'))

    #check for showdown
    if p1.can_showdown():
        p1.showdown()
    
    if p2.can_showdown():
        p2.showdown()

    return gamestate

def get_actor(gamestate):
    p1, p2 = gamestate.game.players
    nature = gamestate.game.nature

    if p1.is_actor():
        return 'p1'
    elif p2.is_actor():
        return 'p2'
    elif nature.is_actor():
        return 'nature'
    else:
        raise Exception('what happened here')

def get_available_actions(gamestate):
    p1, p2 = gamestate.game.players
    if p1.is_actor():
        player = p1
    elif p2.is_actor():
        player = p2
    else:
        raise Exception('player not actor')
    
    actions = []

    if player.can_fold():
        actions.append('fold')
    if player.can_check_call():
        actions.append('call')
    if player.can_bet_raise():
        actions.append('raise')

    return actions

#returns {player_holes: [], board: []}
def do_nature_event(gamestate):

    nature = gamestate.game.nature
    p1, p2 = gamestate.game.players

    if nature.can_deal_hole(): #do both
        nature.deal_hole()
        nature.deal_hole()

    elif nature.can_deal_board():
        nature.deal_board()

    else:
        raise Exception('nature not actor')

    p1_hole = [repr(c) for c in p1.hole]
    p2_hole = [repr(c) for c in p2.hole]
    board = [repr(c) for c in gamestate.game.board]

    return {'player_holes': [p1_hole, p2_hole], 'board': board}


def get_beta_move(gamestate, player_no):
    p = gamestate.game.players[player_no]
    return agent.algo(p, gamestate)


# g = create_state('N-DP-As2h3s8d_P1-C')
# for h in g.his:
#     print(h)
# print(get_beta_move(g, 0))
