export const ssr = false;
export const prerender = true;

export function load({ cookies }) {
	const user_id = cookies.get("user_id");
    const o = cookies.get("o");

    cookies.set('o', 'blahblah', { path: '/' });

	return {
		user_id,
        o
	};
}