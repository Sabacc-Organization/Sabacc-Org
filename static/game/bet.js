$(document).ready(function() {

	// Define sockets
	var socket = io.connect('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev');
	var bet_socket = io('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev/bet');

	// Reduce website hackability by defining variables pulled from the HTML as soon as possible
	let game = document.getElementById("game");
	let player = document.getElementById("player");
	let opponent = document.getElementById("opponent");
	let userCredits = document.getElementById("credits").innerHTML;

	// Create variables off of attributes of "meta" variables
	let game_id = parseInt(game.getAttribute("game_id"));
	let phase = game.getAttribute("phase");
	let player1_bet = game.getAttribute("player1_bet");
	let player2_bet = game.getAttribute("player2_bet");
	let player_turn = parseInt(game.getAttribute("player_turn"));

	let playerID = parseInt(player.getAttribute("player_id"));
	let player_phrase = player.getAttribute("player");

	let opponent_id = parseInt(opponent.getAttribute("opponent_id"));
	let opponent_username = opponent.getAttribute("username");

	// Global Variables
	let fold_count = 0;

	// Define show/hide functions
	function show(id)
	{
		document.getElementById(id).hidden = false;
	}

	function hide(id)
	{
		document.getElementById(id).hidden = true;
	}

	// Hide HTML that must be hidden from the beginning

	if (phase === "betting")
	{
		// First player first turn
		if (player_turn === playerID && (player1_bet === "None" || player1_bet === "null") && (player2_bet === "None" || player2_bet === "null") && player_phrase === "player1")
		{
			hide("p2FollowBet");
			hide("betDiv");
			hide("followFollowRaiseActionDiv");
		}
		// Player 2 raised
		else if (player_turn === playerID && player1_bet != "None" && player1_bet != "null" && player2_bet != "None" && player2_bet != "null" && player_phrase === "player1")
		{
			document.getElementById("raiseCredits").innerHTML = game.getAttribute("player2_bet") + " credits";
			hide("p2FollowBet");
			hide("betDiv");
			hide("betActionDiv");
		}
		// Not your turn? Well then wait.
		else if (player_turn != playerID)
		{
			hide("betPhase");
		}
		// Player 1 just bet, show to player 2
		else if (player_turn === playerID && player1_bet != "None" && player1_bet != "null" && (player2_bet === "None" || player2_bet === "null") && player_phrase === "player2")
		{
			let betTxt = "";
			if (parseInt(player1_bet) === 0)
			{
				betTxt = "Checks (bets 0 credits)";
			}
			else
			{
				betTxt = "bets " + player1_bet + " credits"
			}
			document.getElementById("p1BetAction").innerHTML = betTxt;
			hide("p1Bet");
			hide("followBetDiv");
		}
	}
	else
	{
		hide("betDiv");
	}

	// When client recieves a message through the bet_socket
	bet_socket.on('bet', function(data) {

		for (pair in data)
		{
			if (data[pair] === null)
			{
				game.setAttribute(pair.toString(), data[pair]);
			}
			else
			{
				game.setAttribute(pair.toString(), data[pair].toString());
			}
		}

		game = document.getElementById("game");
		game_id = parseInt(game.getAttribute("game_id"));
		phase = game.getAttribute("phase");
		player1_bet = game.getAttribute("player1_bet");
		player2_bet = game.getAttribute("player2_bet");
		player_turn = parseInt(game.getAttribute("player_turn"));

		if (phase != "betting")
		{
			location.reload();
		}

		fold_count++;
		if (fold_count === 2)
		{
			location.reload();
		}

		if (data["game_id"] === game_id)
		{
			if (data["player1_bet"] != null && data["player2_bet"] === null)
			{
				if (playerID === data["player2_id"])
				{
					document.getElementById("opponent_credits").innerHTML = data["player1_credits"];
					document.getElementById("hand_pot").innerHTML = data["hand_pot"];
					let betTxt = "";
					if (parseInt(player1_bet) === 0)
					{
						betTxt = "Checks (bets 0 credits)";
					}
					else
					{
						betTxt = "bets " + player1_bet + " credits";
					}

					document.getElementById("p1BetAction").innerHTML = betTxt;
					document.getElementById("followBetAction").innerHTML = '<option value="" disabled selected>Action</option> <option value="call">Call</option> <option value="raise">Raise</option> <option value="fold">Fold</option>';

					show("betPhase");
					show("p2FollowBet");
					show("followBetActionDiv");
					hide("p1Bet");
					hide("followBetDiv");
				}
				else if (playerID === data["player1_id"])
				{
					document.getElementById("credits").innerHTML = data["player1_credits"];
					document.getElementById("hand_pot").innerHTML = data["hand_pot"];
				}
			}
			else if (data["player1_bet"] === null && data["player2_bet"] === null)
			{
				if (playerID === data["player2_id"])
				{
					document.getElementById("opponent_credits").innerHTML = data["player1_credits"];
					document.getElementById("hand_pot").innerHTML = data["hand_pot"];
					document.getElementById("credits").innerHTML = data["player2_credits"];
					document.getElementById("hand").innerHTML = data["player2_hand"];
					document.getElementById("opponent_cards").innerHTML = "2";

					hide("betPhase");
				}
				else if (playerID === data["player1_id"])
				{
					document.getElementById("opponent_credits").innerHTML = data["player2_credits"];
					document.getElementById("hand_pot").innerHTML = data["hand_pot"];
					document.getElementById("credits").innerHTML = data["player1_credits"];
					document.getElementById("hand").innerHTML = data["player1_hand"];
					document.getElementById("opponent_cards").innerHTML = "2";

					document.getElementById("followFolded").innerHTML = opponent_username + " folded. ";
					document.getElementById("betAction").innerHTML = '<option value="" disabled selected>Action</option> <option value="bet">Bet</option> <option value="check">Check (Do nothing)</option>'
					document.getElementById("betCredits").value = "";

					show("betPhase");
					show("p1Bet");
					show("betActionDiv");
					hide("p2FollowBet");
					hide("betDiv");
				}
			}
			else if (data["player1_bet"] != null && data["player2_bet"] != null)
			{
				if (playerID === data["player1_id"])
				{
					alert("they raised");
					document.getElementById("raiseCredits").innerHTML = data["player2_bet"] + " credits";
					hide("betActionDiv");
					show("p1Bet");
					show("followFollowRaiseActionDiv");
					document.getElementById("opponent_credits").innerHTML = data["player2_credits"];
					document.getElementById("hand_pot").innerHTML = data["hand_pot"];
				}
				else if(playerID === data["player2_id"])
				{
					document.getElementById("credits").innerHTML = data["player2_credits"];
					document.getElementById("hand_pot").innerHTML = data["hand_pot"];
				}
			}
		}
	});

	// Decide what to do for the betting phase
	$('#betActionBtn').on('click', function() {

		if (document.getElementById("betAction").value === "bet") {
			hide("betActionDiv");
			show("betDiv");
		}
		else if (document.getElementById("betAction").value === "check")
		{
			hide("betActionDiv");
			data = {"game_id": game_id, "action": "bet", "amount": 0};
			bet_socket.emit("bet", data);
		}
		else
		{
			document.getElementById("invalidBetAction").innerHTML = "Invalid bet action - Please input a valid value (check or bet)";
		}

	});

	// Decide how much to bet
	$('#betBtn').on('click', function() {
		let credits = document.getElementById("betCredits").value;
		if (credits === "")
		{
			document.getElementById("invalidBetCredits").innerHTML = "Please input a number of credits you would like to bet(a positive integer 1 to " + userCredits + ")";
		}
		else if (isNaN(parseInt(credits)))
		{
			document.getElementById("invalidBetCredits").innerHTML = "Invalid amount of credits - Please input a valid number of credits (a positive integer 1 to " + userCredits + ")";
		}
		else if (credits < 1 || credits > parseInt(userCredits))
		{
			document.getElementById("invalidBetCredits").innerHTML = "Invalid amount of credits - Please input a valid number of credits (a positive integer 1 to " + userCredits + ")";
		}
		else
		{
			hide("betDiv");
			data = {"game_id": game_id, "action": "bet", "amount": parseInt(credits)};
			bet_socket.emit("bet", data);
		}
	});



	// P2 decide how to follow up
	$('#followBetActionBtn').on('click', function() {

		if (document.getElementById("followBetAction").value === "call")
		{
			if (parseInt(player1_bet) > parseInt(userCredits))
			{
				document.getElementById("invalidFollowBetAction").innerHTML = "You can't call, you don't have enough credits!";
				return;
			}
			data = {"game_id": game_id, "action": "call", "amount": parseInt(player1_bet)};
			bet_socket.emit("bet", data);
		}
		else if (document.getElementById("followBetAction").value === "fold")
		{
			data = {"game_id": game_id, "action": "fold", "amount": 0};
			bet_socket.emit("bet", data);
		}
		else if (document.getElementById("followBetAction").value === "raise")
		{
			if (parseInt(player1_bet) > parseInt(userCredits) + 1)
			{
				document.getElementById("invalidFollowBetAction").innerHTML = "You can't raise, you don't have enough credits!";
				return;
			}
			document.getElementById("followRaise").min = player1_bet + 1;
			document.getElementById("followRaise").max = game.getAttribute("player2_credits");
			show("followBetDiv");
		}
		else
		{
			document.getElementById("invalidFollowBetAction").innerHTML = "Invalid bet action - Please input a valid value (raise, call, or fold)";
		}

		$("#followBetActionDiv").hide();
		return;

	});

	$("#followRaiseBtn").on("click", function() {
		let raise = document.getElementById("followRaise").value;
		if (raise === "")
		{
			document.getElementById("invalidRaise").innerHTML = "Please input a number of credits you would like to bet(a positive integer from " + (parseInt(player1_bet) + 1) + " to " + userCredits + ")";
		}
		else if (isNaN(parseInt(raise)))
		{
			document.getElementById("invalidRaise").innerHTML = "Invalid amount of credits - Please input a valid number of credits (a positive integer from " + (parseInt(player1_bet) + 1) + " to " + userCredits + ")";
		}
		else if (raise < player1_bet || raise > parseInt(userCredits))
		{
			document.getElementById("invalidRaise").innerHTML = "Invalid amount of credits - Please input a valid number of credits (a positive integer from " + (parseInt(player1_bet) + 1) + " to " + userCredits + ")";
		}
		else
		{
			hide("followBetDiv");
			data = {"game_id": game_id, "action": "raise", "amount": parseInt(raise)};
			bet_socket.emit("bet", data);
		}
	});

	$("#followFollowRaiseActionBtn").on("click", function() {

		if (document.getElementById("followFollowRaiseAction").value === "call")
		{
			if (parseInt(player2_bet) > parseInt(userCredits))
			{
				document.getElementById("invalidFollowFollowAction").innerHTML = "You can't call, you don't have enough credits!";
				return;
			}
			data = {"game_id": game_id, "action": "call", "amount": parseInt(player2_bet)};
			bet_socket.emit("bet", data);
		}
		else if (document.getElementById("followFollowRaiseAction").value === "fold")
		{
			data = {"game_id": game_id, "action": "fold", "amount": 0};
			bet_socket.emit("bet", data);
		}
		else
		{
			document.getElementById("invalidFollowFollowAction").innerHTML = "Invalid bet action - Please input a valid value (raise, call, or fold)";
		}

		hide("followFollowRaiseActionDiv");
		return;
	});

});