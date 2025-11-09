/** @type {import('./$types').PageServerLoad} */

import { backendPostRequest, checkLogin, getPreferences } from "$lib";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export async function load({ cookies, platform }) {

    let loggedIn;
    const username = cookies.get("username");
    const password = cookies.get("password");
    if (!username || !password) {
        return {loggedIn: false};
    }
    
	loggedIn = await checkLogin(username, password, BACKEND_URL);

    return {
        gamesData: await backendPostRequest(username, password, BACKEND_URL + "/")
    }
}