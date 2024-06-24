import { c as create_ssr_component } from "../../chunks/ssr.js";
import Cookies from "js-cookie";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  Cookies.get("username");
  Cookies.get("password");
  Cookies.get("dark");
  Cookies.get("theme");
  return `${$$result.head += `<!-- HEAD_svelte-123kiar_START -->${$$result.title = `<title>Sabacc: Home</title>`, ""}<!-- HEAD_svelte-123kiar_END -->`, ""} ${`<h2 data-svelte-h="svelte-334ox">Sabacc</h2> <p data-svelte-h="svelte-15r2ptu">Step into the thrilling universe of Sabacc - the iconic space card game. Test your luck and skill as you navigate shifting card values in a race to achieve the coveted hand with a value of 23. Play for fortunes, strategize your moves, and experience the excitement of Sabacc like never before. Welcome to the ultimate online Sabacc destination, where the cards are your allies and the stakes are high. <b>Log In</b> or <b>Register</b> to play!</p> <div class="parent" data-svelte-h="svelte-1jzgfp1"><div class="child video vidOne"><iframe width="420" height="235" src="https://www.youtube.com/embed/ZjGsiEtmU-w" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> <p>Or read <a target="_blank" href="https://hyperspaceprops.com/wp-content/uploads/2021/11/Rebels-Inspired-Sabacc-Deck-Rules.pdf">this</a> for a comprehensive rulebook.</p></div> <div class="child video"><p>Learn more about this web application:</p> <iframe width="420" height="235" src="https://www.youtube.com/embed/tgRam9fhVJQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div></div> <iframe width="560" height="315" src="https://www.youtube.com/embed/T4V_vwR2pnw?autoplay=1&mute=1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>`}`;
});
export {
  Page as default
};
