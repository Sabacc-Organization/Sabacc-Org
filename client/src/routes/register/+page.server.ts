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
        return;
    }

    throw redirect(303, "/");
}

export const actions = {
	default: async ({cookies, request}) => {
        const formData = await request.formData();
        const username = formData.get('username')?.toString();
        const password = formData.get('password')?.toString();
        const confirmationPassword = formData.get('confirmationPassword')?.toString();

        if (!username || !password || !confirmationPassword) {
            return {error: "Missing required fields"};
        }


        try {

            let requestData = {
                "username": username,
                "password": password,
                "confirmPassword": confirmationPassword
            }
    
            const response = await fetch(BACKEND_URL + "/register", {
                method: 'POST', // Set the method to POST
                headers: {
                    'Content-Type': 'application/json' // Set the headers appropriately
                },
                body: JSON.stringify(requestData) // Convert your data to JSON
            });
    
            let res = await response.json();
            if (response.ok) {
                cookies.set('username', username, {
                    path: '/',
                    httpOnly: false,
                    secure: false,
                    maxAge: 60 * 60 * 24 * 30});
                cookies.set('password', password, {
                    path: '/',
                    httpOnly: false,
                    secure: false,
                    maxAge: 60 * 60 * 24 * 30});
                cookies.set('dark', "false", {
                    path: '/',
                    httpOnly: false,
                    secure: false,
                    maxAge: 60 * 60 * 24 * 30});
                cookies.set('theme', "modern", {
                    path: '/',
                    httpOnly: false,
                    secure: false,
                    maxAge: 60 * 60 * 24 * 30});
                cookies.set('cardDesign', "auto", {
                    path: '/',
                    httpOnly: false,
                    secure: false,
                    maxAge: 60 * 60 * 24 * 30});

                throw redirect(303, "/");
            }
            return {error: res["message"]};
        } catch (e) {
            console.log(e);
            return;
        }
	}
};