function refreshGame(gata) {
    game = gata;

    $("#pAction").text(game["p_act"]);

    $("#sabacc_pot").text(game["sabacc_pot"]);
    $("#hand_pot").text(game["hand_pot"]);

    $("#actBox").empty();

    // Hand stuff
    hands = game["player_hands"].split(";");

    // Credits stuff
    credits = game["player_credits"].split(",");
    pBets = game["player_bets"].split(",");

    // Protected cards stuff
    protAll = game["player_protecteds"].split(";");

    for (let u = 0; u < us_list.length; u++) {

        uName = us_list[u].slice(1, us_list[u].length - 1)
        $("#" + uName + "Stuff").empty();
    }

    setupGame(false);

    // Protecting stuff
    $('.own').mousedown(function(event) {
        switch (event.which) {

            case 1:
                break;

            case 2:
                break;

            case 3:
                $(this).addClass("protected");
                data = {"game_id": game_id, "protect": $(this).text()}; // There is a bug here. One day I will regret this. Do not protect two identical cards.
                protect_socket.emit("protect", data);
                break;

            default:
                
        }
    });

    // If it is the player's turn
    if (game["player_turn"] === uid && game["completed"] === 0) {
                
        if (game["phase"] === "betting") { // Betting Phase
            
            betPhase();

        }


        else if (game['phase'] === "card" || game['phase'] === "alderaan") {

            cardPhase();

        }

    }

    else if (game["player_turn"] === uid && game["completed"] === 1) {
        $("#gameInfo").append('<button type="button" id="pAgainBtn" class="btn btn-primary">Play Again</button>');

        $("#pAgainBtn").click(function(){
            

            let data = { "game_id": game_id };
            cont_socket.emit("cont", data);
            
        });
    }

}

function setupGame(setup) {

    if (setup) {
        // Poker table background
        $("main").addClass("game");

        // Place user at "pole position"
        if (u_dex != 0) {
            let ogPZero = $(".player0");
            let ogPThis = $(".player" + String(u_dex));

            ogPZero.addClass("player" + String(u_dex));
            ogPZero.removeClass("player0");

            ogPThis.addClass("player0");
            ogPThis.removeClass("player" + String(u_dex));
        }
    }


    // Card images
    // Players header text
    let psHeader = "";
    for (let u = 0; u < us_list.length; u++) {

        uName = us_list[u].slice(1, us_list[u].length - 1)
        psHeader += uName + " vs. ";

        if (game["completed"] === 0) {

            for (let i = 0; i < hands[u].split(",").length; i++) {
                let c = hands[u].split(",")[i];
                if (protAll[u].split(",")[i] === "0") {
                    if (u === u_dex) {
                        $("#" + uName + "Stuff").append('<div class="card child own"><h5>' + c + '</h5></div>');
                    }
                    else {
                        $("#" + uName + "Stuff").append('<div class="card child"></div>');
                    }
                }
                else {
                    if (u === u_dex) {
                        $("#" + uName + "Stuff").append('<div class="card child own protected"><h5>' + c + '</h5></div>');
                    }
                    else {
                        $("#" + uName + "Stuff").append('<div class="card child protected"><h5>' + c + '</h5></div>');
                    }
                }
            }
        }
        else if (game["completed"] === 1) {
            for (let i = 0; i < hands[u].split(",").length; i++) {
                let c = hands[u].split(",")[i];
                $("#" + uName + "Stuff").append('<div class="card child"><h5>' + c + '</h5></div>');
            }
        }
    }
    psHeader = psHeader.slice(0, psHeader.length - 5);
    $("#psHeader").text(psHeader);

    // Bet Boxes
    for (let u = 0; u < us_list.length; u++) {

        uName = us_list[u].slice(1, us_list[u].length - 1)

        if (u === u_dex) {
            $("#" + uName + "Stuff").prepend('<div id="' + uName + 'BetBox" class="backBlue"><h5>$<span id="betSpan">' + pBets[u] + '</span></h5> <div id="' + uName + 'BetPile" </div></div>');
        }
        else {
            $("#" + uName + "Stuff").prepend('<div id="' + uName + 'BetBox" class="backRed"><h5>$' + pBets[u] + '</h5</div>');
        }
        
    }

    // Generate player boxes
    for (let i = 0; i < player_ids.length; i++) {

        uName = us_list[i].slice(1, us_list[i].length - 1)

        if (i === u_dex) {
            $("#" + uName + "Stuff").append('<div id="' + uName + 'Box" class="backBlue"><h5>' + uName + '</h5> <div class="parent"> <div class="ownChip child chip bigChip"></div> <div class="ownChip child chip midChip"></div> <div class="ownChip child chip lowChip"></div> </div> <h5>$<span id="credits">' + credits[i] + '</span></h5>');
        }
        else {
            $("#" + uName + "Stuff").append('<div id="' + uName + 'Box" class="backRed"> <h5>' + uName + '</h5> <div class="parent"> <div class="chip bigChip child"></div> <div class="chip midChip child"></div> <div class="chip lowChip child"></div> </div> <h5>$<span id="' + uName + '_credits">' + credits[i] + '</span></h5>');
        }
    }

    // Phase text
    $("#phase").text(game["phase"] + " phase");

    // Display Shift
    if (game["shift"] === 1) {
        $("#dieTwo").css("background-color", "#0cc23c");
    }

    // Alderaan blown up
    if (game["phase"] === "alderaan") {
        $("#alderaan").addClass("blown");
    }


}

// Protecting stuff
$('.own').mousedown(function(event) {
    switch (event.which) {

        case 1:
            break;

        case 2:
            break;

        case 3:
            $(this).addClass("protected");
            data = {"game_id": game_id, "protect": $(this).text()}; // There is a bug here. One day I will regret this. Do not protect two identical cards.
            protect_socket.emit("protect", data);
            break;

        default:
            
    }
});