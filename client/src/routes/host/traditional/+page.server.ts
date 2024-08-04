/** @type {import('./$types').Actions} */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export const actions = {
	default: async ({cookies, request, url}) => {
        const formData = await request.formData();
        const player2 = formData.get('player2')?.toString();
        const player3 = formData.get('player3')?.toString();
        const player4 = formData.get('player4')?.toString();
        const player5 = formData.get('player5')?.toString();
        const player6 = formData.get('player6')?.toString();
        const player7 = formData.get('player7')?.toString();
        const player8 = formData.get('player8')?.toString();

        const username = cookies.get("username");
        const password = cookies.get("password");

        let players = [];
        if (player2) {
            players.push(player2);
        }

        if (player3) {
            players.push(player3);
        }

        if (player4) {
            players.push(player4);
        }
        
        if (player5) {
            players.push(player5);
        }
        
        if (player6) {
            players.push(player6);
        }
        
        if (player7) {
            players.push(player7);
        }

        if (player8) {
            players.push(player8);
        }

        // Standard player vailidity checks
        
        if (players.length < 1) {
            return {error: "You cannot play alone"}
        }

        if (players.indexOf(username!) != -1) {
            return {error: "You cannot play with yourself"};
        }

        for (let i = 0; i < players.length; i++) {
            if (players.lastIndexOf(players[i]) != i) {
                return {error: "All players must be different"};
            }
        }

        try {

            let requestData = {
                "username": username,
                "password": password,
                "players": players,
                "game_variant": "traditional"
            }

            const response = await fetch(BACKEND_URL + "/host", {
                method: 'POST', // Set the method to POST
                headers: {
                    'Content-Type': 'application/json' // Set the headers appropriately
                },
                body: JSON.stringify(requestData) // Convert your data to JSON
            });

            let res = await response.json();
            if (response.ok) {
                console.log("ok")
                throw redirect(303, res["redirect"])
            }
            else {
                console.log(res["message"])
                return {error: res["message"]};
            }
        } catch (e) {
            console.log(e);
            return {error: e};
        }
	}
};