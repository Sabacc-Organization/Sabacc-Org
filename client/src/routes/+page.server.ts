/** @type {import('./$types').PageServerLoad} */

import { backendPostRequest, checkLogin } from "$lib";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export async function load({ cookies, platform }) {

    let loggedIn;
    if (!cookies.get("username") || !cookies.get("password") || !cookies.get("dark") || !cookies.get("theme") || !cookies.get("cardDesign")) {
        return {loggedIn: false};
    }
    
	loggedIn = await checkLogin(cookies.get("username"), cookies.get("password"), BACKEND_URL);

    return {
        gamesData: await backendPostRequest(cookies.get("username"), cookies.get("password"), BACKEND_URL + "/")
    }
}