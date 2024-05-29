import { c as create_ssr_component, b as subscribe } from "../../chunks/ssr.js";
import Cookies from "js-cookie";
import { p as page } from "../../chunks/stores.js";
const Layout = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $page, $$unsubscribe_page;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  Cookies.get("username");
  Cookies.get("password");
  let dark = Cookies.get("dark");
  Cookies.get("theme");
  $$unsubscribe_page();
  return `${$$result.head += `<!-- HEAD_svelte-z6mqcs_START -->${$$result.title = `<title>Sabacc</title>`, ""}<!-- HEAD_svelte-z6mqcs_END -->`, ""} <html lang="en"><head><meta charset="utf-8"> <meta name="viewport" content="initial-scale=1, width=device-width"> <meta name="description" content="Play Sabacc!">  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js" integrity="sha512-894YE6QWD5I59HgZOGReFYm4dnWc1Qt5NtvYSaNcOP+u1T9qYdvdihz0PPSiiqn/+/3e7Jo4EaG7TubfWGUrMQ==" crossorigin="anonymous" referrerpolicy="no-referrer" data-svelte-h="svelte-eqbd2q"><\/script> <script src="https://code.jquery.com/ui/1.13.0/jquery-ui.js" data-svelte-h="svelte-npuxxw"><\/script> <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ/JpcUGGOn+Y7RsweNrtN/tE3MoK7ZeZDyx" crossorigin="anonymous" data-svelte-h="svelte-onl8fz"><\/script>  <script src="https://kit.fontawesome.com/75b19c7a56.js" crossorigin="anonymous" data-svelte-h="svelte-1ejep79"><\/script>  <link href="favicon.png" rel="icon">  <link href="/styles.css" rel="stylesheet"> ${`<link href="/rebels.css" rel="stylesheet">`}</head> <body><nav class="${[
    "navbar navbar-expand-md border",
    (dark != "true" ? "navbar-light" : "") + " " + (dark != "true" ? "bg-light" : "") + " " + (dark === "true" ? "navbar-dark" : "") + " " + (dark === "true" ? "bg-dark" : "")
  ].join(" ").trim()}"><a class="navbar-brand" href="/" data-svelte-h="svelte-18s5wb3"><span class="blue">Sabacc</span></a> <button aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation" class="navbar-toggler" data-target="#navbar" data-toggle="collapse" type="button" data-svelte-h="svelte-1shx7s4"><span class="navbar-toggler-icon"></span></button> <div class="nav nav-pills collapse navbar-collapse" id="navbar">${`<ul class="navbar-nav ml-auto mt-2"><li class="nav-item"><a class="${["nav-link", $page.url.pathname === "/how-to-play" ? "active" : ""].join(" ").trim()}" href="/how-to-play" data-svelte-h="svelte-1yugkry">How to Play</a></li> <li class="nav-item" data-svelte-h="svelte-n6230w"><a class="nav-link" href="https://discord.com/invite/AaYrNZjBus" target="_blank">Join the Discord</a></li> <li class="nav-item"><a class="${["nav-link", $page.url.pathname === "/register" ? "active" : ""].join(" ").trim()}" href="/register" data-svelte-h="svelte-1lxluz2">Register</a></li> <li class="nav-item"><a class="${["nav-link", $page.url.pathname === "/login" ? "active" : ""].join(" ").trim()}" href="/login" data-svelte-h="svelte-fgfbcw">Log In</a></li></ul>`}</div></nav> <main class="container-fluid p-5">${slots.default ? slots.default({}) : ``}</main></body></html>`;
});
export {
  Layout as default
};
