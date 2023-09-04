import { PUBLIC_FLASK_DOMAIN } from "$env/static/public";
import { redirect } from "@sveltejs/kit";

export const actions = {
    default: async ({ cookies, request }) => {
        const data = await request.formData();
        console.log(data);
        console.log(data.get("username"))

        let change;

        if (data.get("change") === "true") {
            change = 1;
        }
        else if (data.get("change") === "false") {
            change = 0;
        }

        const res = await fetch(`${PUBLIC_FLASK_DOMAIN}/svelteLogin`, {
            method: 'POST',
            body: JSON.stringify({
                "username": data.get("username"),
                "password": data.get("password"),
                "change": change,
                "pass": data.get("pass"),
                "passCon": data.get("passCon")
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        });

        console.log(res);

        if (res["success"] == true) {
            throw redirect(300, "/");
        }
        return res;

    }
};