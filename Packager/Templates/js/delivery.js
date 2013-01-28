$(document).ready(function() {
    // Despliego los iconos correspondientes a los estados de cada paquete
    var json_pkgs_object = JSON.parse(json_pkgs_string);
    var json_items_object = JSON.parse(json_items_string);
    $.each(json_pkgs_object.packages, function(indexa, value) {
	if (json_pkgs_object.packages[indexa].item != 0) {
	    var item_id 	= json_pkgs_object.packages[indexa].item;
	    var str_id 		= "it_" + json_pkgs_object.packages[indexa].item + "_cr_" + json_pkgs_object.packages[indexa].customer;
	    switch (json_pkgs_object.packages[indexa].status) {
		case "P":
		    $("#" + str_id).attr('checked', true);
		    $("#" + str_id).attr('disabled', true);
		    break;
		case "Q":
		    $("#" + str_id).attr('checked', true);
		    $("#" + str_id).attr('disabled', true);
		    break;
		case "E":
		    $("#" + str_id).attr('checked', true);
		    $("#" + str_id).attr('disabled', true);
		    break;
		default:
		    //alert("default");
		    break;
	    }
	}
    });
    // Insert brand separatos
    insertBrandSeparatorsAndDisableUnfinishedItems(json_items_object);
    // Enabling tooltips                                                                                                                                           
    $('#tblDelivery *').tooltip();
    // Highlight table rows on hover
    $(".trItemTitle").hover(
	function () {
	    $(this).css("background","#ff9");
	    $(this).find("a").css("color","#333");
	    $(this).css("font-weight","bold");
	}, 
	function () {
	    $(this).css("background","");
	    $(this).find("a").css("color","#fff");
	    $(this).css("font-weight","normal");
	}
    );
});

function actionResetForm() {
    $("input[type=checkbox]:not(:disabled)").attr({
	checked: false,
        //disabled: 'disabled'
    });
}

function selectCustomerAndBrandForExport(customer) {
    var selectedBrand = $('select[name="brandForSelection"]').val();
    switch(selectedBrand) {
	case "all":
	    $("#brandForSelection option").each(function() {
		brand = $(this).val();
		if (brand != "all") {
		    $("input[customer='" + customer + "'][brand='" + brand + "'][type=checkbox]:not(:checked):not(:disabled)").attr({
			checked: "checked"
		    });
		}
	    });
	    break;
	default:
	    $("input[customer='" + customer + "'][brand='" + selectedBrand + "'][type=checkbox]:not(:checked):not(:disabled)").attr({
		checked: "checked"
	    });
	    break;
    }
}

function selectBrandForExport(brand) {
    $("input[brand='" + brand + "'][type=checkbox]:not(:checked):not(:disabled)").attr({
	checked: "checked",
	//disabled: 'disabled'
    });
}

function selectItemFormExport(item_id) {
    $("input[item='" + item_id + "'][type=checkbox]:not(:checked):not(:disabled)").attr({ 
	checked: "checked",
    });
}

function getItemStatus(json_object, id) {
    return json_object[id];
}

function insertBrandSeparatorsAndDisableUnfinishedItems(json_items_object) {
    var brand = "upperRow";
    var total_customers = $("#total_customers").val();
    $('#tblDashboard > tbody  > tr').each(function() {
	// Corte de control sobre la marca
	if (brand != $(this).attr("brand")) {
	    // Salvo brand para corte de control
	    brand = $(this).attr("brand");
	    // Apendo fila separadora
	    $(this).before("<tr><td colspan=\"" + total_customers  + "\"><a href=\"javascript:selectBrandForExport('" + brand  + "')\" class=\"trBrandSeparator\">" + brand + "</a></td></tr>");
	    // Apendo nueva brand al combo de brands
	    $('#brandForSelection').append("<option value='" + brand + "'>" + brand  + "</option>");
	}
	// Habilito para exportar solo aquellos items que estan preparados
	var item_id = $(this).attr("id");
	if (item_id != undefined) {
	    item_id = rightstr(item_id, "_");
	    item_status = getItemStatus(json_items_object, item_id);
	    if (item_status != "D") {
		$(this).find('input', 'checkbox').attr('disabled', true);
	    }
	}
    });
}

function onChangeItemGroup() {
    var url = "/vod/delivery/" + $("#item_group").val();
    window.location = url;
}

function actionBulkExport() {
    data = $('#bulk_export').serialize();
    Dajaxice.Packager_app.bulk_export(message_callback, {'data':data});
}

function message_callback(data) {
    if (data.message == null) {
        window.parent.clbkNewPackageGroup(data);
    } else {
	alert(data.message);
    }
}

function rightstr(s, c) {
    L = s.lastIndexOf(c);
    L = L + 1;
    return s.slice(L);
}
