from app import webapp_db, socketio_handler
from app.models import GuestUser
from chess import Board, BLACK, WHITE
from chess.engine import Limit, SimpleEngine, Mate, MateGiven
from gevent import Greenlet
from math import exp
from constants import MAX_VOLUME, STOCKFISH_PATH, VOLUME_MIDPOINT, VOLUME_STEEPNESS



class Game:
    def __init__(self, handler, first_user_id, second_user_id):
        print("Starting game betwen {} and {}".format(first_user_id, second_user_id))

        # administrative stuff
        self.game_handler = handler
        self.game_id = first_user_id # ASSUMING THAT users are only playing one game at a time, we can safely use the unique user ID as the unique game ID
        self.game_room = "game {}".format(self.game_id)
        self.board = Board()

        # user stuff
        self.white_user_id = first_user_id
        self.white_user = GuestUser.query.filter_by(id=first_user_id).first()
        self.black_user_id = second_user_id
        self.black_user = GuestUser.query.filter_by(id=second_user_id).first()
        self.__spectators = {}

        # engine stuff
        self.engine = SimpleEngine.popen_uci(STOCKFISH_PATH) # open stockfish synchronously, since it should be ready before the players are
        self.score = 0

        # post-game stuff
        self.rematch_requested = {self.white_user_id: False, self.black_user_id: False}
        self.game_is_over = False

        self.__notify_users()

    def add_spectator(self, user_id):
        if user_id not in self.__spectators:
            self.__spectators[user_id] = GuestUser.query.filter_by(id=user_id).first()

    def get_san(self):
        temp_board = Board()
        return temp_board.variation_san(self.board.move_stack) # it exists trust me

    def player_can_move(self, player_id):
        white_and_can_move = (player_id == self.white_user_id) and (self.board.turn == WHITE)
        black_and_can_move = (player_id == self.black_user_id) and (self.board.turn == BLACK)
        return white_and_can_move or black_and_can_move

    def try_move(self, player_id, move):
        if self.player_can_move(player_id):
            try:
                self.board.push_uci(move)
                socketio_handler.emit("update board", move, room=self.game_room) # confirm the move to the players before doing stockfish analysis, to avoid lag

                if self.board.is_game_over(): # if this move ends the game...
                    self.game_over() # clean up and then delete this game
                else:
                    Greenlet.spawn(self.__update_music_volume, player_id) # run the music update in another thread, since stockfish takes a while and we don't want to block move confirmations
            except ValueError: # valueerror means move was illegal
                pass # but it happens often enough that it's not worth commenting on

    def __update_music_volume(self, player_id):
        new_pov_score = self.engine.analyse(self.board, Limit(time=0.5))["score"]

        new_white_score = new_pov_score.white()
        if type(new_white_score) is Mate:
            new_white_score = 200 # change white's volume to a flat 200 if he can be mated
        elif type(new_white_score) is MateGiven:
            new_white_score = -200 # change black's volume to a flat 200 if he can be mated
        else:
            new_white_score = int(new_white_score.cp / 10) # divide by tens to convert from centipawns to pawns
        white_score_change = new_white_score - self.score

        new_black_score = -new_white_score
        black_score_change = -white_score_change

        self.score = new_white_score
        new_white_volume = self.__sigmoid(min(0, new_white_score, white_score_change), MAX_VOLUME, VOLUME_MIDPOINT, VOLUME_STEEPNESS) # set the volume to a logistic function, so it climbs steeply at first but then maxes out later
        new_black_volume = self.__sigmoid(min(0, new_black_score, black_score_change), MAX_VOLUME, VOLUME_MIDPOINT, VOLUME_STEEPNESS)

        if player_id == self.white_user_id:
            socketio_handler.emit("music volume", new_white_volume, room=self.white_user.websocket_id) # change the player's music depending on their move...
            socketio_handler.emit("music volume", max(new_white_volume, new_black_volume), room=self.game_room, skip_sid=[self.white_user.websocket_id, self.black_user.websocket_id])  # ...and the spectator's music based on whose position is shittier
        else:
            socketio_handler.emit("music volume", new_black_volume, room=self.black_user.websocket_id) # change the player's music depending on their move...
            socketio_handler.emit("music volume", max(new_white_volume, new_black_volume), room=self.game_room, skip_sid=[self.white_user.websocket_id, self.black_user.websocket_id])  # ...and the spectator's music based on whose position is shittier

    def game_over(self, user_left=False):
        socketio_handler.emit("game over", room=self.game_room) # tell all the people in the room that the game is over

        self.black_user.current_game = 0 # mark both participants as not being in game in the database
        self.white_user.current_game = 0
        for spectator_id, spectator in self.__spectators: # remove all spectators from this game, allowing them to join other games...
            if spectator.current_game == self.game_id: # but only if they're still spectating this game
                spectator.current_game = 0
        webapp_db.session.commit() # push those commits to the database & expire the user objects

        self.game_is_over = True
        if user_left: # if this game was ended by one of the players leaving:
            socketio_handler.emit("no rematch", room=self.game_room) # tell everyone there isn't going to be a rematch
            self.game_handler.remove_game(self.game_id) # and kill the game to free the other player
            # self.game_handler.remove_game(self.game_id) # remove the game from the list (allowing both players to rejoin the queue)

    def __notify_users(self):
        socketio_handler.server.leave_room(self.white_user.websocket_id, self.white_user.current_game) # remove both players from their old game room,
        socketio_handler.server.leave_room(self.black_user.websocket_id, self.black_user.current_game) # so they don't get moves from both games at once

        socketio_handler.server.enter_room(self.white_user.websocket_id, self.game_room) # put both players in the game room,
        socketio_handler.server.enter_room(self.black_user.websocket_id, self.game_room) # so they can see announced moves and other messages

        socketio_handler.emit("game start", self.__generate_game_data("white"), room=self.white_user.websocket_id) # tell the white player they're playing white...
        socketio_handler.emit("game start", self.__generate_game_data("black"), room=self.black_user.websocket_id) # ...and the black player they're playing black

    def __generate_game_data(self, color):
        return {
            "color": color,
            "opponent": self.white_user.username if color == "black" else self.black_user.username,
            "opponentAvatarUrl": self.white_user.avatar_url if color == "black" else self.black_user.avatar_url
        }

    @staticmethod
    def __sigmoid(value, max_value, midpoint, steepness):
        exponent = steepness * (value - midpoint) # positive steepness so volume increases as the degree they fuck up increases
        exponential = exp(exponent)
        sig_value = max_value/(1 + exponential)
        return 0.25 + sig_value
