/** @type {import('./$types').PageServerLoad} */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export async function load({ cookies, platform, params }) {
    try {
        const username = params.username;
        
        const response = await fetch(BACKEND_URL + "/player", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username })
        });

        if (!response.ok) {
            return {
                playerData: null
            };
        }

        const playerData = await response.json();
        
        return {
            playerData: playerData
        };
    } catch (e) {
        console.log(e);
        return {
            playerData: null
        };
    }
}