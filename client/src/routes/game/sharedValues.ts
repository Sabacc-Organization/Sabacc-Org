import { Socket, io } from "socket.io-client";
import { writable, derived, type Writable } from "svelte/store";
import { page } from '$app/stores';

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

export function resetGameStores() {
  socket.set(null);
  game_variant.set(null);
  username.set(null);
  password.set(null);
  dark.set(null);
  theme.set(null);
  cardDesign.set(null);

//   game_id.set(null);
  dataToRender.set(false);
  header.set("");

  game.set({
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

  orderedPlayers.set([]);
  greatestBet.set(0);

  user_id.set(-1);
  u_dex.set(-1);

  activePlayers.set([]);
  thisPlayer.set(null);

  turnSound.set(null);

  isWaitingOnClick.set(false);
  backupServerInfo.set(null);
  movesDone.set(0);

  betCreds.set(null);
  betErr.set("");
  raising.set(false);

  chipInput.set(false);
  raiseAmount.set(0);
  followAmount.set(0);
  potsActive.set(false);

  cardBool.set(false);
  alderaanActive.set(false);

  tradeType.set("none");
  tradeCard.set({});

  shiftActive.set(false);

  currentMove.set(null);
  playbackInput.set(null);
}