

export const index = 5;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/host/traditional/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/5.Cj1mP9Hh.js","_app/immutable/chunks/scheduler.QKfR1-GZ.js","_app/immutable/chunks/index.BIyETQvx.js","_app/immutable/chunks/js.cookie.Cz0CWeBA.js","_app/immutable/chunks/index.B033ejRg.js"];
export const stylesheets = [];
export const fonts = [];
