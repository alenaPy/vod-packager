$(document).ready(function() {
	// Initializing accordion
	$('.accordion').accordion({defaultOpen: ''});
	// Adding events
	//element.onclick = doSomething
	// package_group select
	$('#package_group').change(function() {
		//alert('Value change to ' + $(this).attr('value'));
		var opt = $("#package_group").val();
		if (opt == "new") {
			$('#new_package_group').click();
		}
	});
	$(".various").fancybox({
		maxWidth	: 800,
		maxHeight	: 600,
		fitToView	: false,
		width		: '40%',
		height		: '50%',
		autoSize	: false,
		closeClick	: false,
		openEffect	: 'none',
		closeEffect	: 'none'
	});
	
});

function actionUploadImageRenditions(e) {
	window.location = "/vod/image_renditions/upload/" + $("#item_id").val();
}

function actionExportItem() {
	if (validateItem()) {
		var jsonObj = {'item_id':$('#item_id').val(),'selected_customers':$('#customers_for_export').val(),'package_group':$('#package_group').val()};
		
		/*
		var foo = []; 
		$('#customers_for_export :selected').each(function(i, selected){ 
			foo[i] = $(selected).text(); 
		});
		alert(foo);
		*/
		
		//alert(JSON.stringify(jsonObj));
		Dajaxice.Packager_app.export_item(clbkExportItem, jsonObj);
	}
}

function clbkExportItem(data) {
	alert(data.message);
}

function clbkNewPackageGroup(data) {
	json_data = json_parse(data);
	// Closing fancybox window
	parent.$.fancybox.close();
	// Add new option to package group select
	$("#package_group").append("<option value='"+json_data.id+"'>"+json_data.name+"</option>");
	// Select created option
	$('select').val(json_data.id);
	// Go to top
	$('html, body').animate({ scrollTop: 0 }, 0);
}

function validateItem() {
	if ($("#customers_for_export").val() != null) {
		pkg_grp = $("#package_group").val();
		if ((pkg_grp != "null") && (pkg_grp != "new")) {
			return true;
		} else {
			alert("Por favor indique el grupo para el cual desea exportar el item.");
			return false;
		}
	} else {
		alert("Debe seleccionar al menos un cliente.");
		return false;
	}
}

/* DAJAXICE: Funciones de ejemplo, por favor no borrar! */

function dajaxice_example() {
	Dajaxice.Packager_app.dajaxice_example(my_callback_example_1);
}

function dajaxice_args_example() {
	var jsonObj = {'text':$('#text').val()};
	Dajaxice.Packager_app.args_example(my_callback_example_2, jsonObj);
}

function my_callback_example_1(data) {
	alert(data.message);
}

function my_callback_example_2(data) {
	alert(data.message);
}