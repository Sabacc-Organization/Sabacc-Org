/** @type {import('./$types').Actions} */


import { checkLogin } from "$lib";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies, platform }) {
    if (!cookies.get("username") || !cookies.get("password") || !cookies.get("dark") || !cookies.get("theme") || !cookies.get("cardDesign")) {
        throw redirect(303, "/login");
    }
    
	if (await checkLogin(cookies.get("username"), cookies.get("password"), BACKEND_URL) === false) {
        throw redirect(303, "/login");
    }

}
