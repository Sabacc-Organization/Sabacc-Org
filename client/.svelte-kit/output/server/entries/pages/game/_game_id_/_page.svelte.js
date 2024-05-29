import { c as create_ssr_component, b as subscribe, o as onDestroy, e as escape } from "../../../../chunks/ssr.js";
import { p as page } from "../../../../chunks/stores.js";
import Cookies from "js-cookie";
import "socket.io-client";
const css = {
  code: ".shift1.svelte-emteyc{background-color:#0cc23c}",
  map: null
};
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let game_id;
  let $page, $$unsubscribe_page;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  Cookies.get("username");
  Cookies.get("password");
  Cookies.get("dark") == "true";
  Cookies.get("cardDesign");
  Cookies.get("theme");
  let refreshInterval;
  onDestroy(() => {
    clearInterval(refreshInterval);
  });
  $$result.css.add(css);
  game_id = $page.params.game_id;
  $$unsubscribe_page();
  return `${$$result.head += `<!-- HEAD_svelte-1k8k4nw_START -->${$$result.title = `<title>Sabacc: Game ${escape(game_id)}</title>`, ""}<!-- HEAD_svelte-1k8k4nw_END -->`, ""} ${``}`;
});
export {
  Page as default
};
