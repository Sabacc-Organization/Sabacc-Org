// place files you want to import through the `$lib` alias in this folder.


/**
 * @param {string} username
 * @param {string} password
 * @param {string} BACKEND_URL
 */
export async function checkLogin(username, password, BACKEND_URL) {

    try {

        let requestData = {
            "username": username,
            "password": password
        }

        const response = await fetch(BACKEND_URL + "/login", {
            method: 'POST', // Set the method to POST
            headers: {
                'Content-Type': 'application/json' // Set the headers appropriately
            },
            body: JSON.stringify(requestData) // Convert your data to JSON
        });

        let res = await response.json();
        if (response.ok) {
            return true;
        }
        else {
            return false;
        }
    } catch (e) {
        console.log(e);
        return false;
    }
}


/**
 * @param {string} username
 * @param {string} password
 * @param {string} BACKEND_URL
 */
export async function backendPostRequest(username, password, BACKEND_URL) {

    try {

        let requestData = {
            "username": username,
            "password": password
        }

        const response = await fetch(BACKEND_URL, {
            method: 'POST', // Set the method to POST
            headers: {
                'Content-Type': 'application/json' // Set the headers appropriately
            },
            body: JSON.stringify(requestData) // Convert your data to JSON
        });

       return response.json();
    } catch (e) {
        console.log(e);
        return {};
    }
}

/**
 * @param {string} url
 */
export function customRedirect(url) {
    window.location.href = url;
}