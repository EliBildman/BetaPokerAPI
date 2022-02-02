from venv import create
from flask import Flask, request, jsonify, Response
app = Flask(__name__)
from game import get_actor, get_beta_move, get_available_actions, create_state, do_nature_event

def build_response(data):
    # print(data)
    res = jsonify(data)
    res.headers.add('Access-Control-Allow-Origin', '*')
    res.headers.add('Content-Type', 'application/json')
    return res

@app.route('/get-actor')
def actor():
    gs = create_state(request.args.get('hist'))
    return build_response(get_actor(gs))

@app.route("/get-beta-action")
def beta_action():
    gs = create_state(request.args.get('hist'))
    player_no = 0 if request.args.get('agent_player') == 'p1' else 1
    return build_response(get_beta_move(gs, player_no))

@app.route("/get-available-actions")
def available_actions():
    gs = create_state(request.args.get('hist'))
    return build_response(get_available_actions(gs))

@app.route("/get-bets")
def bets():
    gs = create_state(request.args.get('hist'))
    bs = [(p.bet + gs.game.pot / 2) for p in gs.game.players]
    return build_response(bs)

@app.route("/get-nature-action")
def nature_action():
    gs = create_state(request.args.get('hist'))
    return build_response(do_nature_event(gs))

@app.route("/is-terminal")
def is_terminal():
    gs = create_state(request.args.get('hist'))
    term = gs.game.is_terminal()
    takes = gs.takes
    return build_response((term, takes))