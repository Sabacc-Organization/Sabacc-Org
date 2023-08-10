$(document).ready(function() {

	let dom = "http://127.0.0.1:5000/";

	var socket = io.connect(dom);
	var game_socket = io(dom + '/game');
	var protect_socket = io(dom + '/protect');

	game_socket.on('connect', function() {
		game_socket.emit("game");
	});

	console.log("ye");


});