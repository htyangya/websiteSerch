
var cms_dialog_common = function() {

///////////////////////////////////////////////////////////////////////
function ajax_post(url, data, success_func, err_func_name)
{
	$.ajax({
		type: 'post',
		url: url,
		data: data,
		dataType: 'json',
		success: success_func,
		error: function(xmlhttprequest, textstatus, errorThrown) {
			alert_dlg("Error", "Error at " + err_func_name + "<br>\n" +
				xmlhttprequest.responseText + "<br>\n" +
				"HttpStatus: " + xmlhttprequest.status + "<br>\n" +
				"TextStatus: " + textstatus + "<br>\n" +
				"Error: " + errorThrown.message);
		},
		cache: false,
		async: false
	});
}

///////////////////////////////////////////////////////////////////////

function reset_jqm(jqm_nm) {
	$('#' + jqm_nm).html("Please wait...");
}

function copy_document_url(popup_msg) {
	alert_dlg('Message', popup_msg);
}

// public method
return {
	ajax_post: ajax_post,
	reset_jqm: reset_jqm,
	copy_document_url: copy_document_url
};

};
