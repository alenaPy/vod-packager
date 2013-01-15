$(document).ready(function() {
	
	$("#package_group").val($("#package_group_id").val());
	
	var json_object = JSON.parse(json_string);
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
					var pkg_status = findPackageStatus(json_object, indexa, customer_id);
					if (pkg_status != "ZZZ") {
						var td = $("#"+tr_tag_id).children("#"+td_tag_id);
						var span = td.children("span");
						span.attr("class", "pkgstatus_"+pkg_status);
					}
				}
			});
		}
	});

});

function findPackageStatus(json_object, item_id, customer_id) {
	var output = "ZZZ";
	$.each(json_object.items[item_id].pkgs, function(indexc, value) {
		if (json_object.items[item_id].pkgs[indexc].customer_id == customer_id) {
			output = json_object.items[item_id].pkgs[indexc].pkg_status;
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