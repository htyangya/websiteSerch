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

function submit() {

	var file_input = $("#" + args['elm_ids']['input_id']);
	var file_form = $("#" + args['elm_ids']['ul_form_id']);
    if (args['elm_ids']['check_func'] && !args['elm_ids']['check_func']()) {
        return
    }
	if (file_input.val()) {
		file_form.submit();
		return
	}

	// FormDataオブジェクトを用意
	var fd = function () {
	    file_input.prop("disabled", true);
	    var fd = new FormData(file_form[0]);
	    file_input.prop("disabled", false);
        fd.append("file_select_method", file_select_method);
        fd.append("ajax_flag", 1);
        if(typeof files !== "undefined" && files.length !== 0) {
            // ファイル情報を追加
            fd.append(file_input.attr("name"), files[0]);
        }
        return fd;
    }();

	// XHR で送信
	$.ajax({
		url: file_form.attr("action"),
		type: 'POST',
		data: fd,
		dataType: 'json',
		processData: false,
		contentType: false,
		success: function(result) {
				 file_input.attr("type","hidden").val(result.excel_name)
				 file_form.submit()
			},
		error: function(xmlhttprequest, textstatus, errorThrown) {
			hide_loading_msg();
			alert_dlg("Error", "File upload failed");
			}
  	});
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
	submit: submit
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