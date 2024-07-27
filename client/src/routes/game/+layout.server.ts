/** @type {import('./$types').PageServerLoad} */


export async function load({ cookies }) {

    return {
        password: cookies.get("password"),
    }
}