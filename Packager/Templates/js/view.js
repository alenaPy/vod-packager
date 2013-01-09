$(document).ready(function() {
	$("#search").keypress(function(e) {
		if(e.which == 13) {
			// enter pressed
			window.location = "/vod/search?q=" + $("#search").val();
		}
	});
});

function getSelectedEntries() {
	var selectedEntries = $("input:checkbox[name=entrycheck]:checked");
	
	return selectedEntries;
}

function actionViewEntry(relURL) {
	var selectedEntries = getSelectedEntries();
	
	if (selectedEntries.size() == 1) {
		window.location = relURL + "/" + selectedEntries[0].value;
	} else {
		if (selectedEntries.size() == 0) {
			alert("Por favor, seleccione al menos una entrada.");
		} else {
			alert("Solo puede visualizar una entrada.");
		}
	}
}

function actionRefreshView() {
	window.location.reload();
}

function actionSearch() {
	alert("Search");
}
