function cardPhase() {

    if (game["phase"] === "card" && game["cycle_count"] != 0) {

        $("#alderaan").addClass("active");

        $("#alderaan").click(function(){
           
            let data = { "game_id": game_id, "action": "alderaan"};
            card_socket.emit("card", data);
            
        });
    }

    $("#deck").addClass("active");
    $("#discard").addClass("active");

    $("#deck").click(function(){
        let data = { "game_id": game_id, "action": "draw"};
        card_socket.emit("card", data);
    });

    $("#tradeBtn").click(function(){
        $('.own').click(function(event) {
            switch (event.which) {

                case 1:
                    let data = { "game_id": game_id, "action": "trade", "trade": $(this).find("h5").text()};
                    card_socket.emit("card", data);
                    break;

                case 2:
                    break;

                case 3:
                    break;

                default:
                    
            }
        });

        
    });

    $("#standBtn").click(function(){
        let data = { "game_id": game_id, "action": "stand"};
        card_socket.emit("card", data);
    });

}