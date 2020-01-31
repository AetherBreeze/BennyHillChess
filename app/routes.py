from app import socketio_handler, application, webapp_db, master_game_handler
from app.models import GuestUser
from utils.database import sign_on_user, sign_off_user
from utils.users import add_guest_user
from flask import request, render_template, send_from_directory, session
from flask_socketio import emit


@application.route("/")
@application.route("/index.html")
def default():
    username_or_none = session.get("username")
    if username_or_none is None: # if this is a new session
        this_user = add_guest_user(session)
    else:
        this_user = GuestUser.query.filter_by(username=session["username"]).first()
        if not this_user or this_user.id != session["id"]: # if this account's been deleted from the database, or another user's taken the guest name,
            this_user = add_guest_user(session) # give the user a new account
        else:
            print("Existing user connected: {}".format(session["username"]))
    user_data = {"id": this_user.id, "username": this_user.username} # cache this user data so we can still pass it to render_template after commiting this_user back to the db

    all_users = GuestUser.query.filter_by(online=True)
    return render_template("index.html", user=user_data, all_users=[user for user in all_users if user.id != this_user.id]) # avoid double-adding the same player via this and emit("logged on")


# favicon server
@application.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico")

# simple util to serve images of chess pieces
@application.route("/img/<path:filename>")
def serve_piece_imgs(filename):
    return send_from_directory("static/img", filename)


# simple util to serve yakety sax
@application.route("/audio/<path:filename>")
def serve_music(filename):
    return send_from_directory("static/audio", filename)


# records user's WebSocket IDs when they first connect, so we can contact them individually
@socketio_handler.on("connect")
def sockio_on_connect():
    if session["id"] is not None:
        print("User {} connected".format(session["id"]))
        this_user = GuestUser.query.filter_by(id=session["id"]).first()
        sign_on_user(webapp_db, this_user, request.sid)

        user_data = {"id": this_user.id, "username": this_user.username} # cache this user data so we can still pass it to render_template after commiting this_user back to the db

        socketio_handler.emit("logged on", user_data, broadcast=True) # add this player to everyone else's online players list

        # master_game_handler.queue_up_or_start_game(session["id"]) # automatically queue up users when they connect (this is run here instead of in route "/", so people that get kicked when disconnecting from socketio are readded when they reconnect


# allows in-game clients to make moves on the server
@socketio_handler.on("make move")
def sockio_try_move(move):
    game_id = master_game_handler.get_player_game_id(session["id"])
    if game_id == 0:
        return

    game = master_game_handler.get_match_by_id(game_id)
    if game:
        game.try_move(session["id"], move)


# puts players back in the queue
@socketio_handler.on("join queue")
def sockio_join_queue():
    master_game_handler.queue_up_or_start_game(session["id"])


# passes a player's challenge onto its target
@socketio_handler.on("challenge")
def sockio_challenge(challenged_player_id):
    print("User {} challenged user {}".format(session["id"], challenged_player_id))
    if master_game_handler.x_challenges_y(session["id"], challenged_player_id): # if this returns true, y is available for challenge, so we can emit a challenge message to challenged_player_id
        challenged_user_socket = GuestUser.query.filter_by(id=challenged_player_id).first().websocket_id
        socketio_handler.emit("challenged by", {"id": session["id"], "username": session["username"]}, room=challenged_user_socket)


# accepts the oldest non-rejected challenge that a player has
@socketio_handler.on("challenge accepted")
def sockio_accept_challenge():
    master_game_handler.x_accepts_challenge(session["id"])


# declines the oldest non-rejected challenge that a player has
@socketio_handler.on("challenge declined")
def sockio_decline_challenge():
    next_challenger = master_game_handler.x_declines_challenge(session["id"]) # this returns the id of the next challenger of this player, or None if there isn't one
    if next_challenger is not None:
        challenged_user_socket = GuestUser.query.filter_by(id=session["id"]).first().websocket_id
        challenger = GuestUser.query.filter_by(id=session["id"]).first()
        socketio_handler.emit("challenged by", {"id": challenger.id, "username": challenger.username}, room=challenged_user_socket)


# Accepts or declines a spectate request
@socketio_handler.on("spectate")
def sockio_spectate_request(id_to_spectate):
    game_id_or_none = master_game_handler.get_player_game_id(id_to_spectate)
    if game_id_or_none is None:
        print("User {} attempted to spectate user {} while they weren't in game!".format(session["id"], id_to_spectate))
        emit("spectate failed")
    else:
        game = master_game_handler.get_match_by_id(game_id_or_none)
        this_user = GuestUser.query.filter_by(id=session["id"]).first()

        this_user.current_game = game_id_or_none # mark them as spectating this game, so we can make them leave the room when they leave the game/stop spectating

        emit("spectate confirmed", {
                "whiteName": game.white_user.username,
                "whiteAvatarUrl": game.white_user.avatar_url,
                "blackName": game.black_user.username,
                "blackAvatarUrl": game.black_user.avatar_url,
                "fen": game.board.fen(),
                "san": game.get_san()
        })  # if they're allowed to spectate, send them the current state of the game...
        socketio_handler.server.enter_room(this_user.websocket_id, game.game_room) # ...and allow them to recieve new moves


# Ends a game for good once one player leaves it
@socketio_handler.on("left game")
def sockio_left_game():
    try_game_id = master_game_handler.get_player_game_id(session["id"])
    if try_game_id is not None: # if the other player hasn't left already, and the game still exists
        game = master_game_handler.get_match_by_id(try_game_id)
        socketio_handler.emit("no rematch", room=game.game_room)
        master_game_handler.remove_game(try_game_id) # kill the game once and for all

# Starts a rematch if both players have requested it, notifies the other if only one has
@socketio_handler.on("rematch requested")
def sockio_rematch_requested():
    try_game_id = master_game_handler.get_player_game_id(session["id"])
    if try_game_id is None:
        socketio_handler.emit("no rematch", room=GuestUser.query.filter_by(id=session["id"]).first().websocket_id) # tell the user that the game already ended
        print("[ERROR] User {} requested a rematch for a nonexistent game!".format(session["id"]))
    else:
        game = master_game_handler.get_match_by_id(try_game_id)
        game.rematch_requested[session["id"]] = True # mark that this player wants a rematch
        if game.rematch_requested[game.white_user_id] and game.rematch_requested[game.black_user_id]: # if the other player wants a rematch too
            master_game_handler.rematch(try_game_id)
        else: # otherwise, if this is the first rematch request for this game
            socketio_handler.emit("wants rematch", room=game.game_room) # tell both the players that a rematch was requested


# removes users from queue and updates their 'last active' times when they disconnect
@socketio_handler.on("disconnect")
def sockio_disconnect():
    master_game_handler.remove_all_challenges(session["id"]) # user can't accept or have challenges accepted while offline

    game_id = master_game_handler.get_player_game_id(session["id"])
    print("removing user {} from game {}".format(session["id"], game_id))
    if game_id is None: # if they aren't in game, remove them from queue
        master_game_handler.remove_user_from_queue(session["id"])
    else: # if they are in game, mark the game as over
        master_game_handler.get_match_by_id(game_id).game_over()

    socketio_handler.emit("logged off", session["id"], broadcast=True) # update everyone's 'online users' list

    this_user = GuestUser.query.filter_by(id=session["id"]).first()
    sign_off_user(webapp_db, this_user)

    print("User {} disconnected".format(session["id"]))
