// HTML stuff
var board = null
var color = "white" // keeps track of the orientation of the board, since we have to reinstantiate it every time the window resizes (ugh)
var game = new Chess()
var inOnlineGame = false
var $gameLog = $('#log')

// Sound effects
var piece_move = new Audio("audio/piece_move.mp3")
var piece_cap = new Audio("audio/piece_cap.mp3")
var music = new Audio("audio/whoops.mp3")
var defaultVolume = 0.25
music.loop = true

// CSS skullfuckery
function changeMeterLevel(newVolume) {
    var $gom = $("#geniusOMeterMidFull") // animate the genius-o-meter-moving to its new level with the worst hack yet created
    var endingMeterLevel = Math.round(1.33 * ((newVolume * 100) - 25)) // 25 is the base level volume, multiplying by 1.33 converts 75 bonus volume to 100% full meter
    var endingMeterClip = 100 - endingMeterLevel // clipping at 100% is fully hiding, clipping at 0% is fullly showing
    $gom.animate({
        fontSize: endingMeterClip // fontSize will track the level to which the meter is full
    },
    {
        step: function(now, fx) { // every frame of the animation, jQuery calls this function with now=the current value of fontSize (which is animating)...
            $(this).css("clip-path", "inset(" + now + "% " + 0 + " " + 0 + " " + 0 + ")") // ...letting us manually update clip-path with a new argument based off fontSize
        }
    },
    100) // take 100 steps in the animation

    changeMeterText(endingMeterLevel)
}

// Chess *game* utils
function isStalemate(game) {
    return game.in_threefold_repetition() || game.insufficient_material() || game.in_stalemate()
}

// Chess *board* utils
function onDragStart(source, piece, startPosition, facing) { // called when a piece is picked up
    if(game.game_over()) {
        return false // don't let players move pieces if the game is over
    }

    if(game.turn() == "w" && piece.charAt(0) == 'b'|| game.turn() == "b" && piece.charAt(0) == 'w') {
        return false // don't let players move black pieces on white's turn, or vice versa
    }
}

function onSnapEnd() { // called when a piece "snap" animation is finished
    board.position(game.fen()) // autocorrects the board to the state of the game, to prevent illegal moves
}

function updateLog() {
    $gameLog.html(game.pgn())
}

// Chessboard -> server communication (need this here since spectate() shit needs it in iomain.js)
function onDropPvp(startPosition, endPosition, piece) {
    var move = startPosition + endPosition
    var endRow = endPosition.charAt(1)
    if((endRow == '1' || endRow == '8') && piece.charAt(1) == 'P') { // if moving a pawn to an end row, automatically promote to a queen (can cause problems when knights are needed)
        move += "q"
    }

    ioSocket.emit("make move", move) // submit moves to the server for approval, to avoid client-side fuckery
}

function getBoardConfig(startingFen, onDropFn) {
    return {
            draggable: true, // allow players to drag pieces
            onDragStart: onDragStart,
            onDrop: onDropFn,
            onSnapEnd: onSnapEnd,
            position: startingFen, // start the pieces in the standard start position
            showNotation: false
           }
}
