import { PUBLIC_FLASK_DOMAIN } from "$env/static/public"

export async function load({ cookies }) {

    // Session Data
	const user_id = cookies.get("user_id");
    const username = cookies.get("username");
    const dark = cookies.get("dark");
    const theme = cookies.get("theme");

    // Game data
    let gamesJson = {
        "games": [], 
        "usernames": [], 
        "gamesLen": 0, 
        "player_turns": []
    };

    if (user_id != undefined) {
        const res = await fetch(`${PUBLIC_FLASK_DOMAIN}/gameData?user_id=` + user_id); // TODO add variable parameter for user_id
        gamesJson = await res.json();
    }

	return {
		user_id,
        username,
        dark,
        theme,
        gamesJson
	};
    
}