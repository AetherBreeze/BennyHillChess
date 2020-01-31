from app.models import GuestUser
from flask_socketio import close_room
from game import Game
from random import seed, random
from os import urandom



class GameHandler:
    def __init__(self):
        self.__recieved_challenges = {} # keep track of all recieved and issued challenges for each player, so that
        self.__issued_challenges = {} # all of each can be removed quickly when the player is placed in a match
        self.__master_games_list = {}
        self.__queue = []

        seed(urandom(1)[0]) # initialize with a random seed between 0 and 255

    def get_match_by_id(self, match_id):
        return self.__master_games_list.get(match_id)

    def get_player_game_id(self, user_id):
        for _, game in self.__master_games_list.items():
            if user_id == game.white_user_id or user_id == game.black_user_id:
                return game.game_id

        return None

    def start_new_game(self, first_user_id, second_user_id):
        if random() > 0.5: # decide which player is white (i.e. which is the first argument to Game())
            user_id_list = [first_user_id, second_user_id]
        else:
            user_id_list = [second_user_id, first_user_id]

        for user_id in user_id_list: # make sure neither user is already in game
            for _, game in self.__master_games_list.items():
                print("Game found: {} vs {}".format(game.white_user_id, game.black_user_id))
                if user_id == game.white_user_id or user_id == game.black_user_id:
                    print("[ERROR] Cannot create a new game for user with ID {} because they are already in a game!".format(user_id))
                    return False
        self.__master_games_list[first_user_id] = Game(self, first_user_id, second_user_id)
        return True

    """def queue_up_or_start_game(self, user_id):
        if len(self.__queue) == 0: # if no one is in the queue, place this user in it
            self.__queue.append(user_id)
            print("Added user {} to queue".format(user_id))
            print("Queue: {}".format(self.__queue))
        elif user_id in self.__queue: # if they're already in queue, don't let them join again
            print("[WARNING] User {} attempted to join queue while already in it!".format(user_id))
        else: # otherwise, match up the new user with the oldest one in the queue, then remove the matched player from the queue
            self.start_new_game(self.__queue[0], user_id)
            print("Started game between users {} and {}".format(self.__queue[0], user_id))
            self.__queue = self.__queue[1:]"""

    def remove_user_from_queue(self, user_id):
        try:
            self.__queue.remove(user_id)
        except ValueError: # thrown when the user_id wasn't in queue in the first place
            pass # happens often enough (i.e. on disconnect) and is inconsequential enough that we don't log it

    def remove_game(self, game_id):
        try:
            close_room(self.__master_games_list[game_id].game_room)  # stop sending updates to everyone in the room
            del self.__master_games_list[game_id]
        except KeyError:
            print("[ERROR] Attempted to remove the game with ID {} when no such game exists.".format(game_id))

    def rematch(self, game_id):
        wuid = self.__master_games_list[game_id].white_user_id
        buid = self.__master_games_list[game_id].black_user_id

        self.remove_game(game_id)
        self.start_new_game(buid, wuid) # switch up so the former black player is now playing white

    def x_challenges_y(self, x_player_id, y_player_id): # return value indicates whether to send a challenge emit() to or not
        if self.get_player_game_id(x_player_id) or self.get_player_game_id(y_player_id):
            print("[WARNING] User {} attempted to challenge user {} while one of them was in game!".format(x_player_id, y_player_id))
            return False

        if x_player_id in self.__issued_challenges:
            self.__issued_challenges[x_player_id].append(y_player_id)
        else:
            self.__issued_challenges[x_player_id] = [y_player_id]

        if y_player_id in self.__recieved_challenges:
            self.__recieved_challenges[y_player_id].append(x_player_id)
            return False
        else:
            self.__recieved_challenges[y_player_id] = [x_player_id]
            return True

    def x_accepts_challenge(self, x_player_id):
        try:
            challenger_id = self.__recieved_challenges[x_player_id][0] # default to accepting the oldest non-rejected challenge
        except IndexError:
            print("[WARNING] User {} accepted a challenge without having one (????)")
            return False
        return self.x_accept_y_challenge(x_player_id, challenger_id)

    def x_declines_challenge(self, x_player_id):
        x_challenges = self.__recieved_challenges.get(x_player_id)
        if x_challenges is None:
            print("[WARNING] User {} declined a challenge without having one (????)")
            return False

        next_challenger = None
        challenger_id = self.__recieved_challenges[x_player_id][0] # default to declining the oldest non-rejected challenge

        if len(self.__recieved_challenges[x_player_id]) == 1:
            del self.__recieved_challenges[x_player_id]
        else:
            self.__recieved_challenges[x_player_id] = self.__recieved_challenges[x_player_id][1:]
            next_challenger = self.__recieved_challenges[x_player_id][0] # tell routes.py to send the next challenge

        if len(self.__issued_challenges[challenger_id]) == 1:
            del self.__issued_challenges[challenger_id]
        else:
            self.__issued_challenges[challenger_id].remove(x_player_id)

        return next_challenger

    def x_accept_y_challenge(self, x_player_id, y_player_id):
        if self.get_player_game_id(x_player_id) or self.get_player_game_id(y_player_id): # if either player is in game, they can't accept challenges
            print("[WARNING] User {} accepted user {}'s challenge while one of them was in game!".format(x_player_id, y_player_id))
            return False
        elif x_player_id not in self.__recieved_challenges: # if x has no challenges, he obviously can't accept challenges
            print("User {} somehow accepted a challenge from user {} without having any challenges (????)".format(x_player_id, y_player_id))
            return False
        elif y_player_id not in self.__recieved_challenges[x_player_id]: # if x has no challenges from y, he obviously can't accept y's challenge
            print("[WARNING] User {} accepted a challenge from user {} without having a challenge from them (????)".format(x_player_id, y_player_id))
            return False
        elif y_player_id in self.__recieved_challenges[x_player_id]: # if x still has challenges pending and this is one of them
            self.remove_all_challenges(x_player_id)
            self.remove_all_challenges(y_player_id)

            x_online = GuestUser.query.filter_by(id=x_player_id).first().online
            y_online = GuestUser.query.filter_by(id=y_player_id).first().online
            if x_online and y_online:
                self.start_new_game(x_player_id, y_player_id) # KNOWN RACE CONDITION: if x or y logs off during this function, the other will be stuck in the game until they refresh
                return True
            else:
                print("[ERROR] User {} logged off after user {} accepted their challenge!".format(x_player_id if x_online else y_player_id, y_player_id if y_online else x_player_id))
                return False

    def remove_all_challenges(self, player_id):
        if player_id in self.__issued_challenges: # unchallenge everyone that a player's challenged once that player gets into game
            for challenged_player in self.__issued_challenges[player_id]:
                print("Removing challenge to user {} from user {}".format(challenged_player, player_id))
                self.__recieved_challenges[challenged_player].remove(player_id)
            del self.__issued_challenges[player_id]

        if player_id in self.__recieved_challenges:
            for challenger in self.__recieved_challenges[player_id]:
                self.__issued_challenges[challenger].remove(player_id)
            del self.__recieved_challenges[player_id]
