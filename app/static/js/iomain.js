var ioSocket = io()

// Webpage IO functions and utils
function generatePlayerListEntry(userData) {
    html = "<li id='" + userData.id + "' class='userInList' onmouseenter='openUserMenu(" + userData.id + ")' onmouseleave='closeUserMenu(" + userData.id + ")'>"
    html = html + "<span class='userInListName'>" + userData.username + "</span>"
    html = html + "</li>"

    return html
}

function challenge(userId) {
    if(inOnlineGame) {
        $("#" + userId).find(".challengeMenu").html("Can't challenge while in game!")
    }
    else {
        ioSocket.emit("challenge", userId)
        $("#" + userId).find(".challengeMenu").html("Challenged!")
    }
}

function spectate(userId) {
    ioSocket.emit("spectate", userId)
}

// Browser -> server communication
ioSocket.on("challenged by", (userData) => {
    challengeHtml = "<div id='alertMessage'><span id='challengeMessage'>" + userData.username + " has challenged you!</span></div><div id='alertButtonsDiv'><button id='acceptChallenge'>Accept</button><button id='declineChallenge'>Decline</button></div>"
    showAlert(challengeHtml)
    $("#acceptChallenge").mouseup((event) => {
        ioSocket.emit("challenge accepted")
        removeAlert()
    })
    $("#declineChallenge").mouseup((event) => {
        ioSocket.emit("challenge declined")
        removeAlert()
    })
})

ioSocket.on("spectate confirmed", (gameData) => {
    $("#enemyAvatar").attr("src", gameData.blackAvatarUrl)
    $("#enemyName").html(gameData.blackName)
    $("#gameLog").html(gameData.san)
    $("#thisAvatar").attr("src", gameData.whiteAvatarUrl)
    $("#thisName").html(gameData.whiteName)

    game = new Chess(gameData.fen) // create a new client-side game in the current state...
    board = Chessboard("myBoard", getBoardConfig(gameData.fen, onDropPvp)) // ...initialized to the FEN of the game you're spectating
    music.volume = defaultVolume
    music.currentTime = 0 // start the song at the beginning again
    music.play()
    changeMeterLevel(0)
})

ioSocket.on("spectate failed", () => {
    $(".spectateButton").html(" Not in game!")
})

ioSocket.on("logged on", (userData) => { // when another user connects,
    $("#onlinePlayerList").append(generatePlayerListEntry(userData)) // add them to the online users list
})

ioSocket.on("logged off", (userId) => { // when another user disconnects,
    $("#" + userId).remove() // remove them from the online users list
})

function openUserMenu(userId) {
    $("#" + userId).append("<span class='userMenu'><span class='challengeButton' onclick='challenge(" + userId + ")'>  Challenge</span><span class='spectateButton' onclick='spectate(" + userId +")'>  Spectate</span></span>")
}

function closeUserMenu(userId) {
    $("#" + userId).find(".userMenu").remove()
}
