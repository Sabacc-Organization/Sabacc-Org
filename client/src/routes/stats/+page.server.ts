/** @type {import('./$types').PageServerLoad} */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export async function load({ cookies, platform }) {
    try {
        const response = await fetch(BACKEND_URL + "/stats", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });

        const stats = await response.json();
        
        return {
            stats: stats
        }
    } catch (e) {
        console.log(e);
        return {
            stats: null
        }
    }
}