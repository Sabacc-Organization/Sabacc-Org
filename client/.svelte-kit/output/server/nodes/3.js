

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/game/_game_id_/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/3.C0Qw9MAF.js","_app/immutable/chunks/scheduler.QKfR1-GZ.js","_app/immutable/chunks/index.BIyETQvx.js","_app/immutable/chunks/each.D6YF6ztN.js","_app/immutable/chunks/stores.kWwb1NKH.js","_app/immutable/chunks/entry.CuRSDHTx.js","_app/immutable/chunks/js.cookie.Cz0CWeBA.js"];
export const stylesheets = ["_app/immutable/assets/3.DSPI_kwT.css"];
export const fonts = [];
