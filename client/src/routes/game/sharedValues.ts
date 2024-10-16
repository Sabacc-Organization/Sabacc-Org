import { Socket, io } from "socket.io-client";
import { writable, derived, type Writable } from "svelte/store";
import { page } from '$app/stores';

// URLs for Requests and Redirects
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
export const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

//socket.io
export const socket: Writable<Socket|null> = writable(null);

export const game_variant : Writable<string |null> = writable(null);
export const username     : Writable<string |null> = writable(null);
export const password     : Writable<string |null> = writable(null);
export const dark         : Writable<boolean|null> = writable(null);
export const theme        : Writable<string |null> = writable(null);
export const cardDesign   : Writable<string |null> = writable(null);

export const game_id = derived(page, (value) => value.params.game_id);

export const dataToRender = writable(false);
export const header = writable("");

export const game: Writable<{[id: string]: any}> = writable({
    "p_act": "",
    "players": [],
    "hand_pot": 0,
    "sabacc_pot": 0,
    "phase": "",
    "shift": 0,
    "player_turn": -1,
    "completed": 0,
    "cycle_count": 0
});

export const orderedPlayers: Writable<{[id: string]: any}[]> = writable([]);

export const greatestBet = writable(0);

export const user_id = writable(-1);
export const u_dex = writable(-1);

export const activePlayers: Writable<{[id: string]: any}[]> = writable([]);
export const thisPlayer = writable(null);

export const turnSound: Writable<HTMLAudioElement|null> = writable(null);

export const isWaitingOnClick = writable(false);

export const backupServerInfo = writable(null);
export const movesDone = writable(0);

// betting phase
export const betCreds: Writable<number|null> = writable(null);
export const betErr = writable("");

export const raising = writable(false);

export const chipInput = writable(false);
export const raiseAmount = writable(0);
export const followAmount = writable(0)
export const potsActive = writable(false);

// card phase
export const cardBool = writable(false);
export const alderaanActive = writable(false);

export const tradeType = writable("none");
export const tradeCard = writable({});

export const shiftActive = writable(false);

// playback
export const currentMove: Writable<number|null> = writable(null);
export const playbackInput: Writable<number|null> = writable(null);