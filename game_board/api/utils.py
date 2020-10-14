from game_board import config
from game_board import rules
from game_board.database import game_board_db as db
from game_board.avl import avl_handler as avl

from datetime import datetime
from bson import json_util, ObjectId

import random
import uuid
import json


def create_board_db(new_board):
    '''
    Create a new board in the database.
    :param new_board:
    :return dict:
    '''
    error = False

    try:
        game_id = db.create_game(new_board)
        game_id = json.loads(json_util.dumps(game_id))

    except Exception as e:
        error = True
        return {'error': error, 'reason': str(e)}

    return {'error': error, 'game_id': game_id}


def update_board_db(board):
    '''
    Update the game board in the database.

    :param board:
    :return dict:
    '''
    error = False
    try:
        # Game ended
        if board['graph']['root_node'] == board['graph']['gold_node']:
            db.remove_game(board['game_id'])
            board['end_game'] = True

        # Game continues
        else:
            db_response = db.update_game(board['game_id'], board)

    except Exception as e:
        error = True
        return {'error': error, 'reason': str(e)}

    return {'error': error, 'game_board': board}


def load_board_db(game_id):
    '''
    Load a game board state from database.

    :string game_id: id of the game board
    :return: game board dict or error
    '''
    error = False

    try:
        # game_board = mock_db.read_game('game_id1234')
        game_board = db.read_game(str(game_id))
        if game_board == "nah bro idk about it":
            error = True
            return {'error': error, 'reason':'Game Not Found!'}

        # Serialize
        game_board = json.loads(json_util.dumps(game_board))

        # Remove the database entry ID
        del game_board['_id']

    except Exception as e:
        error = True
        return {'error':error, 'reason':str(e)}

    return {'error':error, 'game_board':game_board}


def new_board(difficulty, player_ids, data_structures):
    '''
    Create new board dictionary.

    :string difficulty: difficulty of the game
    :list player_ids: list of player ids
    :list data_structures: list of data structures
    :string online: multiplater/online
    :return: game board dict
    '''

    # if it is an AVL
    if data_structures[0] == 'AVL':
        graph = avl.avlNew(config.HEIGHT[str(difficulty)], config.POINTS[str(difficulty)]['max'])
    # Currently only gives AVL
    else:
        graph = avl.avlNew(config.HEIGHT[str(difficulty)], config.POINTS[str(difficulty)])

    board = {
        'game_id': str(uuid.uuid1()),
        'graph': graph,
        'player_ids': player_ids,
        'player_names': [''],
        'player_points': {str(id): 0 for id in player_ids},
        'turn': random.choice(player_ids),
        'cards': distribute_cards(player_ids,
                                  list(graph['node_points'].keys()),
                                  data_structures[0],
                                  difficulty,
                                  graph['gold_node']),
        'difficulty': difficulty,
        'num_players': len(player_ids),
        'online': False,
        'curr_data_structure': data_structures[0],
        # 'selected_data_structures': data_structures,
        # 'timed_game': False,
        # 'seconds_until_next_ds': 60,
        'time_created': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'end_game': False
    }

    return board


def cheat_check(game_board, card=-1, rebalance=-1):
    '''
    Check if the action that is attempted is valid.

    :dict game_board:
    :string card:
    :string player_id:
    :bool rebalance:
    :return: True if invalid action, and string for reason.
    '''
    check = rules.general(game_board, card)
    if check['cheat']:
        return check

    if game_board['curr_data_structure'] == 'AVL':
        check = rules.AVL(game_board, rebalance)
        if check['cheat']:
            return check
    # No cheat detected
    return {'cheat': False}


def distribute_cards(player_ids, nodes, data_structure, difficulty, gold_node):
    '''
    Distribute cards to the users.

    :list player_ids: player IDs
    :list nodes: graph nodes
    :string data_structure: current data structure
    :int cards_per: how many cards per player
    :string difficulty: game difficulty. See config.py
    :return: dict of cards per player
    '''
    board_cards = dict()

    # Minimum and maximum possible node value
    min_point = config.POINTS[str(difficulty)]['min']
    max_point = config.POINTS[str(difficulty)]['max']
    # Card types for the DS
    card_types = config.CARDS[str(data_structure)]

    # Remove the golden node from node options
    nodes.remove(gold_node)

    # generate the deck of cards
    cards = list()
    for ii in range(len(player_ids) * config.CARDS_PER_PLAYER):
        # can not pick node dependent anymore
        if len(nodes) == 0:
            card_types = [action for action in card_types if "node#" not in action]

        # pick a card
        picked_card = random.choice(card_types)

        # node specific action
        if 'node#' in picked_card:
            node_choice = str(random.choice(nodes))
            nodes.remove(node_choice)
            cards.append(picked_card.replace('node#', node_choice))
        # point dependent action
        else:
            cards.append(picked_card.replace('#', str(random.randint(min_point, max_point))))

    # Shuffle the deck of cards
    random.shuffle(cards)

    # pick cards for each player
    for player in player_ids:
        # assign the cards to the player
        player_cards = list()
        for ii in range(config.CARDS_PER_PLAYER):
            player_cards.append(cards.pop())

        board_cards[str(player)] = player_cards

    return board_cards


def pick_a_card(game_board):
    '''
    Pick a new card.

    :dict game_board: game board state
    :return: string card
    '''
    # Minimum and maximum possible node value
    min_point = config.POINTS[str(game_board['difficulty'])]['min']
    max_point = config.POINTS[str(game_board['difficulty'])]['max']
    # Card types for the DS
    card_types = config.CARDS[str(game_board['curr_data_structure'])]

    nodes = list(game_board['graph']['node_points'].keys())
    nodes.remove(game_board['graph']['gold_node'])
    for player, hand in game_board['cards'].items():
        for curr_card in hand:
            # remove the node based action card from options
            if 'node' in curr_card:
                node = curr_card.split(' ')
                nodes.remove(node[1])

        # no available nodes left for the node based action cards
        if len(nodes) == 0:
            card_types = [action for action in card_types if "node#" not in action]
            break

    # Pick a card
    card = random.choice(card_types)

    # node specific action
    if 'node#' in card:
        card_ = card.replace('node#', str(random.choice(nodes)))
    # point dependent action
    else:
        card_ = card.replace('#', str(random.randint(min_point, max_point)))

    return card_