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

    let game_variant = 'kessel';

    function renderCard(cardValue: {'suit': string, 'val':number} | string, negative: boolean = false){
        let returnText: string = "background-image:url(";

        returnText += '/images/cards/kessel/pescado/';
        if (typeof cardValue === 'string'){
            returnText += 'shiftTokens/' + cardValue;
        } else {
            returnText += 'cards/'
            if (cardValue["suit"] === "basic"){
                returnText += cardValue['val'];
            } else {
                returnText += cardValue['suit'];
            }
            returnText += negative? '_blood' : '_sand';
        }

        returnText += ".png);background-color:transparent;border:transparent;";
        return returnText;
    }

    function renderBack(negative: boolean){
        let returnText = 'background-image:url(/images/cards/kessel/pescado/cards/';

        returnText += negative? 'back_blood' : 'back_sand'

        returnText += '.png);background-color:transparent;border:transparent;';
        return returnText
    }
</script>

<GameTemplate _game_variant={game_variant} _username={username} _password={password} _dark={dark} _cardDesign={cardDesign} _theme={theme} {renderCard} {renderBack}/>