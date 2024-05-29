export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["classic.css","dark.css","favicon.png","images/Sabacc.png","images/SabaccIcon.png","images/alderaan.png","images/alderaanExplode.webp","images/imperial-credit.svg","images/octogonal-poker-table.svg","images/poker_table.jpeg","images/rebels-card-back.png","images/rebels_pot.jpeg","images/red_poker_table.jpeg","images/solo-card-back.png","modern-theme-images/+1 Circle.png","modern-theme-images/+1 Square.png","modern-theme-images/+1 Triangle.png","modern-theme-images/+10 Circle.png","modern-theme-images/+10 Square.png","modern-theme-images/+10 Triangle.png","modern-theme-images/+2 Circle.png","modern-theme-images/+2 Square.png","modern-theme-images/+2 Triangle.png","modern-theme-images/+3 Circle.png","modern-theme-images/+3 Square.png","modern-theme-images/+3 Triangle.png","modern-theme-images/+4 Circle.png","modern-theme-images/+4 Square.png","modern-theme-images/+4 Triangle.png","modern-theme-images/+5 Circle.png","modern-theme-images/+5 Square.png","modern-theme-images/+5 Triangle.png","modern-theme-images/+6 Circle.png","modern-theme-images/+6 Square.png","modern-theme-images/+6 Triangle.png","modern-theme-images/+7 Circle.png","modern-theme-images/+7 Square.png","modern-theme-images/+7 Triangle.png","modern-theme-images/+8 Circle.png","modern-theme-images/+8 Square.png","modern-theme-images/+8 Triangle.png","modern-theme-images/+9 Circle.png","modern-theme-images/+9 Square.png","modern-theme-images/+9 Triangle.png","modern-theme-images/-1 Circle.png","modern-theme-images/-1 Square.png","modern-theme-images/-1 Triangle.png","modern-theme-images/-10 Circle.png","modern-theme-images/-10 Square.png","modern-theme-images/-10 Triangle.png","modern-theme-images/-2 Circle.png","modern-theme-images/-2 Square.png","modern-theme-images/-2 Triangle.png","modern-theme-images/-3 Circle.png","modern-theme-images/-3 Square.png","modern-theme-images/-3 Triangle.png","modern-theme-images/-4 Circle.png","modern-theme-images/-4 Square.png","modern-theme-images/-4 Triangle.png","modern-theme-images/-5 Circle.png","modern-theme-images/-5 Square.png","modern-theme-images/-5 Triangle.png","modern-theme-images/-6 Circle.png","modern-theme-images/-6 Square.png","modern-theme-images/-6 Triangle.png","modern-theme-images/-7 Circle.png","modern-theme-images/-7 Square.png","modern-theme-images/-7 Triangle.png","modern-theme-images/-8 Circle.png","modern-theme-images/-8 Square.png","modern-theme-images/-8 Triangle.png","modern-theme-images/-9 Circle.png","modern-theme-images/-9 Square.png","modern-theme-images/-9 Triangle.png","modern-theme-images/0 Sylop.png","modern-theme-images/Attribution-ShareAlike CC BY-SA.png","modern-theme-images/Back.png","modern-theme-images/Credit Bronze.png","modern-theme-images/Credit Gold.png","modern-theme-images/Credit Silver.png","modern-theme-images/License.pdf","modern-theme-images/Playing Sabacc on Roll20.pdf","modern-theme-images/Sabacc Dealer Puck.png","modern-theme-images/Sabacc Set.png","modern-theme-images/Sabacc Table.jpg","modern-theme-images/Sabacc.pdf","modern-theme-images/SabaccTable-NoBackground.png","modern-theme-images/Spike Die Side 1.png","modern-theme-images/Spike Die Side 2.png","modern-theme-images/Spike Die Side 3.png","modern-theme-images/Spike Die Side 4.png","modern-theme-images/Spike Die Side 5.png","modern-theme-images/Spike Die Side 6.png","modern-theme-images/Yarith Bespin Casino_s Corellian Spike Rules.pdf","modern-theme-images/Zabaka_s Corellian Spike Rules.pdf","modern-theme-images/attribution-image.png","modern-theme-images/dark/b1.png","modern-theme-images/dark/b10.png","modern-theme-images/dark/b11.png","modern-theme-images/dark/b12.png","modern-theme-images/dark/b13.png","modern-theme-images/dark/b14.png","modern-theme-images/dark/b15.png","modern-theme-images/dark/b2.png","modern-theme-images/dark/b3.png","modern-theme-images/dark/b4.png","modern-theme-images/dark/b5.png","modern-theme-images/dark/b6.png","modern-theme-images/dark/b7.png","modern-theme-images/dark/b8.png","modern-theme-images/dark/b9.png","modern-theme-images/dark/g1.png","modern-theme-images/dark/g10.png","modern-theme-images/dark/g11.png","modern-theme-images/dark/g12.png","modern-theme-images/dark/g13.png","modern-theme-images/dark/g14.png","modern-theme-images/dark/g15.png","modern-theme-images/dark/g2.png","modern-theme-images/dark/g3.png","modern-theme-images/dark/g4.png","modern-theme-images/dark/g5.png","modern-theme-images/dark/g6.png","modern-theme-images/dark/g7.png","modern-theme-images/dark/g8.png","modern-theme-images/dark/g9.png","modern-theme-images/dark/p-11.png","modern-theme-images/dark/p-13.png","modern-theme-images/dark/p-14.png","modern-theme-images/dark/p-15.png","modern-theme-images/dark/p-17.png","modern-theme-images/dark/p-2.png","modern-theme-images/dark/p-8.png","modern-theme-images/dark/p0.png","modern-theme-images/dark/r1.png","modern-theme-images/dark/r10.png","modern-theme-images/dark/r11.png","modern-theme-images/dark/r12.png","modern-theme-images/dark/r13.png","modern-theme-images/dark/r14.png","modern-theme-images/dark/r15.png","modern-theme-images/dark/r2.png","modern-theme-images/dark/r3.png","modern-theme-images/dark/r4.png","modern-theme-images/dark/r5.png","modern-theme-images/dark/r6.png","modern-theme-images/dark/r7.png","modern-theme-images/dark/r8.png","modern-theme-images/dark/r9.png","modern-theme-images/dark/y1.png","modern-theme-images/dark/y10.png","modern-theme-images/dark/y11.png","modern-theme-images/dark/y12.png","modern-theme-images/dark/y13.png","modern-theme-images/dark/y14.png","modern-theme-images/dark/y15.png","modern-theme-images/dark/y2.png","modern-theme-images/dark/y3.png","modern-theme-images/dark/y4.png","modern-theme-images/dark/y5.png","modern-theme-images/dark/y6.png","modern-theme-images/dark/y7.png","modern-theme-images/dark/y8.png","modern-theme-images/dark/y9.png","modern-theme-images/light/b1.png","modern-theme-images/light/b10.png","modern-theme-images/light/b11.png","modern-theme-images/light/b12.png","modern-theme-images/light/b13.png","modern-theme-images/light/b14.png","modern-theme-images/light/b15.png","modern-theme-images/light/b2.png","modern-theme-images/light/b3.png","modern-theme-images/light/b4.png","modern-theme-images/light/b5.png","modern-theme-images/light/b6.png","modern-theme-images/light/b7.png","modern-theme-images/light/b8.png","modern-theme-images/light/b9.png","modern-theme-images/light/g1.png","modern-theme-images/light/g10.png","modern-theme-images/light/g11.png","modern-theme-images/light/g12.png","modern-theme-images/light/g13.png","modern-theme-images/light/g14.png","modern-theme-images/light/g15.png","modern-theme-images/light/g2.png","modern-theme-images/light/g3.png","modern-theme-images/light/g4.png","modern-theme-images/light/g5.png","modern-theme-images/light/g6.png","modern-theme-images/light/g7.png","modern-theme-images/light/g8.png","modern-theme-images/light/g9.png","modern-theme-images/light/p-11.png","modern-theme-images/light/p-13.png","modern-theme-images/light/p-14.png","modern-theme-images/light/p-15.png","modern-theme-images/light/p-17.png","modern-theme-images/light/p-2.png","modern-theme-images/light/p-8.png","modern-theme-images/light/p0.png","modern-theme-images/light/r1.png","modern-theme-images/light/r10.png","modern-theme-images/light/r11.png","modern-theme-images/light/r12.png","modern-theme-images/light/r13.png","modern-theme-images/light/r14.png","modern-theme-images/light/r15.png","modern-theme-images/light/r2.png","modern-theme-images/light/r3.png","modern-theme-images/light/r4.png","modern-theme-images/light/r5.png","modern-theme-images/light/r6.png","modern-theme-images/light/r7.png","modern-theme-images/light/r8.png","modern-theme-images/light/r9.png","modern-theme-images/light/y1.png","modern-theme-images/light/y10.png","modern-theme-images/light/y11.png","modern-theme-images/light/y12.png","modern-theme-images/light/y13.png","modern-theme-images/light/y14.png","modern-theme-images/light/y15.png","modern-theme-images/light/y2.png","modern-theme-images/light/y3.png","modern-theme-images/light/y4.png","modern-theme-images/light/y5.png","modern-theme-images/light/y6.png","modern-theme-images/light/y7.png","modern-theme-images/light/y8.png","modern-theme-images/light/y9.png","modern-theme-images/pescado/b1.png","modern-theme-images/pescado/b10.png","modern-theme-images/pescado/b11.png","modern-theme-images/pescado/b12.png","modern-theme-images/pescado/b13.png","modern-theme-images/pescado/b14.png","modern-theme-images/pescado/b15.png","modern-theme-images/pescado/b2.png","modern-theme-images/pescado/b3.png","modern-theme-images/pescado/b4.png","modern-theme-images/pescado/b5.png","modern-theme-images/pescado/b6.png","modern-theme-images/pescado/b7.png","modern-theme-images/pescado/b8.png","modern-theme-images/pescado/b9.png","modern-theme-images/pescado/back.png","modern-theme-images/pescado/g1.png","modern-theme-images/pescado/g10.png","modern-theme-images/pescado/g11.png","modern-theme-images/pescado/g12.png","modern-theme-images/pescado/g13.png","modern-theme-images/pescado/g14.png","modern-theme-images/pescado/g15.png","modern-theme-images/pescado/g2.png","modern-theme-images/pescado/g3.png","modern-theme-images/pescado/g4.png","modern-theme-images/pescado/g5.png","modern-theme-images/pescado/g6.png","modern-theme-images/pescado/g7.png","modern-theme-images/pescado/g8.png","modern-theme-images/pescado/g9.png","modern-theme-images/pescado/p-10.png","modern-theme-images/pescado/p-11.png","modern-theme-images/pescado/p-13.png","modern-theme-images/pescado/p-14.png","modern-theme-images/pescado/p-15.png","modern-theme-images/pescado/p-17.png","modern-theme-images/pescado/p-2.png","modern-theme-images/pescado/p-8.png","modern-theme-images/pescado/p0.png","modern-theme-images/pescado/r1.png","modern-theme-images/pescado/r10.png","modern-theme-images/pescado/r11.png","modern-theme-images/pescado/r12.png","modern-theme-images/pescado/r13.png","modern-theme-images/pescado/r14.png","modern-theme-images/pescado/r15.png","modern-theme-images/pescado/r2.png","modern-theme-images/pescado/r3.png","modern-theme-images/pescado/r4.png","modern-theme-images/pescado/r5.png","modern-theme-images/pescado/r6.png","modern-theme-images/pescado/r7.png","modern-theme-images/pescado/r8.png","modern-theme-images/pescado/r9.png","modern-theme-images/pescado/y1.png","modern-theme-images/pescado/y10.png","modern-theme-images/pescado/y11.png","modern-theme-images/pescado/y12.png","modern-theme-images/pescado/y13.png","modern-theme-images/pescado/y14.png","modern-theme-images/pescado/y15.png","modern-theme-images/pescado/y2.png","modern-theme-images/pescado/y3.png","modern-theme-images/pescado/y4.png","modern-theme-images/pescado/y5.png","modern-theme-images/pescado/y6.png","modern-theme-images/pescado/y7.png","modern-theme-images/pescado/y8.png","modern-theme-images/pescado/y9.png","modern.css","move-sound.mp3","rebels.css","solo.css","styles.css"]),
	mimeTypes: {".css":"text/css",".png":"image/png",".webp":"image/webp",".svg":"image/svg+xml",".jpeg":"image/jpeg",".pdf":"application/pdf",".jpg":"image/jpeg",".mp3":"audio/mpeg"},
	_: {
		client: {"start":"_app/immutable/entry/start.Dafkw4SY.js","app":"_app/immutable/entry/app.BhbKo8Ft.js","imports":["_app/immutable/entry/start.Dafkw4SY.js","_app/immutable/chunks/entry.CkW9y3TV.js","_app/immutable/chunks/scheduler.DFkagfZI.js","_app/immutable/entry/app.BhbKo8Ft.js","_app/immutable/chunks/scheduler.DFkagfZI.js","_app/immutable/chunks/index.C2iL-XhR.js"],"stylesheets":[],"fonts":[],"uses_env_dynamic_public":false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js')),
			__memo(() => import('./nodes/5.js')),
			__memo(() => import('./nodes/6.js')),
			__memo(() => import('./nodes/7.js')),
			__memo(() => import('./nodes/8.js')),
			__memo(() => import('./nodes/9.js')),
			__memo(() => import('./nodes/10.js'))
		],
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			},
			{
				id: "/game",
				pattern: /^\/game\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/game/[game_id]",
				pattern: /^\/game\/([^/]+?)\/?$/,
				params: [{"name":"game_id","optional":false,"rest":false,"chained":false}],
				page: { layouts: [0,], errors: [1,], leaf: 4 },
				endpoint: null
			},
			{
				id: "/host",
				pattern: /^\/host\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 5 },
				endpoint: null
			},
			{
				id: "/how-to-play",
				pattern: /^\/how-to-play\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 6 },
				endpoint: null
			},
			{
				id: "/login",
				pattern: /^\/login\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 7 },
				endpoint: null
			},
			{
				id: "/logout",
				pattern: /^\/logout\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 8 },
				endpoint: null
			},
			{
				id: "/register",
				pattern: /^\/register\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 9 },
				endpoint: null
			},
			{
				id: "/settings",
				pattern: /^\/settings\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 10 },
				endpoint: null
			}
		],
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
