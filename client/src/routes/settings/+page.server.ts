/** @type {import('./$types').Actions} */


import { checkLogin } from "$lib";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
    if (!cookies.get("username") || !cookies.get("password")) {
        throw redirect(303, "/login");
    }
    
	if (await checkLogin(cookies.get("username")!, cookies.get("password")!, BACKEND_URL) === false) {
        throw redirect(303, "/login");
    }

    return;
}

export const actions = {
	default: async ({cookies, request}: {"cookies": any, "request": any}) => {
        const formData = await request.formData();
        const dark = formData.get('dark')?.toString();
        const cardDesign = formData.get('cardDesign')?.toString();
        const theme = formData.get('theme')?.toString();

        if (!cardDesign || !theme) {
            return {error: "Missing required fields"};
        }

        let darkBool;

        if (dark === "on") {
            darkBool = true;
        } else {
            darkBool = false;
        }

        if (typeof cardDesign !== "string" || typeof theme !== "string") {
            return {error: "Invalid data type"}
        }



        if (cardDesign !== "classic" && cardDesign !== "auto" && cardDesign !== "dark" && cardDesign !== "light" && cardDesign !== "pescado") {
            return {error: "Invalid card design"}
        }

        if (theme !== "modern" && theme !== "rebels" && theme !== "solo" && theme !== "classic") {
            return {error: "Invalid theme"}
        }

        let requestData = {
            username: cookies.get("username"),
            password: cookies.get("password"),
            dark: darkBool,
            theme: theme,
            cardDesign: cardDesign
        }

        fetch(BACKEND_URL + "/preferences", {
            method: 'POST', // Set the method to POST
            headers: {
                'Content-Type': 'application/json' // Set the headers appropriately
            },
            body: JSON.stringify(requestData) // Convert your data to JSON
        });

        throw redirect(303, "/");
	}
};
