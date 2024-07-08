<script lang="ts">
    import GameTemplate, { BACKEND_URL, FRONTEND_URL, username, password, dark, cardDesign, theme, socket } from "../../gameTemplate.svelte";
    import { page } from '$app/stores'

    $: game_id = $page.params.game_id;
    let game_variant = 'traditional';

    function renderCard(cardValue: {'suit': string, 'val':number, 'prot':boolean}, cardDesign: string, dark: boolean){
        let returnText: string = "background-image:url(";

        let darkPath = "/images/cards/traditional/dark/";
        let lightPath = "/images/cards/traditional/light/";
        let pescadoPath = "/images/cards/traditional/pescado/";

        if (cardDesign === "classic"){
            returnText += "/images/rebels-card-back.png);";
            return returnText;
        }

        else if (cardDesign === "auto"){
            returnText += dark? darkPath:lightPath;
        }

        else if (cardDesign === "dark"){
            returnText += darkPath;
        }

        else if (cardDesign === "light"){
            returnText += lightPath;
        }

        else if (cardDesign === "pescado"){
            returnText += pescadoPath;
        }

        returnText += {"flasks":"b", "sabers":"r", "staves":"g", "coins":"y", "negative/neutral":"p"}[cardValue["suit"]];
        returnText += cardValue["val"].toString();
        returnText += cardDesign === "pescado" && cardValue['prot']? "p":"";
        returnText += ".png);";
        return returnText;
    }

    function renderBack(cardDesign: string){
        if (cardDesign === "pescado"){
            return "background-image:url(/images/cards/traditional/pescado/back.png);";
        }
        return "background-image:url(/images/cards/traditional/rebels-card-back.png);";
    }

    // protect doesnt request any data, it just sends it. when the server recieves it, it updates the game, and sends the new info to every client through updateClientGame
    // this applies to bet, card, shift, and playAgain.
    function protect(protCard : {[id: string]: any}) {
        let clientInfo = {
            "username": username,
            "password": password,
            "game_id": game_id,
            "game_variant": game_variant,
            "action": "protect",
            "protect": protCard
        }
        socket.emit('gameAction', clientInfo)
    }
</script>

<GameTemplate {game_variant} {renderBack} {renderCard} onDBClickCard={protect}/>