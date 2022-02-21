$(document).ready(function() {

	// Define sockets
	var socket = io.connect('https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/');
	var bet_socket = io('https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/bet');
	
	// Reduce website hackability by defining variables pulled from the HTML as soon as possible
	let game = document.getElementById("game");
	let game_id = parseInt(game.getAttribute("game_id"))
	let userCredits = document.getElementById("credits").innerHTML;
	let opponent_id = parseInt(document.getElementById("opponent").getAttribute("opponent_id"));
	
	// Hide HTML that must be hidden from the beginning
	$("#betDiv").hide()
	
	// When client recieves a message through the bet_socket
	bet_socket.on('bet', function(gameID, action, amount, player_id) {
		console.log("bet")
		if (gameID === game_id)
		{
			if (action === "bet")
			{
				if (player_id === opponent_id)
				{
					document.getElementById("credits").innerHTML = (parseInt(document.getElementById("credits").innerHTML) - amount).toString();
					document.getElementById("hand_pot").innerHTML = (parseInt(document.getElementById("hand_pot").innerHTML) + amount).toString();
				}
				else
				{
					document.getElementById("opponent_credits").innerHTML = (parseInt(document.getElementById("opponent_credits").innerHTML) - amount).toString();
					document.getElementById("hand_pot").innerHTML = (parseInt(document.getElementById("hand_pot").innerHTML) + amount).toString();
				}
			}
		}
	});

	// Decide what to do for the betting phase
	$('#betActionBtn').on('click', function() {

		if (document.getElementById("betAction").value === "bet") {
			$("#betActionDiv").hide();
			$("#betDiv").show();
		}
		else if (document.getElementById("betAction").value === "check")
		{
			$("#betActionDiv").hide();
			bet_socket.emit("bet", game_id, "check", 0);
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
			bet_socket.emit("bet", game_id, "bet", parseInt(credits));
		}
	});

});