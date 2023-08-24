export function load({ cookies }) {
	const user_id = cookies.get("user_id");
    const username = cookies.get("username");
    const dark = cookies.get("dark");
    const theme = cookies.get("theme");

	return {
		user_id,
        username,
        dark,
        theme
	};
}