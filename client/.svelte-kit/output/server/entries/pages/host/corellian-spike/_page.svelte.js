import { c as create_ssr_component, d as add_attribute, e as escape } from "../../../../chunks/ssr.js";
import Cookies from "js-cookie";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  Cookies.get("username");
  Cookies.get("password");
  Cookies.get("dark");
  Cookies.get("theme");
  let errorMsg = "";
  let player2 = "";
  return `${$$result.head += `<!-- HEAD_svelte-ri7zbw_START -->${$$result.title = `<title>Sabacc: Host</title>`, ""}<!-- HEAD_svelte-ri7zbw_END -->`, ""} <h2 data-svelte-h="svelte-1uccw09">Host a game of <b>Corellian Spike</b> Sabacc</h2> <br> <h5 data-svelte-h="svelte-t1gu5e">Who would you like to play Sabacc with? Enter your opponent&#39;s username.</h5> <input autocomplete="off" autofocus class="form-control form-group" id="player2" name="player2" placeholder="Player 2" type="text" required${add_attribute("value", player2, 0)}> ${``} ${``} ${``} ${``} ${``} ${``} <br> <button class="btn btn-primary" type="submit" data-svelte-h="svelte-1khyfp1">Play</button> <p>${escape(errorMsg)}</p>`;
});
export {
  Page as default
};
