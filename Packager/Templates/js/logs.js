$(document).ready(function() {
	var url = "/logs/" + $("#logfile").val() + "?" + randomString();
	$("#ifLog").attr('src', url);
});

function changeIframeSrc() {
	var url = "/logs/" + $("#logfile").val() + "?" + randomString();
	$("#ifLog").attr('src', url);
}
	
function actionRefreshIFrame() {
	//$("#ifLog").attr('src', $("#ifLog").attr('src'));
	var url = $("#ifLog").attr('src') + "?" + randomString();
	$("#ifLog").attr('src', url);
}

function randomString() {
	var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
	var string_length = 8;
	var randomstring = '';
	for (var i=0; i<string_length; i++) {
		var rnum = Math.floor(Math.random() * chars.length);
		randomstring += chars.substring(rnum,rnum+1);
	}
	return randomstring;
}