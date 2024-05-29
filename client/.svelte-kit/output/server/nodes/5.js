

export const index = 5;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/host/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/5.B5GsIYDF.js","_app/immutable/chunks/scheduler.DFkagfZI.js","_app/immutable/chunks/index.C2iL-XhR.js","_app/immutable/chunks/js.cookie.Cz0CWeBA.js","_app/immutable/chunks/index.B033ejRg.js"];
export const stylesheets = [];
export const fonts = [];
