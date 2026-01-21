/** @type {import('./$types').PageServerLoad} */

import { checkLogin } from "$lib";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export async function load({ cookies, platform }) {

    let loggedIn;
    if (!cookies.get("username") || !cookies.get("password") || !cookies.get("dark") || !cookies.get("theme") || !cookies.get("cardDesign")) {
        return {
            loggedIn: false,
            theme: "modern",
            dark: "false",
            cardDesign: "auto"
        };
    }
    
	loggedIn = await checkLogin(cookies.get("username"), cookies.get("password"), BACKEND_URL);

    return {
        loggedIn: loggedIn,
        username: cookies.get("username"),
        dark: cookies.get("dark"),
        theme: cookies.get("theme"),
        cardDesign: cookies.get("cardDesign")
    }
}