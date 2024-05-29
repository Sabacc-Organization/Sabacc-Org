import { c as create_ssr_component, d as add_attribute } from "../../../chunks/ssr.js";
import Cookies from "js-cookie";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  Cookies.get("username");
  Cookies.get("password");
  let dark = Cookies.get("dark");
  dark = dark == "true";
  Cookies.get("theme");
  Cookies.get("cardDesign");
  return `${$$result.head += `<!-- HEAD_svelte-1h9z3p1_START -->${$$result.title = `<title>Sabacc: Settings</title>`, ""}<!-- HEAD_svelte-1h9z3p1_END -->`, ""} <h2 data-svelte-h="svelte-15f2bar">Settings</h2> <br> <div class="parent"><h5 class="child" data-svelte-h="svelte-uy1196">Dark Mode</h5>  <label class="switch child"><input name="dark" type="checkbox"${add_attribute("checked", dark, 1)}> <span class="slider round"></span></label></div> <br> <label for="cardDesign" data-svelte-h="svelte-qzu2py">Card Design</label> <select name="cardDesign" id="cardDesign"><option value="classic" data-svelte-h="svelte-1ja9xse">Classic</option><option value="auto" data-svelte-h="svelte-13uzty">Auto</option><option value="dark" data-svelte-h="svelte-6c4gk6">Dark</option><option value="light" data-svelte-h="svelte-yop7ea">Light</option><option value="pescado" data-svelte-h="svelte-uejfmk">Pescado</option></select> <br> <label for="theme" data-svelte-h="svelte-1uzaucu">Theme (Work in Progress)</label> <select name="theme" id="theme"><option value="modern" data-svelte-h="svelte-dpfcy">Modern</option><option value="rebels" data-svelte-h="svelte-4ssisi">Rebels</option><option value="solo" data-svelte-h="svelte-16kpcru">Solo</option><option value="classic" data-svelte-h="svelte-1ja9xse">Classic</option></select> <br> <br> <button type="button" class="btn btn-primary" data-svelte-h="svelte-1pa6p81">Save</button>`;
});
export {
  Page as default
};
