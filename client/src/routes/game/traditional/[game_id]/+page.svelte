<script lang="ts">
    import GameTemplate from "../../gameTemplate.svelte";

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
</script>

<GameTemplate {game_variant} {renderBack} {renderCard}/>