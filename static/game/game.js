$(document).ready(function() {

	var socket = io.connect('https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/');
	var game_socket = io('https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/game');

	game_socket.on('connect', function() {
		game_socket.emit("game");
	});

});