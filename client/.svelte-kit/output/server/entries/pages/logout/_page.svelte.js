import { c as create_ssr_component } from "../../../chunks/ssr.js";
import "../../../chunks/client.js";
import Cookies from "js-cookie";
function customRedirect(url) {
  window.location.href = url;
}
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  const FRONTEND_URL = "https://sabacc.pages.dev";
  Cookies.remove("username");
  Cookies.remove("password");
  Cookies.remove("theme");
  Cookies.remove("dark");
  customRedirect(FRONTEND_URL);
  return `${$$result.head += `<!-- HEAD_svelte-1tibigw_START -->${$$result.title = `<title>Sabacc: Logout</title>`, ""}<!-- HEAD_svelte-1tibigw_END -->`, ""}`;
});
export {
  Page as default
};
