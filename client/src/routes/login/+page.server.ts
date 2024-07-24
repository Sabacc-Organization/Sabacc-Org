/** @type {import('./$types').Actions} */


import { checkLogin } from "$lib";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies, platform }) {
    if (!cookies.get("username") || !cookies.get("password") || !cookies.get("dark") || !cookies.get("theme") || !cookies.get("cardDesign")) {
        return;
    }
    
	if (await checkLogin(cookies.get("username"), cookies.get("password"), BACKEND_URL) === false) {
        return
    }

    throw redirect(303, "/");
}

export const actions = {
	default: async ({cookies, request}) => {
        const formData = await request.formData();
        const username = formData.get('username')?.toString();
        const password = formData.get('password')?.toString();

        if (!username || !password) {
            return {error: "Missing required fields"};
        }


        let loginIsValid = await checkLogin(username, password, BACKEND_URL);


        if (!loginIsValid) {
            return {error: "Login data is invalid"}
        }

        cookies.set('username', username, {
            path: '/',
            maxAge: 60 * 60 * 24 * 30});
        cookies.set('password', password, {
            path: '/',
            maxAge: 60 * 60 * 24 * 30});
        cookies.set('dark', "false", {
            path: '/',
            maxAge: 60 * 60 * 24 * 30});
        cookies.set('theme', "modern", {
            path: '/',
            maxAge: 60 * 60 * 24 * 30});
        cookies.set('cardDesign', "auto", {
            path: '/',
            maxAge: 60 * 60 * 24 * 30});

        throw redirect(303, "/");
	}
};