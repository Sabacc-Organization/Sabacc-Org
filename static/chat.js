$(document).ready(function() {

	let dom = "http://127.0.0.1:5000";

	var socket = io.connect(dom);
	var chat_socket = io(dom + '/chat');

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