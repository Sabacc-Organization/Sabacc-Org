/** @type {import('./$types').PageServerLoad} */

import { redirect } from "@sveltejs/kit";

export async function load({ cookies }) {
    cookies.delete('username', { path: '/' });
    cookies.delete('password', { path: '/' });
    cookies.delete('dark', { path: '/' });
    cookies.delete('theme', { path: '/' });
    cookies.delete('cardDesign', { path: '/' });
}
