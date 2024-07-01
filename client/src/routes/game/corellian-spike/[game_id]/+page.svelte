<script lang="ts">
    import GameTemplate from "../../gameTemplate.svelte";

    let game_variant = 'corellian_spike';

    function renderCard(cardValue: {'suit': string, 'val':number}, cardDesign: string, dark: boolean){
        let returnText: string = "background-image:url(";

        returnText += '/images/cards/corellian/jacob-densford/';

        if (cardValue['val'] > 0){
            returnText += '+';
        }

        returnText += cardValue['val'].toString();

        returnText += {'circle':'_Circle', 'square':'_Square', 'triangle':'_Triangle', 'sylop':'_Sylop'}[cardValue['suit']]

        returnText += ".png);background-color:transparent;border:transparent;";
        return returnText;
    }

    function renderBack(cardDesign: string){
        return 'background-image:url(/images/cards/corellian/jacob-densford/Back.png);background-color:transparent;border:transparent;'
    }
</script>

<GameTemplate {game_variant} {renderBack} {renderCard}/>