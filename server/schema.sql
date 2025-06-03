 CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
)

CREATE TABLE traditional_games (
    game_id SERIAL PRIMARY KEY,
    players TEXT, -- TraditionalPlayer[]
    hand_pot INTEGER NOT NULL DEFAULT 0,
    sabacc_pot INTEGER NOT NULL DEFAULT 0,
    phase TEXT NOT NULL DEFAULT 'betting',
    deck TEXT, -- TraditionalCard[]
    player_turn INTEGER,
    p_act TEXT,
    cycle_count INTEGER NOT NULL DEFAULT 0,
    shift BOOLEAN NOT NULL DEFAULT FALSE,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    settings TEXT NOT NULL DEFAULT '{"BigBlind": 2, "SmallBlind": 1, "HandPotAnte": 5, "SabaccPotAnte": 10, "StartingCredits": 1000, "PokerStyleBetting": false}',
    created_at TEXT, -- ISO 8601 (UTC)
    move_history TEXT -- json[]
)

CREATE TABLE corellian_spike_games (
    game_id SERIAL PRIMARY KEY,
    players TEXT, -- CorellianSpikePlayer[]
    hand_pot INTEGER NOT NULL DEFAULT 0,
    sabacc_pot INTEGER NOT NULL DEFAULT 0,
    phase TEXT NOT NULL DEFAULT 'card',
    deck TEXT, -- CorellianSpikeCard[]
    discard_pile TEXT, -- CorellianSpikeCard[]
    player_turn INTEGER,
    p_act TEXT,
    cycle_count INTEGER NOT NULL DEFAULT 0,
    shift BOOLEAN NOT NULL DEFAULT FALSE,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    settings TEXT NOT NULL DEFAULT '{"BigBlind": 2, "SmallBlind": 1, "HandPotAnte": 5, "HandRanking": "Wayne", "DeckDrawCost": 5, "DiscardCosts": [15, 20, 25], "DeckTradeCost": 10, "SabaccPotAnte": 10, "DiscardDrawCost": 10, "StartingCredits": 1000, "DiscardTradeCost": 15, "PokerStyleBetting": false}',
    created_at TEXT, -- ISO 8601 (UTC)
    move_history TEXT -- json[]
)

CREATE TABLE kessel_games (
    game_id SERIAL PRIMARY KEY,
    players TEXT, -- KesselPlayer[]
    phase TEXT NOT NULL DEFAULT 'draw',
    dice TEXT NOT NULL DEFAULT '1,1', -- INTEGER[]
    positivedeck TEXT, -- KesselCard[]
    negativedeck TEXT, -- KesselCard[]
    positivediscard TEXT, -- KesselCard[]
    negativediscard TEXT, -- KesselCard[]
    activeshifttokens TEXT, -- TEXT[]
    player_turn INTEGER,
    p_act TEXT,
    cycle_count INTEGER NOT NULL DEFAULT 0,
    shift BOOLEAN NOT NULL DEFAULT FALSE,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    settings TEXT NOT NULL DEFAULT '{"startingChips": 8, "playersChooseShiftTokens": false}',
    created_at TEXT, -- ISO 8601 (UTC)
    move_history TEXT -- json[]
)