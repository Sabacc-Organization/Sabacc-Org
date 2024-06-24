

export const index = 10;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/settings/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/10.DDczPdz0.js","_app/immutable/chunks/scheduler.QKfR1-GZ.js","_app/immutable/chunks/index.BIyETQvx.js","_app/immutable/chunks/index.B033ejRg.js","_app/immutable/chunks/js.cookie.Cz0CWeBA.js"];
export const stylesheets = [];
export const fonts = [];
