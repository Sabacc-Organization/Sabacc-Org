

export const index = 6;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/how-to-play/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/6.kIXkBceD.js","_app/immutable/chunks/scheduler.DFkagfZI.js","_app/immutable/chunks/index.C2iL-XhR.js"];
export const stylesheets = [];
export const fonts = [];
