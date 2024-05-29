import { c as create_ssr_component, d as add_attribute, e as escape } from "../../../chunks/ssr.js";
import Cookies from "js-cookie";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let username = "";
  let password = "";
  let errorMsg = "";
  Cookies.remove("username");
  Cookies.remove("password");
  return `${$$result.head += `<!-- HEAD_svelte-6vfb03_START -->${$$result.title = `<title>Sabacc: Login</title>`, ""}<!-- HEAD_svelte-6vfb03_END -->`, ""} <h1 data-svelte-h="svelte-1wsy7a9">Login</h1> <div><input autocomplete="off" class="form-control form-group" name="username" placeholder="Username" type="text" required${add_attribute("value", username, 0)}></div> <div><input class="form-control form-group" name="password" placeholder="Password" type="password" required${add_attribute("value", password, 0)}></div> <button class="btn btn-primary" type="submit" data-svelte-h="svelte-t8ps4p">Log in</button> <p>${escape(errorMsg)}</p>`;
});
export {
  Page as default
};
