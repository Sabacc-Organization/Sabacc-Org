function betPhase() {

    if (u_dex === 0) {

        // If there has been no raise
        if (pBets[u_dex + 1] === "") {

            $("#pots").addClass("active");

            // Double Tap Check
            $("#pots").dblclick(function(){
                let data = { "game_id": game_id, "action": "bet", "amount": 0};
                bet_socket.emit("bet", data);
            });

            // Dragging interface
            $("#" + thisUName + "BetPile").addClass("betPile");

            $('.ownChip').draggable({
                cursor: 'move',
                revert: 'invalid', // Revert only if not dropped onto a valid droppable target
                helper: 'clone'   // Use a clone when dragging
            });

            $('.betPile').droppable({
                accept: '.ownChip',
                drop: function(event, ui) {
                    $("#actBox").show();
                    $(this).append(ui.helper.clone()); // Append the clone to the droppable area
                    
                    let incVal;
                    if (ui.helper.hasClass("bigChip")) {
                        incVal = 10;
                    }
                    else if (ui.helper.hasClass("midChip")) {
                        incVal = 5;
                    }
                    else if (ui.helper.hasClass("lowChip")) {
                        incVal = 1;
                    }

                    if (isNaN(parseInt($("#betSpan").text()))) {
                        $("#betSpan").text(String(incVal));
                    }
                    else {

                        $("#betSpan").text(String(parseInt($("#betSpan").text()) + incVal));
                    }
                }
            });

            // Submit bet
            $("#actBox").append('<button type="button" id="betBtn" class="btn btn-primary">Bet</button>');
            $("#actBox").hide();

            $("#betBtn").click(function(){
                let credsIn = parseInt($("#betSpan").text());
                if (isNaN(credsIn)) {
                    $("#betDiv").remove();
                    let data = { "game_id": game_id, "action": "bet", "amount": 0 };
                    bet_socket.emit("bet", data);
                ")";
                } else if (credsIn < 0 || credsIn > parseInt(credits[u_dex])) {
                } else {
                    $("#betDiv").remove();
                    let data = { "game_id": game_id, "action": "bet", "amount": credsIn };
                    bet_socket.emit("bet", data);
                }
            });

        }

        // If there has been a raise
        else {
            let raiseAmount = 0;
            let followAmount = 0;
            for (let i = 1; i < pBets.length; i++) {
                if (pBets[i] != "") {
                    if (parseInt(pBets[i]) > raiseAmount) {
                        raiseAmount = parseInt(pBets[i]);
                    }
                }
            }
            followAmount = raiseAmount - parseInt(pBets[u_dex]);


            $("#actBox").append('<div id="betDiv" class="backBlue"> <form> <button type="button" id="callOpt" class="btn btn-primary">Call</button> <button type="button" id="raiseOpt" class="btn btn-primary">Raise</button> <button type="button" id="foldOpt" class="btn btn-primary">Fold</button> </form><p id="invalidBetCredits" class="red"></p></div>');

            // Player calls
            $("#callOpt").click(function(){
                $("betDiv").remove();
                let data = { "game_id": game_id, "action": "call", "amount": followAmount};
                bet_socket.emit("bet", data);
            });


            // Player raises
            $("#raiseOpt").click(function(){

                let lowVal = 0;

                for (let i = 0; i < pBets.length; i++) {
                    try {
                        if (parseInt(pBets[i]) > lowVal && !isNaN(parseInt(pBets[i]))) {
                            lowVal = pBets[i];
                        }
                    }
                    catch (error) {
                        console.log(error);
                    }
                }
                lowVal;

                // Remove old bet prompt
                $("#betDiv").remove();

                $("#betSpan").text(String(lowVal));

                // Dragging interface
                $("#" + thisUName + "BetPile").addClass("betPile");

                $("#betSpan").text(pBets[u_dex - 1]);

                $('.ownChip').draggable({
                    cursor: 'move',
                    revert: 'invalid', // Revert only if not dropped onto a valid droppable target
                    helper: 'clone'   // Use a clone when dragging
                });

                $('.betPile').droppable({
                    accept: '.ownChip',
                    drop: function(event, ui) {
                        $(this).append(ui.helper.clone()); // Append the clone to the droppable area
                        
                        let incVal;
                        if (ui.helper.hasClass("bigChip")) {
                            incVal = 10;
                        }
                        else if (ui.helper.hasClass("midChip")) {
                            incVal = 5;
                        }
                        else if (ui.helper.hasClass("lowChip")) {
                            incVal = 1;
                        }

                        if (isNaN(parseInt($("#betSpan").text()))) {
                            $("#betSpan").text(String(incVal));
                        }
                        else {

                            $("#betSpan").text(String(parseInt($("#betSpan").text()) + incVal));
                        }
                    }
                });


                // Submit bet
                $("#actBox").append('<button type="button" id="raiseBtn" class="btn btn-primary">Raise</button>');

                $("#raiseBtn").click(function(){
                    let credsIn = parseInt($("#betSpan").text());
                    if (credsIn > lowVal && credsIn < parseInt(credits[u_dex])) {
                        // $("#betDiv").remove();
                        let data = { "game_id": game_id, "action": "raise", "amount": credsIn - pBets[u_dex] };
                        bet_socket.emit("bet", data);
                    }
                });
                

            });

            // Player folds
            $("#foldOpt").click(function(){
                $("betDiv").remove();
                let data = { "game_id": game_id, "action": "fold"};
                bet_socket.emit("bet", data);
            });
            
        }


    }

    else {

        $("#actBox").append('<div id="betDiv" class="backBlue"> <form> <button type="button" id="callOpt" class="btn btn-primary">Call</button> <button type="button" id="raiseOpt" class="btn btn-primary">Raise</button> <button type="button" id="foldOpt" class="btn btn-primary">Fold</button> </form><p id="invalidBetCredits" class="red"></p></div>');

        // Player calls
        $("#callOpt").click(function(){
            $("betDiv").remove();
            let a;
            if (pBets[u_dex] != "") {
                a = parseInt(pBets[0]) - parseInt(pBets[u_dex]);
            } 
            else {
                a = parseInt(pBets[0]);
            }


            let data = { "game_id": game_id, "action": "call", "amount": a};
            bet_socket.emit("bet", data);
        });


        // Player raises
        $("#raiseOpt").click(function(){

            $("#betDiv").remove();

            $("#betSpan").text(pBets[u_dex - 1]);

            // Dragging interface
            $("#" + thisUName + "BetPile").addClass("betPile");

            $("#betSpan").text(pBets[u_dex - 1]);

            $('.ownChip').draggable({
                cursor: 'move',
                revert: 'invalid', // Revert only if not dropped onto a valid droppable target
                helper: 'clone'   // Use a clone when dragging
            });

            $('.betPile').droppable({
                accept: '.ownChip',
                drop: function(event, ui) {
                    $(this).append(ui.helper.clone()); // Append the clone to the droppable area
                    
                    let incVal;
                    if (ui.helper.hasClass("bigChip")) {
                        incVal = 10;
                    }
                    else if (ui.helper.hasClass("midChip")) {
                        incVal = 5;
                    }
                    else if (ui.helper.hasClass("lowChip")) {
                        incVal = 1;
                    }

                    if (isNaN(parseInt($("#betSpan").text()))) {
                        $("#betSpan").text(String(incVal));
                    }
                    else {

                        $("#betSpan").text(String(parseInt($("#betSpan").text()) + incVal));
                    }
                }
            });


            // Submit raise
            $("#actBox").append('<button type="button" id="raiseBtn" class="btn btn-primary">Raise</button>');

            $("#raiseBtn").click(function(){
                let credsIn = parseInt($("#betSpan").text());
                if (credsIn > parseInt(pBets[u_dex - 1]) && credsIn < parseInt(credits[u_dex])) {
                    $("#betDiv").remove();
                    let data = { "game_id": game_id, "action": "raise", "amount": credsIn - pBets[u_dex] };
                    bet_socket.emit("bet", data);
                }
            });
        });

        // Player folds
        $("#foldOpt").click(function(){
            $("#betDiv").remove();
            let data = { "game_id": game_id, "action": "fold"};
            bet_socket.emit("bet", data);
        });

    }

}