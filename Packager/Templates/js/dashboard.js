$(document).ready(function() {
	// Seteo el valor del combo package_group
	$("#package_group").val($("#package_group_id").val());
	// Despliego los iconos correspondientes a los estados de cada paquete
	var json_object = JSON.parse(json_string);
	var json_items_object = JSON.parse(json_items_string);
	$.each(json_object.items, function(indexa, value) {
		if (json_object.items[indexa].item != 0) {
			var item_id = json_object.items[indexa].item;
			var tr_tag_id = "item_" + item_id.toString();
			var trItem = $("#"+tr_tag_id);
			var tds = trItem.children("td");
			$.each(tds, function(indexb, value) {
				if (tds[indexb].id != "") {
					var td_tag_id = tds[indexb].id;
					var customer_id = parseInt(rightstr(td_tag_id, "_"));
					var pkg_obj = findPackageStatusAndError(json_object, indexa, customer_id);
					//var pkg_status = findPackageStatus(json_object, indexa, customer_id);
					if (pkg_obj.status != "ZZZ") {
						var td = $("#"+tr_tag_id).children("#"+td_tag_id);
						var span = td.children("span");
						span.attr("class", "pkgstatus_"+pkg_obj.status);
						span.attr("title", pkg_obj.error);
					}
				}
			});
		}
	});	
	// Enabling tooltips
	$('#iconography *').tooltip();
	$('#dashboardicons *').tooltip();
	// Inserto separadores por marca
	insertBrandSeparators(json_items_object)
	// Highlight table rows on hover
	$(".trItemTitle").hover(
		function () {
			$(this).css("background","#ff9");
			$(this).css("color","#333");
			$(this).css("font-weight","bold");
		},
		function () {
			$(this).css("background","");
			$(this).css("color","#fff");
			$(this).css("font-weight","normal");
		}
	);
});

function selectBrandForExport(brand) {
    alert(brand);
}

function insertBrandSeparators(json_items_object) {
    var brand = "upperRow";
    var total_customers = $("#total_customers").val();
    $('#tblDashboard > tbody  > tr').each(function() {
        // Corte de control sobre la marca
        if (brand != $(this).attr("brand")) {
            brand = $(this).attr("brand");
            $(this).before("<tr><td colspan=\"" + total_customers  + "\"><a href=\"#\" class=\"trBrandSeparator\">" + brand + "</a></td></tr>");
        }
    }); 
}

function findPackageStatus(json_object, item_id, customer_id) {
	var output = "ZZZ";
	$.each(json_object.items[item_id].pkgs, function(indexc, value) {
		if (json_object.items[item_id].pkgs[indexc].customer_id == customer_id) {
			output = json_object.items[item_id].pkgs[indexc].pkg_status;
		}
	});
	return output;
}

function findPackageStatusAndError(json_object, item_id, customer_id) {
	var output = new Object();
	output.status = "ZZZ";
	output.error = "";
	$.each(json_object.items[item_id].pkgs, function(indexc, value) {
		if (json_object.items[item_id].pkgs[indexc].customer_id == customer_id) {
			output.status = json_object.items[item_id].pkgs[indexc].pkg_status;
			output.error = json_object.items[item_id].pkgs[indexc].pkg_error;
		}
	});
	return output;
}

function rightstr(s, c) {
	L = s.lastIndexOf(c);
	L = L + 1;
	return s.slice(L);
}

function onChangePackageGroup() {
	window.location = "/vod/package_group/" + $("#package_group").val();
}
