/** @type {import('./$types').PageServerLoad} */

import { redirect } from "@sveltejs/kit";

export async function load({ cookies }) {
    cookies.delete('username', {
        path: '/',
        httpOnly: false,
        secure: false,
    });
    cookies.delete('password', {
        path: '/',
        httpOnly: false,
        secure: false,
    });
    cookies.delete('dark', {
        path: '/',
        httpOnly: false,
        secure: false,
    });
    cookies.delete('theme', {
        path: '/',
        httpOnly: false,
        secure: false,
    });
    cookies.delete('cardDesign', {
        path: '/',
        httpOnly: false,
        secure: false,
    });
}
