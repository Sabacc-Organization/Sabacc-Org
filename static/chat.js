$(document).ready(function() {

	var socket = io.connect('https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws');
	var chat_socket = io('https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/chat');

	let user = document.getElementById("user");

	chat_socket.on('connect', function() {
		chat_socket.emit("message", user.getAttribute("name") + ' has connected!');
	});

	chat_socket.on('message', function(msg) {
		$("#messages").append('<p>'+msg+'</p>');
	});

	$('#sendbutton').on('click', function() {
		let msg = user.getAttribute("name") + ": " + document.getElementById("myMessage").value;
		chat_socket.emit("message", msg);
		$('#myMessage').val('');
	});

});