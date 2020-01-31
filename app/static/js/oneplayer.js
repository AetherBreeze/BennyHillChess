var difficulty = 2
var timeout = 500

// AI utils

// Value arrays indicating how valuable a given piece is on a given square
function reverseArray(array) {
	return array.slice().reverse();
}

var whitePawnEval =
	[
	    [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
	    [5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0],
	    [1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0],
	    [0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5],
	    [0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0],
	    [0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5],
	    [0.5,  1.0,  1.0,  -2.0, -2.0,  1.0,  1.0,  0.5],
	    [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
	];

var blackPawnEval = reverseArray(whitePawnEval);

var knightEval =
	[
	    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
	    [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
	    [-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0],
	    [-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0],
	    [-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0],
	    [-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0],
	    [-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0],
	    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
	];

var whiteBishopEval = [
	[ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
	[ -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
	[ -1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0],
	[ -1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0],
	[ -1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0],
	[ -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0],
	[ -1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
	[ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
];

var blackBishopEval = reverseArray(whiteBishopEval);

var whiteRookEval = [
	[  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
	[  0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5],
	[ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
	[ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
	[ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
	[ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
	[ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
	[  0.0,   0.0, 0.0,  0.5,  0.5,  0.0,  0.0,  0.0]
];

var blackRookEval = reverseArray(whiteRookEval);

var evalQueen = [
	[ -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
	[ -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
	[ -1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
	[ -0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
    [  0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
    [ -1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
    [ -1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
    [ -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
];

var whiteKingEval = [

	[ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
	[ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
	[ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
	[ -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
	[ -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
	[  2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0 ],
	[  2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0 ]
];

var blackKingEval = reverseArray(whiteKingEval);

// Calculates the best move for the given game object
function calculateBestMove() {
	var possibleNextMoves = game.moves();
    var bestMove = -9999;
    var bestMoveFound;

    for(var i = 0; i < possibleNextMoves.length; i++) {
        var possibleNextMove = possibleNextMoves[i]
        game.move(possibleNextMove);
        var value = minmax(difficulty, -10000, 10000, false);
        game.undo();
        if(value >= bestMove) {
             bestMove = value;
	         bestMoveFound = possibleNextMove;
	    }
	}
	return bestMoveFound;
}


// Calculates the value of a move using alpha-beta pruning on [depth] levels
function minmax(depth, alpha, beta, isMaximisingPlayer) {
	if (depth === 0) {
	    return -evaluateBoard(game.board());
	}

	var possibleNextMoves = game.moves();
	var numPossibleMoves = possibleNextMoves.length

	if (isMaximisingPlayer) {
	    var bestMove = -9999;
	    for (var i = 0; i < numPossibleMoves; i++) {
	        game.move(possibleNextMoves[i]);
	        bestMove = Math.max(bestMove, minmax(depth - 1, alpha, beta, !isMaximisingPlayer));
	        game.undo();
	        alpha = Math.max(alpha, bestMove);
	        if(beta <= alpha){
	            return bestMove;
	        }
	    }
	}
	else {
	    var bestMove = 9999;
	    for (var i = 0; i < numPossibleMoves; i++) {
	        game.move(possibleNextMoves[i]);
	        bestMove = Math.min(bestMove, minmax(depth - 1, alpha, beta, !isMaximisingPlayer));
	        game.undo();
	        beta = Math.min(beta, bestMove);
	        if(beta <= alpha){
	            return bestMove;
	        }
	    }
	}

    return bestMove;
}


// Gives a numerical rating to the 'good'ness of a board position (called recursively by minmax)
function evaluateBoard(board) {
	var totalEvaluation = 0;
	for (var i = 0; i < 8; i++) {
	    for (var j = 0; j < 8; j++) {
	        totalEvaluation = totalEvaluation + getPieceValue(board[i][j], i, j);
	    }
    }
	return totalEvaluation;
}

function getPieceValue(piece, x, y) {
	if (piece === null) {
	    return 0;
	}

	var absoluteValue = getAbsoluteValue(piece, piece.color === 'w', x ,y);
    if(piece.color === 'w') {
	    return absoluteValue;
	}
	else {
	    return -absoluteValue;
	}
}


function getAbsoluteValue(piece, isWhite, x ,y) {
    if (piece.type === 'p') {
        return 10 + ( isWhite ? whitePawnEval[y][x] : blackPawnEval[y][x] );
    }
    else if (piece.type === 'r') {
        return 50 + ( isWhite ? whiteRookEval[y][x] : blackRookEval[y][x] );
    }
    else if (piece.type === 'n') {
        return 30 + knightEval[y][x];
    }
    else if (piece.type === 'b') {
        return 30 + ( isWhite ? whiteBishopEval[y][x] : blackBishopEval[y][x] );
    } else if (piece.type === 'q') {
        return 90 + evalQueen[y][x];
    } else if (piece.type === 'k') {
        return 900 + ( isWhite ? whiteKingEval[y][x] : blackKingEval[y][x] );
    }
}

function makeAImove() {
	game.move(calculateBestMove());
	board.position(game.fen());
	updateLog();
}

// Chess *board* utils
function onDropAi(source, target) {
    var move = game.move({
      from: source,
      to: target,
      promotion: 'q' // assume we always promote to a queen, could cause problems when knight is necessary
    })

    if (move === null) {
        return 'snapback'
    }
    window.setTimeout(makeAImove, timeout);
}

// jQuery resizing shenanigans || have to do this here, since it requires our onDrop function
$(window).resize(() => { // reinstantiate the board every time the window is resized (ugh) because it doesn't do it by itself otherwise and ends up covering the right columns
    board = new Chessboard("myBoard", getBoardConfig(board.fen(), onDropAi))
})

// Main function
function startGameVsAi(newDifficulty) {
    $("#enemyAvatar").attr("src", "/static/img/avatars/stockfish.png")
    $("#enemyName").html("Computer Overlords (level " + newDifficulty + ")")
    $("#gameLog").html('')
    difficulty = newDifficulty
    board = new Chessboard("myBoard", getBoardConfig("start", onDropAi)) // Initialize the preexisting board for the AI game
    game = new Chess()
}

startGameVsAi(1)
