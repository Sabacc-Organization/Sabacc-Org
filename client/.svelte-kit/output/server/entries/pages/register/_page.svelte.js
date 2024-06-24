import { c as create_ssr_component, d as add_attribute, e as escape } from "../../../chunks/ssr.js";
import "js-cookie";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let username = "";
  let password = "";
  let confirmPassword = "";
  let errorMsg = "";
  return `${$$result.head += `<!-- HEAD_svelte-6hrwf1_START -->${$$result.title = `<title>Sabacc: Register</title>`, ""}<!-- HEAD_svelte-6hrwf1_END -->`, ""} <input type="text" class="form-control form-group" name="username" placeholder="Username" autocomplete="off" required${add_attribute("value", username, 0)}> <br> <input type="password" class="form-control form-group" name="password" placeholder="Password" autocomplete="off" required${add_attribute("value", password, 0)}> <br> <input type="password" class="form-control form-group" name="confirmation" placeholder="Confirm Password" autocomplete="off" required${add_attribute("value", confirmPassword, 0)}> <br> <button type="submit" class="btn btn-primary" data-svelte-h="svelte-1t3jjdh">Register</button> <p>${escape(errorMsg)}</p>`;
});
export {
  Page as default
};
