/** @type {import('./$types').Actions} */


import { checkLogin } from "$lib";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
    if (!cookies.get("username") || !cookies.get("password") || !cookies.get("dark") || !cookies.get("theme") || !cookies.get("cardDesign")) {
        throw redirect(303, "/login");
    }
    
	if (await checkLogin(cookies.get("username"), cookies.get("password"), BACKEND_URL) === false) {
        throw redirect(303, "/login");
    }

    return;
}

export const actions = {
	default: async ({cookies, request}) => {
        const formData = await request.formData();
        const dark = formData.get('dark')?.toString();
        const cardDesign = formData.get('cardDesign')?.toString();
        const theme = formData.get('theme')?.toString();

        if (!cardDesign || !theme) {
            return {error: "Missing required fields"};
        }

        let darkString;

        if (dark === "on") {
            darkString = "true";
        } else {
            darkString = "false";
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

        cookies.set('dark', darkString, {
            path: '/',
            httpOnly: false,
            secure: false,
            maxAge: 60 * 60 * 24 * 30});
        cookies.set('theme', theme, {
            path: '/',
            httpOnly: false,
            secure: false,
            maxAge: 60 * 60 * 24 * 30});
        cookies.set('cardDesign', cardDesign, {
            path: '/',
            httpOnly: false,
            secure: false,
            maxAge: 60 * 60 * 24 * 30});

        throw redirect(303, "/");
	}
};
