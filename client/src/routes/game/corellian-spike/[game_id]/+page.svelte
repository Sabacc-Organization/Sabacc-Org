<script lang="ts">
    import GameTemplate, { BACKEND_URL, FRONTEND_URL, username, password, dark, cardDesign, theme, socket } from "../../gameTemplate.svelte";
    import { page } from '$app/stores'

    $: game_id = $page.params.game_id;

    let game_variant = 'corellian_spike';

    function renderCard(cardValue: {'suit': string, 'val':number}){
        let returnText: string = "background-image:url(";

        if (cardDesign === "pescado"){
            returnText += '/images/cards/corellian/pescado/';
        } else {
            returnText += '/images/cards/corellian/jacob-densford/';
        }

        if (cardValue['val'] > 0){
            returnText += '+';
        }

        returnText += cardValue['val'].toString();

        returnText += {'circle':'_Circle', 'square':'_Square', 'triangle':'_Triangle', 'sylop':'_Sylop'}[cardValue['suit']]

        returnText += ".png);background-color:transparent;border:transparent;";
        return returnText;
    }

    function renderBack(){
        let returnText = 'background-image:url(/images/cards/corellian/';
        if (cardDesign === 'pescado'){
            returnText += 'pescado';
        } else {
            returnText += 'jacob-densford';
        }
        returnText += '/Back.png);background-color:transparent;border:transparent;';
        return returnText
    }
</script>

<GameTemplate {game_variant} {renderBack} {renderCard} onDBClickCard={() => {}}/>