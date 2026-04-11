/** @type {import('./$types').PageServerLoad} */

import { checkLogin, getPreferences } from "$lib";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export async function load({ cookies, platform }) {

    let loggedIn;
    const username = cookies.get("username");
    const password = cookies.get("password");
    if (!username || !password) {
        return {
            loggedIn: false,
            dark: false,
            theme: "modern",
            cardDesign: "pescado"
        };
    }
    
	loggedIn = await checkLogin(username, password, BACKEND_URL);
    let preferences: {"dark": boolean, "theme": string, "cardDesign": string} = await getPreferences(username, password, BACKEND_URL);

    return {
        loggedIn: loggedIn,
        username: username,
        dark: preferences["dark"],
        theme: preferences["theme"],
        cardDesign: preferences["cardDesign"]
    };
}