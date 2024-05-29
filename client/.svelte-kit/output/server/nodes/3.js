

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/game/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/3.CDy7JezY.js","_app/immutable/chunks/scheduler.DFkagfZI.js","_app/immutable/chunks/index.C2iL-XhR.js","_app/immutable/chunks/each.D6YF6ztN.js","_app/immutable/chunks/stores.BJH6eBSf.js","_app/immutable/chunks/entry.CkW9y3TV.js","_app/immutable/chunks/js.cookie.Cz0CWeBA.js","_app/immutable/chunks/index.CGwCSIWv.js"];
export const stylesheets = ["_app/immutable/assets/3.DSPI_kwT.css"];
export const fonts = [];
