var tlib_drag_and_drop = function(args) {

var files;
var file_select_method;
function show_loading_msg(msg) {
	$("#" + args['elm_ids']['div_id']).hide();
	$("#tlibFileUploadLoadingMessage").show();
	$("#tlibFileUploadLoadingMessageBody").html(msg).show();
}

function hide_loading_msg() {
	$("#tlibFileUploadLoadingMessageBody").hide();
	$("#tlibFileUploadLoadingMessage").hide();
	$("#" + args['elm_ids']['div_id']).show();
}

$(document).keydown(function(e){
	if(e.keyCode == 27){
		hide_loading_msg();
	}
});

function show_error_message(msg) {
	alert_dlg('Error', msg);
}

function check_template_form() {

	// FormDataオブジェクトを用意
	var fd = create_form_data(args['func']['check_template_form']);

	var err_func_name = 'check_template_form';
	// XHR で送信
	$.ajax({
		url: args['url'],
		type: 'POST',
		data: fd,
		dataType: 'json',
		processData: false,
		contentType: false,
		success: function(result) {
				post_check_template_form(result);
			},
		error: function(xmlhttprequest, textstatus, errorThrown) {
			hide_loading_msg();
			alert_dlg("Error", "Error at " + err_func_name + "<br>\n" +
				xmlhttprequest.responseText + "<br>\n" +
				"HttpStatus: " + xmlhttprequest.status + "<br>\n" +
				"TextStatus: " + textstatus + "<br>\n" +
				"Error: " + errorThrown.message);
			}
  	});
}

function post_check_template_form(result) {
	if(result.check_error_flg) {
		alert_dlg('Error', result.msg);
		return;
	} else {
		var url = args['param']['redirect_url'] + result.template_id;
		if(result.opt_param) {
			url += result.opt_param;
		}
		window.location.href = url;
	}
}

function create_form_data(func) {

	// FormDataオブジェクトを用意
	var file_upload_form = document.forms.namedItem(args['elm_ids']['ul_form_id']);
	if(typeof file_upload_form.elements["func"] !== "undefined") {
		file_upload_form.elements["func"].value = func;
	}
	var fd = new FormData(file_upload_form);
	fd.append("func", func);
	fd.append("file_select_method", file_select_method);

	if(typeof files !== "undefined" && files.length !== 0) {
		// ファイル情報を追加
		fd.append(args['elm_ids']['ul_filename'], files[0]);
	}

	return fd;
}

function init_drop_file_target() {
	var drop_zone = $("#" + args['elm_ids']['div_id']);

	if(!drop_zone[0]) {
		alert_dlg('Warn', 'The page has not file drop area.');
		return;
	}

	var dropUploadFiles = function() {
		if(files.length === 0) return;

		if(files.length > 1) {
			hide_loading_msg();
			show_error_message('Please select just one file.');
			return false;
		}

		$("#" + args['elm_ids']['ul_file_id']).html(files[0].name);
		$("#" + args['elm_ids']['input_id'])[0].files = files;
	};

	var onDropFile = function(evt) {
		// Check for the various File API support.
		if (!window.File || !window.FileList || !window.FileReader
			|| !window.Blob) {
			alert_dlg('Warn', 'The File APIs are not fully supported in this browser.');
			return;
		}
		evt.preventDefault();
		evt.stopPropagation();

		files = evt.originalEvent.dataTransfer.files;

		file_select_method = 'drop';
		dropUploadFiles();
	};

	drop_zone.bind('dragover', function(evt) {
		evt.preventDefault();
		evt.stopPropagation();
		evt.originalEvent.dataTransfer.dropEffect = "link";
		return false;
	})
	.bind('dragenter', function(evt) {
		evt.preventDefault();
		evt.stopPropagation();
		evt.originalEvent.dataTransfer.dropEffect = "link";
		return false;
	})
	.bind('drop', onDropFile);

	/*================================================
		ダミーボタンを押した時の処理
	=================================================*/
	$("#" + args['elm_ids']['button_id']).click(function() {
		// 連続で同一ファイルがアップロードできるため
		$("#" + args['elm_ids']['input_id']).val('');

		// ダミーボタンとinput[type="file"]を連動
		$("#" + args['elm_ids']['input_id']).click();
	});

	$("#" + args['elm_ids']['input_id']).change(function(){
		// ファイル情報を取得
		files = this.files;
		if(files.length === 0) return;

		file_select_method = 'dialog';
		dropUploadFiles();
	});
}

function on_ready() {
	init_drop_file_target();
}

////////////////////////////////////////////////////////////////////////

// public method
return {
	on_ready: on_ready,
	check_template_form: check_template_form
};

};

// 全体の初期化
function tlib_init_drag_and_drop_upload() {
	$.event.props.push('dataTransfer');
	document.addEventListener("drop", function( event ) {
			// prevent default action (open as link for some elements)
			event.preventDefault();
	}, false);

	// 画面全体のdragoverのイベント設定
	$(document.body).bind('dragover', function(evt) {
		return false;
	});
}