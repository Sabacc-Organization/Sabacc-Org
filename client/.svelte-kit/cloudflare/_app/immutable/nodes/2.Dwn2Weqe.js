import{s as V,n as P,o as z,a as F}from"../chunks/scheduler.DFkagfZI.js";import{S as N,i as O,s as k,n as I,h as U,d as f,c as T,j as p,e as b,a as v,g as R,b as L,k as _,r as $,f as E,o as H,p as S,q as Y}from"../chunks/index.C2iL-XhR.js";import{e as j}from"../chunks/each.D6YF6ztN.js";import{a as M}from"../chunks/js.cookie.Cz0CWeBA.js";import{c as J,b as K}from"../chunks/index.B033ejRg.js";function B(d,a,h){const n=d.slice();return n[7]=a[h],n[9]=h,n}function Q(d){let a,h="Your Active Games",n,i,r,t,l,g="<th>Players</th> <th>Turn</th> <th>Game Link</th>",w,u=j(d[1].games),s=[];for(let e=0;e<u.length;e+=1)s[e]=G(B(d,u,e));return{c(){a=b("h2"),a.textContent=h,n=k(),i=b("br"),r=k(),t=b("table"),l=b("tr"),l.innerHTML=g,w=k();for(let e=0;e<s.length;e+=1)s[e].c()},l(e){a=v(e,"H2",{"data-svelte-h":!0}),R(a)!=="svelte-1tmbhrq"&&(a.textContent=h),n=T(e),i=v(e,"BR",{}),r=T(e),t=v(e,"TABLE",{});var c=L(t);l=v(c,"TR",{"data-svelte-h":!0}),R(l)!=="svelte-1nlk7n2"&&(l.innerHTML=g),w=T(c);for(let o=0;o<s.length;o+=1)s[o].l(c);c.forEach(f)},m(e,c){p(e,a,c),p(e,n,c),p(e,i,c),p(e,r,c),p(e,t,c),_(t,l),_(t,w);for(let o=0;o<s.length;o+=1)s[o]&&s[o].m(t,null)},p(e,c){if(c&2){u=j(e[1].games);let o;for(o=0;o<u.length;o+=1){const C=B(e,u,o);s[o]?s[o].p(C,c):(s[o]=G(C),s[o].c(),s[o].m(t,null))}for(;o<s.length;o+=1)s[o].d(1);s.length=u.length}},d(e){e&&(f(a),f(n),f(i),f(r),f(t)),$(s,e)}}}function W(d){let a,h="Sabacc",n,i,r="Step into the thrilling universe of Sabacc - the iconic space card game. Test your luck and skill as you navigate shifting card values in a race to achieve the coveted hand with a value of 23. Play for fortunes, strategize your moves, and experience the excitement of Sabacc like never before. Welcome to the ultimate online Sabacc destination, where the cards are your allies and the stakes are high. <b>Log In</b> or <b>Register</b> to play!",t,l,g='<div class="child video vidOne"><iframe width="420" height="235" src="https://www.youtube.com/embed/ZjGsiEtmU-w" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen=""></iframe> <p>Or read <a target="_blank" href="https://hyperspaceprops.com/wp-content/uploads/2021/11/Rebels-Inspired-Sabacc-Deck-Rules.pdf">this</a> for a comprehensive rulebook.</p></div> <div class="child video"><p>Learn more about this web application:</p> <iframe width="420" height="235" src="https://www.youtube.com/embed/tgRam9fhVJQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen=""></iframe></div>',w,u,s;return{c(){a=b("h2"),a.textContent=h,n=k(),i=b("p"),i.innerHTML=r,t=k(),l=b("div"),l.innerHTML=g,w=k(),u=b("iframe"),this.h()},l(e){a=v(e,"H2",{"data-svelte-h":!0}),R(a)!=="svelte-334ox"&&(a.textContent=h),n=T(e),i=v(e,"P",{"data-svelte-h":!0}),R(i)!=="svelte-15r2ptu"&&(i.innerHTML=r),t=T(e),l=v(e,"DIV",{class:!0,"data-svelte-h":!0}),R(l)!=="svelte-1jzgfp1"&&(l.innerHTML=g),w=T(e),u=v(e,"IFRAME",{width:!0,height:!0,src:!0,title:!0,frameborder:!0,allow:!0}),L(u).forEach(f),this.h()},h(){E(l,"class","parent"),E(u,"width","560"),E(u,"height","315"),F(u.src,s="https://www.youtube.com/embed/T4V_vwR2pnw?autoplay=1&mute=1")||E(u,"src",s),E(u,"title","YouTube video player"),E(u,"frameborder","0"),E(u,"allow","accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"),u.allowFullscreen=!0},m(e,c){p(e,a,c),p(e,n,c),p(e,i,c),p(e,t,c),p(e,l,c),p(e,w,c),p(e,u,c)},p:P,d(e){e&&(f(a),f(n),f(i),f(t),f(l),f(w),f(u))}}}function G(d){let a,h,n=d[1].usernames[d[9]]+"",i,r,t,l=d[1].player_turns[d[9]]+"",g,w,u,s,e,c,o,C;return{c(){a=b("tr"),h=b("td"),i=H(n),r=k(),t=b("td"),g=H(l),w=H("'s"),u=k(),s=b("td"),e=b("a"),c=H("Play"),C=k(),this.h()},l(y){a=v(y,"TR",{});var m=L(a);h=v(m,"TD",{});var x=L(h);i=S(x,n),x.forEach(f),r=T(m),t=v(m,"TD",{});var D=L(t);g=S(D,l),w=S(D,"'s"),D.forEach(f),u=T(m),s=v(m,"TD",{});var q=L(s);e=v(q,"A",{href:!0});var A=L(e);c=S(A,"Play"),A.forEach(f),q.forEach(f),C=T(m),m.forEach(f),this.h()},h(){E(e,"href",o="/game/"+d[7].id)},m(y,m){p(y,a,m),_(a,h),_(h,i),_(a,r),_(a,t),_(t,g),_(t,w),_(a,u),_(a,s),_(s,e),_(e,c),_(a,C)},p(y,m){m&2&&n!==(n=y[1].usernames[y[9]]+"")&&Y(i,n),m&2&&l!==(l=y[1].player_turns[y[9]]+"")&&Y(g,l),m&2&&o!==(o="/game/"+y[7].id)&&E(e,"href",o)},d(y){y&&f(a)}}}function Z(d){let a,h;function n(t,l){if(t[0]===!1)return W;if(t[0])return Q}let i=n(d),r=i&&i(d);return{c(){a=k(),r&&r.c(),h=I(),this.h()},l(t){U("svelte-123kiar",document.head).forEach(f),a=T(t),r&&r.l(t),h=I(),this.h()},h(){document.title="Sabacc: Home"},m(t,l){p(t,a,l),r&&r.m(t,l),p(t,h,l)},p(t,[l]){i===(i=n(t))&&r?r.p(t,l):(r&&r.d(1),r=i&&i(t),r&&(r.c(),r.m(h.parentNode,h)))},i:P,o:P,d(t){t&&(f(a),f(h)),r&&r.d(t)}}}function X(d,a,h){const n="http://127.0.0.1:5000";let i=!1,r=M.get("username"),t=M.get("password");M.get("dark"),M.get("theme");let l={games:[]};return z(async()=>{h(0,i=await J(r,t,n)),i&&h(1,l=await K(r,t,n+"/"))}),[i,l]}class ie extends N{constructor(a){super(),O(this,a,X,Z,V,{})}}export{ie as component};