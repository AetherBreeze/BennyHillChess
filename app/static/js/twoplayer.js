/*// Music stuff
var music = new Audio("audio/whoops.mp3")
var defaultVolume = 0.25
music.loop = true*/

// Server -> chessboard communication
ioSocket.on("game start", function(gameData) {
    inOnlineGame = true

    // update the game and the board
    game = new Chess() // create a new client-side game
    board = Chessboard("myBoard", getBoardConfig("start", onDropPvp)) // reset the chess board when the game starts
    board.orientation(gameData.color) // flip the board so that the player's side is facing them
    color = gameData.color

    // update things around the board (users, log, etc.)
    $("#enemyName").html(gameData.opponent) // change the opponent's name to our new opponent's name...
    $("#enemyAvatar").attr("src", gameData.opponentAvatarUrl) // ...and the opponent's avatar to the new opponent's
    $("#postGameButtons").html('') // remove the post-game buttons, if they were there
    $("#geniusOMeterMidFull").css({"clip-path": "inset(100%, 0, 0, 0)"}) // set the genius-o-meter back to zero
    updateLog() // reset the SAN log

    music.volume = defaultVolume
    music.currentTime = 0 // start the song at the beginning again
    music.play()
    changeMeterLevel(0)
})

ioSocket.on("update board", function(move) { // updates the state of the board every time a server-approved move is made
    console.log("got move " + move)
    var startPosition = move.substring(0, 2) // do all computing first, to decrease delay between game move and board move
    var endPosition = move.substring(2, 4)
    game.move({ // update the game
        from: startPosition,
        to: endPosition,
        promotion: 'q' // default promoting to queen, could cause problems when knight is needed
    })

    var that_move = game.history({verbose: true})[game.history().length - 1]
    if(that_move['flags'] == 'c') { // if the move was a capture
        piece_cap.play() // play the capture sfx
    }
    else { // otherwise, play the normal move sfx
        piece_move.play()
    }
    if("promotion" in that_move) {
        console.log("promotion!")
    }

    board.position(game.fen()) // update the board
    updateLog() // update the game log
})

ioSocket.on("music volume", function(volume) { // change the volume of the benny hill music depending on the max of (how bad their position is, how bad the last move was for them)
    console.log("new music volume: " + volume)
    music.volume = volume

    changeMeterLevel(volume)
    /*var $gom = $("#geniusOMeterMidFull") // animate the genius-o-meter-moving to its new level using the worst hack yet created
    var endingMeterClip = 100 - Math.round(1.33 * ((volume * 100) - 25)) // 25 is the base level volume, multiplying by 1.33 converts 75 bonus volume to 100% full meter
    $gom.animate({
        fontSize: endingMeterClip // fontSize will track the level to which the meter is full
    },
    {
        step: function(now, fx) { // every frame of the animation, jQuery calls this function with now=the current value of fontSize (which is animating)...
            $(this).css("clip-path", "inset(" + now + "% " + 0 + " " + 0 + " " + 0 + ")") // ...letting us manually update clip-path with a new argument based off fontSize
        }
    },
    100) // take 100 steps in the animation*/
})

ioSocket.on("game over", function() { // shows players a "new game?" button and spectators a "game over" splash when the client confirms that game is over
    if(inOnlineGame) { // only show the rematch button to the actual players (it doesn't work for spectators anyway, but nice try)
        $("#postGameButtons").html('<button id="leaveGameButton" onclick="leaveGame()">Leave game</button><button id="rematchButton" onclick="issueRematchRequest()">Rematch</button>')
    }
    else {
        $("#postGameButtons").html('<button id="leaveGameButton" onclick="leaveGame()">Leave game</button>')
    }
    inOnlineGame = false
    music.pause() // pause the music when the game ends
})

ioSocket.on("wants rematch", function() { // let the player know the other player wants a rematch
    $("#rematchButton").html("Rematch requested")
})

ioSocket.on("no rematch", function() {
    var $rematchButton = $("#rematchButton")
    if($rematchButton.length) { // if the rematch button is still on this person's screen,
        $rematchButton.attr("disabled", true) // disable it
        $rematchButton.html("No rematch")
    }
})

// Post match shenanigans
function leaveGame() {
    $("#postGameButtons").html('')
    $gameLog.html("")
    changeMeterLevel(0)
    ioSocket.emit("left game")
    startGameVsAi(1)
}

function issueRematchRequest() {
    $("#rematchButton").html("Requesting rematch...")
    ioSocket.emit("rematch requested")
}

// jQuery resizing shenanigans || have to do this here, since it requires our onDrop function
$(window).resize(() => { // reinstantiate the board every time the window is resized (ugh) because it doesn't do it by itself otherwise and ends up covering the right column
    board = new Chessboard("myBoard", getBoardConfig(board.fen(), onDropPvp))
    board.orientation(color)
})
