/**
 TlibDragAndDropUpload.js Drag and drop support library.

 Version: 1.10 (2017/04/19)
  - Add check max file size.
  - Support javascript function in reload_edit_file_list().
  - Check result.result is 'Error' in post_check_overwrite_by_drop().
*/

var tlib_drag_and_drop = function(args) {

var files;
var file_select_method;
function show_loading_msg(msg) {
    $("." + args['elm_ids']['div_class']).hide();
    $("#tlibFileUploadLoadingMessage").show();
    $("#tlibFileUploadLoadingMessageBody").html(msg).show();
}

function hide_loading_msg() {
    $("#tlibFileUploadLoadingMessageBody").hide();
    $("#tlibFileUploadLoadingMessage").hide();
    $("." + args['elm_ids']['div_class']).show();
}

$(document).keydown(function(e){
    if(e.keyCode === 27){
        hide_loading_msg();
    }
});

function show_error_message(msg) {
    alert_dlg('Error', msg);
}

function check_template_form() {
    // FormDataオブジェクトを用意
    var fd = create_form_data();

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
        if (typeof(args['tlib_types']['request_type']) !== "undefined" && args['tlib_types']['request_type'] === "GET") {
            var url = args['param']['redirect_url'] + result.template_id;
            if(result.opt_param) {
                url += result.opt_param;
            }
            window.location.href = url;
        } else {
            // FormDataオブジェクトを用意
            var file_upload_form = document.forms.namedItem(args['elm_ids']['ul_form_id']);
            if(typeof file_upload_form.elements["template_id"] !== "undefined") {
                file_upload_form.elements["template_id"].value = result.template_id;
            }
            file_upload_form.submit();
        }
    }
}

function reload_edit_file_list(result, fileTypeId) {
    var func = args['func']['get_file_list'];
    if($.isFunction(func)) {
        func.call(this, result, fileTypeId);
        hide_loading_msg();
        return false;
    }

    var fd = create_form_data(func, fileTypeId);

    // XHR で送信
    $.ajax({
        url: args['url'],
        type: 'POST',
        data: fd,
        dataType: 'text',
        processData: false,
        contentType: false,
        success: function(result) {
                $("#" + args['elm_ids']['file_list_id']).html(result);
            },
        error: function(xmlhttprequest, textstatus, errorThrown) {
            alert_dlg("Error", "Error at reload_edit_file_list<br>\n" +
                xmlhttprequest.responseText + "<br>\n" +
                "HttpStatus: " + xmlhttprequest.status + "<br>\n" +
                "TextStatus: " + textstatus + "<br>\n" +
                "Error: " + errorThrown.message);
            }
    });
}

function post_file_upload(result, fileTypeId) {
    hide_loading_msg();
    reload_edit_file_list(result, fileTypeId);
}

function post_file_upload_by_drop(xhr, fileTypeId) {
    if(xhr.status !== 200) {
        hide_loading_msg();
        show_error_message(xhr.responseText);
        return;
    }

    var result = JSON.parse(xhr.response);
    if(result.status === 'Error') {
        hide_loading_msg();
        show_error_message(result.msg);
        return;
    }
    if(result.status === 'Redirect') {
        location.href = result.url;
        return;
    }

    post_file_upload(result, fileTypeId);
}

function get_total_file_size() {
    var i;
    var size = 0;
    for(i = 0; i < files.length; i++) {
        size = size + files[i].size;
    }
    return size;
}

function do_file_upload_by_drop(fileTypeId) {
    var err_func_name = 'do_file_upload_by_drop';
    var progress = document.getElementById('tlibFileUploadProgressBar');

    var fd = create_form_data(args['func']['file_upload'], fileTypeId);

    var xhr = new XMLHttpRequest();
    var total_size = get_total_file_size();

    xhr.open('POST', args['url'], true);

    xhr.onload = function() {
        progress.value = progress.innerHTML = 100;

        if(xhr.readyState === 4) {
            var tm = 200;
            if(total_size > (1024*1024*10)) {
                tm = 600;
            }
            setTimeout(
                function() { post_file_upload_by_drop(xhr, fileTypeId); },
                tm);
        }
    };

    xhr.upload.onprogress = function (event) {
        if (event.lengthComputable) {
            var complete = (event.loaded / event.total * 100 | 0);

            // ファイルサイズが大きい(10MB超)の場合、Progress Barを
            // 90%で停止して、ファイルの登録完了を待つ
            // ファイルサイズが10MB以下の場合は95%にする
            if(complete === 100) {
                if(event.total > (1024*1024*10)) {
                    progress.value = progress.innerHTML = 90;
                    $('#uploading_msg').text("Wait a moment");
                } else {
                    progress.value = progress.innerHTML = 95;
                }
            } else {
                if(event.total > (1024*1024*10) && complete > 90) {
                    complete = 90;
                } else if(complete > 95) {
                    complete = 95;
                }
                progress.value = progress.innerHTML = complete;
            }
        }
    }

    xhr.send(fd);
}

function post_check_overwrite_by_drop(result, fileTypeId) {
    if(result.status === 'Error') {
        hide_loading_msg();
        show_error_message(result.msg);
        return;
    }

    if(result.check_overwrite_flg) {
        confirm_2cb_noclose(result.msg,
            function() { do_file_upload_by_drop(fileTypeId); },
            function() { hide_loading_msg(); });
    } else {
        do_file_upload_by_drop(fileTypeId);
    }
}

function create_form_data(func, fileTypeId) {
    // テンプレート一括登録の場合
    if (typeof(args['tlib_types']['operate_type']) !== "undefined" && args['tlib_types']['operate_type'] === "TEMPLATE_FILE") {
        // FormDataオブジェクトを用意
        var file_upload_form = document.forms.namedItem(args['elm_ids']['ul_form_id']);
        var fd = new FormData(file_upload_form);
        fd.append("file_select_method", file_select_method);

        if(typeof files !== "undefined" && files.length !== 0) {
            // ファイル情報を追加
            fd.append(args['elm_ids']['ul_filename'], files[0]);
        }

        return fd;

    // ファイル一括アップロードの場合
    } else {
        // FormDataオブジェクトを用意
        var fd = new FormData();
        fd.append("func", func);
        fd.append("file_type_id", fileTypeId);
        fd.append("file_select_method", file_select_method);

        // ループでargsのparamを全部セットする
        for (var keyString in args['param']) {
            fd.append(keyString, args['param'][keyString]);
        }

        // ファイルの個数を取得
        var filesLength = files.length;

        // ファイル情報を追加
        for (var i = 0; i < filesLength; i++) {
            if(func === args['func']['file_upload']) {
                fd.append("file_path[]", files[i]);
            } else {
                fd.append("file_name[]", files[i].name);
                fd.append("file_size[]", files[i].size);
            }
        }
        return fd;
    }
}

function file_name_compare(file_name, file_list_for_check)
{
    var i;
    for(i = 0; i < file_list_for_check.length; i++) {
        if(file_name.toLowerCase() === file_list_for_check[i].toLowerCase()) {
            return file_name;
        }
    }
    return "";
}

function init_drop_file_target() {
    var drop_zone = $("." + args['elm_ids']['div_class']);

    if(!drop_zone[0]) {
        alert_dlg('Warn', 'The page has not file drop area.');
        return;
    }

    // テンプレート一括登録用
    var dropUploadFiles = function() {
        if(files.length === 0) return;

        if(files.length > 1) {
            hide_loading_msg();
            show_error_message('Please select just one file.');
            return false;
        }

        $("#" + args['elm_ids']['ul_file_id']).html(files[0].name);
        $("#" + args['elm_ids']['input_class'])[0].files = files;
    };

    // ファイルアップロードの重複チェック用
    var checkOverwrite = function(fileTypeId) {
        // FormDataオブジェクトを用意
        var fd = create_form_data(args['func']['check_overwrite'], fileTypeId);

        var err_func_name = 'uploadFiles';
        // XHR で送信
        $.ajax({
            url: args['url'],
            type: 'POST',
            data: fd,
            dataType: 'json',
            processData: false,
            contentType: false,
            success: function(result) {
                    post_check_overwrite_by_drop(result, fileTypeId);
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

    var checkOverwriteLocal = function(fileTypeId, file_list_for_check) {
        var i;
        var same_file_list = new Array;
        var same_file;

        if(file_list_for_check.length > 0) {
            for(i = 0; i < files.length; i++) {
                same_file = file_name_compare(files[i].name,
                    file_list_for_check);
                if(same_file !== "") same_file_list.push(same_file);
            }
        }

        if(same_file_list.length != 0) {
            var same_file_list_str = same_file_list.join("<br>");
            var overwrite_message = args['msg']['overwrite_file_msg'];
            confirm_2cb_noclose(same_file_list_str + '<br><br>' + overwrite_message,
                function() { do_file_upload_by_drop(fileTypeId); },
                function() { hide_loading_msg(); });
        } else {
            do_file_upload_by_drop(fileTypeId);
        }
    }

    var uploadFiles = function(fileTypeId) {
        if(args['func']['check_overwrite'] !== undefined) {
            checkOverwrite(fileTypeId);
            return;
        }
        if(args['file_list_for_check_overwrite'] !== undefined) {
            setTimeout(function() {
                checkOverwriteLocal(fileTypeId, args['file_list_for_check_overwrite']);
                },
                10);
            return;
        }

        do_file_upload_by_drop(fileTypeId);
        return;

        alert('Fatal Error');
    };

    var confirmUploadFiles = function(fileTypeId, chk_flg) {
        if(files.length === 0) return;

        var max_files = args['max_files'];
        if(typeof(max_files) !== 'number') {
            max_files = 5;
        }
        if(files.length > max_files) {
            hide_loading_msg();
            var max_file_msg = args['msg']['max_file_msg'];
            max_file_msg = max_file_msg.replace(/%s/, max_files);
            show_error_message(max_file_msg);
            return false;
        }

        var max_file_size = args['max_file_size'];
        var min_file_size = args['min_file_size'];
        if(typeof(max_files) === 'number') {
            for(i = 0; i < files.length; i++) {
                if(files[i].size >= max_file_size) {
                    var max_file_size_mb = max_file_size / (1024 * 1024);
                    hide_loading_msg();
                    var max_file_msg = args['msg']['max_file_size_msg'];
                    max_file_msg = max_file_msg.replace(/%s/, max_file_size_mb);
                    show_error_message(max_file_msg);
                    return false;
                }
                // 添付ファイル実行時にファイルサイズ　0byte　であればエラーメッセージ表示して，アップロードしない。
                if(files[i].size === min_file_size) {
                    hide_loading_msg();
                    var min_file_msg = args['msg']['mix_file_size_msg'];
                    show_error_message(min_file_msg);
                    return false;
                }
            }
        }

        show_loading_msg(
            '<h1 id="uploading_msg">Uploading...</h1><br>' +
            '<p><progress id="tlibFileUploadProgressBar" min="0" max="100" value="0">0' +
            '</progress></p>');

        // ファイル名を取得
        var fileNameList = '';
        for (var i = 0; i < files.length; i++) {
            if(i > 0) fileNameList += '<br>';
            fileNameList += files[i].name;
        }

        if(chk_flg) {
            confirm_2cb_noclose(fileNameList + '<br><br>' +
                    args['msg']['upload_confirm_msg'],
                function() { uploadFiles(fileTypeId); },
                function() { hide_loading_msg(); });
        } else {
            uploadFiles(fileTypeId);
        }
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
        file_select_method = 'drop';
        files = evt.originalEvent.dataTransfer.files;

        // テンプレート一括登録の場合
        if (typeof(args['tlib_types']['operate_type']) !== "undefined" && args['tlib_types']['operate_type'] === "TEMPLATE_FILE") {
            dropUploadFiles();

        // ファイル一括アップロードの場合
        } else {
            var fileTypeId = $(evt.currentTarget).find('input.fileType').val();
            confirmUploadFiles(fileTypeId, true);
        }
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
    $("." + args['elm_ids']['button_class']).click(function() {

        var inputClass = $(this).parent().find("input." + args['elm_ids']['input_class']);

        // 連続で同一ファイルがアップロードできるため
        inputClass.val('');

        // ダミーボタンとinput[type="file"]を連動
        inputClass.click();
    });

    $("." + args['elm_ids']['input_class']).change(function(){

        // ファイル情報を取得
        files = this.files;
        if(files.length === 0) return;
        file_select_method = 'dialog';

        // テンプレート一括登録の場合
        if (typeof(args['tlib_types']['operate_type']) !== "undefined" && args['tlib_types']['operate_type'] === "TEMPLATE_FILE") {
            dropUploadFiles();

        // ファイル一括アップロードの場合
        } else {
            fileTypeId = $(this).parent().find("input.fileType").val();
            confirmUploadFiles(fileTypeId, false);
        }
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

