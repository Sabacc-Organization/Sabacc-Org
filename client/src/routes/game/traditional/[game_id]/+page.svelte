<script lang="ts">
    import GameTemplate from "../../gameTemplate.svelte";
    import { page } from '$app/stores'

    /** @type {import('./$types').PageData} */
	export let data;
    let username = data.username;
    let password = data.password;
    let dark = data.dark;
    let cardDesign = data.cardDesign;
    let theme = data.theme;

    $: game_id = $page.params.game_id;
    let game_variant = 'traditional';

    function renderCard(cardValue: {'suit': string, 'val':number, 'prot':boolean}){
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

    function renderBack(){
        if (cardDesign === "pescado"){
            return "background-image:url(/images/cards/traditional/pescado/back.png);";
        }
        return "background-image:url(/images/cards/traditional/rebels-card-back.png);";
    }
</script>

<GameTemplate _game_variant={game_variant} _username={username} _password={password} _dark={dark} _cardDesign={cardDesign} _theme={theme} {renderCard} {renderBack}/>