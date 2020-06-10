
var svcdb_main_frame = function(view_type) {

var last_list_hash = '';
var cur_tree_type = '';
var cur_contents_id = '';
var tree_search_text ='';
var cur_view_type = view_type;
var yf_id = '';
var isMSIE = /*@cc_on!@*/false;
var isFirefox = (navigator.userAgent.toLowerCase().indexOf("firefox")+1?1:0);

var no_incr_read_cnt_flg = false;
var refresh_list_flg = false;

var hsplitter;
var vsplitter;

var children_window = {};

var db_title = '';

var KEY_ENTER = 13;

/////////////////////////////////////////////////////////////////////
// utilities
function get_ie_version() {
	var ieVersion = document.documentMode;
	return ieVersion;
}

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

/////////////////////////////////////////////////////////////////////
function get_page_hash() {
	if(!location.hash) return '';
	var h = location.hash;
	if(h.substr(1, 3) === '%21') {
		// #!cが#%21cなどになることがある
		return "#!" + h.substr(4, 1);
	}
	return h.substr(0, 3);
}

function get_page_hash_opt(o) {
	if(!location.hash) return '';
	var h = location.hash;
	var re = new RegExp(o + "=([\\w\\-\\.!]+)");
	if(h.match(re)) {
		return RegExp.$1;
	}
	return "";
}

function set_page_hash(a) {
	if(location.hash === a) {
		on_hashchange();
		return;
	}
	location.hash = a;
}

function post_show_contents(x, s) {
	if(s === 'success') {
		$("#contentsView").html(x.responseText);
		$(window).trigger("resize");
		cur_contents_id = get_page_hash_opt('contents_id');

		var contents_title = $("#contentsTitle").text();
		document.title = contents_title + " : " + db_title;

		focus_contents();
	} else {
		$("#contentsView").html("Error");
	}
}

function show_contents() {
	var opt = get_page_hash_opt('opt');
	if(opt.length > 0) cur_contents_id = '';

	if(cur_contents_id === get_page_hash_opt('contents_id')) {
		var anc = get_page_hash_opt('anc');
		if(anc === 'attach_files') {
			scrollToAttachFiles();
			return;
		} else if(anc === 'comments') {
			scrollToComments();
			return;
		} else {
			$("#contentsScrArea").scrollTop(0);
			return;
		}
	}

	hide_contents();

	var contents_id = get_page_hash_opt('contents_id');

	$("#contentsViewArea").show();
	$("#contentsScrArea").scrollTop(0);
	focus_contents();

	$("#tr_" + contents_id).removeClass('unread');

	var url = "contents_show.cgi?contents_id=" + contents_id +
		"&show_contents_opt=" + opt;

	if(no_incr_read_cnt_flg) {
		url = url + "&no_incr_read_cnt_flg=1";
	}

	$.ajax({
		url: url,
		cache: false,
		complete: post_show_contents
	});
}

/////////////////////////////////////////////////////////////////////
function show_attach_files(contents_id) {
    var href = 'contents_file.cgi?func=show_attach_files' +
		'&contents_id=' + contents_id;
    load_jqmodal_dlg(href);
}

function close_attach_files() {
    close_jqmodal_dlg();
}

/////////////////////////////////////////////////////////////////////

function show_loading_msg(msg) {
	$("#loadingMessage").show();
	$("#loadingMessageBody").html(msg).show();
}

function hide_loading_msg() {
	$("#loadingMessageBody").hide();
	$("#loadingMessage").hide();
}

function show_null_loading() {
	$("#nullLoading").show();
}

function hide_null_loading() {
	$("#nullLoading").hide();
}

function hide_contents() {
	cur_contents_id = '';
	$("#contentsViewArea").hide();
	$("#contentsView").html("");
	hide_loading_msg();
	setTimeout(resize_object, 0);

	document.title = db_title;

	if(document.hasFocus() && $("#TlibTableContentsList").is(':visible')) {
		$("#TlibTableContentsList").focus();
	}
}

function scrollToRow(id) {
	var jid = "#" + id;

	var e = $(jid);
	if(!e || e.length === 0) return;

	var p = e.parent();
	if(!p || p.length === 0) return;
	for(;;) {
		if(p.get(0).tagName === 'DIV') break;
		p = p.parent();
		if(!p || p.length === 0) break;
	}
	if(p && p.length > 0) p.scrollTo(jid);
}

function scrollToAttachFiles() {
	$('#contentsScrArea').scrollTo('#contents_attach_files');
}

function scrollToComments() {
	$('#contentsScrArea').scrollTo('#comment_list_title');
}

function highlightRow() {
	if(yf_id.length === 0) return;

	scrollToRow(yf_id);

	var jid = "#" + yf_id;
	yf_id = '';

	var e = $(jid);
	if(!e && e.length === 0) return;

	e.highlightFade('yellow');
}

function post_list_data(x, s)
{
    var result = $.parseJSON(x.responseText);
    // 返却メッセージ
    if (result.msg !== "OK") {
        alert(result.msg);
        return;
    }

    var header = result.header;
    var fileList = result.dataList;
    var col_cnt = header.length;
    var child_object_type_id = result.child_object_type_id;
    if (isEditMode == 'True' && child_object_type_id !== '') {
        $('#edit_btn_group').show();
        $('#listArea').css('top', '35px');
    }

    var listTable = $("<table></table>").attr("id", "Dummy").attr("class", "datalistC");
    var rowEmHead = $("<tr></tr>");
    $.each(header, function(index, value) {
        rowEmHead.append($("<th></th>").text(value.property_name).attr("style", value.td_style));
    });
    listTable.append(rowEmHead);

    $.each(fileList, function(index, entity) {
        var rowEm = $("<tr></tr>").attr("class", "unread");
        $.each(header, function(index, value) {
            var ids = result.id;
            if (typeof(cur_view_type) !== "undefined" && cur_view_type == "KEYWORD") {
                ids = entity["parent_folder_id"];
            }
            var object_id = entity["object_id"];
            var property_type = value["property_type"];
            var file_id = entity["file_id_" + index];
            var file_cnt = entity["file_cnt_" + index];
            var txtValue = entity["col_" + index];
            if ("SELECT" == property_type) {
                txtValue = entity["col_" + index + "_label"];
            }
            if ("URL" == value.link_type
                && typeof entity["col_" + index + "_label"] !== "undefined") {
                txtValue = entity["col_" + index + "_label"];
            }

            // 編集モードの場合
            if (isEditMode == 'True') {
                // 詳細画面へ遷移
                if(index == 0) {
                    // リンク対象の列のデータがNULLの場合、表示するテキストを’___’にしてリンクを設定する
                    if (txtValue == "") txtValue = "___";
                    var aEm = $("<a></a>").text(txtValue)
                                          .attr("href", "javascript:void(0);")
                                          .attr("onClick", "openPropertyPage('" + ids + "', '" + object_id + "', 'NEW_WINDOW')");
                    rowEm.append($("<td></td>").append(aEm).attr("style", value.td_style));
                } else if("URL" == value.link_type) {
                    // データの種類がURLリンクの場合
                    var tdEm = $("<td></td>").attr("style", value.td_style);
                    if (entity["col_" + index] !== "") {
                        // PropertyにURLを入力する場合、<a>タグでリンクを付与
                        tdEm.text(txtValue);
                    }
                    rowEm.append(tdEm);
                } else {
                    // デフォルト設定
                    rowEm.append($("<td></td>").text(txtValue).attr("style", value.td_style));
                }
            // 参照モードの場合
            } else {
                // 詳細画面へ遷移
                if("PROPERTY" == value.link_type && object_id !== null && object_id !== "") {
                    // リンク対象の列のデータがNULLの場合、表示するテキストを’___’にしてリンクを設定する
                    if (txtValue == "") txtValue = "___";
                    var aEm = $("<a></a>").text(txtValue)
                                          .attr("href", "javascript:void(0);")
                                          .attr("onClick", "openPropertyPage('" + ids + "', '" + object_id + "', 'NEW_WINDOW')");
                    rowEm.append($("<td></td>").append(aEm).attr("style", value.td_style));
                // データの種類がファイルの場合
                } else if("FILE" == value.link_type && file_id !== null && file_id != "") {
                    var aEm = $("<a></a>").text(txtValue).attr("href", "javascript:void(0);");
                    if (file_cnt == 1) {
                        aEm.attr("onClick", "downloadFile('" + file_id + "')");
                    } else {
                        aEm.attr("onClick", "fileDetail('" + object_id + "', '" + file_id + "', '" + value.link_type_id + "')");
                    }
                    rowEm.append($("<td></td>").append(aEm).attr("style", value.td_style));
                // データの種類がURLリンクの場合
                } else if("URL" == value.link_type) {
                    var tdEm = $("<td></td>").attr("style", value.td_style);
                    if (entity["col_" + index] !== "") {
                        // PropertyにURLを入力する場合、<a>タグでリンクを付与
                        tdEm.append($("<a></a>").text(txtValue).attr("href", entity["col_" + index]).attr("target", "_blank"));
                    }
                    rowEm.append(tdEm);
                } else {
                    // デフォルト設定
                    rowEm.append($("<td></td>").text(txtValue).attr("style", value.td_style));
                }
            }
        });
        listTable.append(rowEm);
    });
    var contentDiv = $("<div></div>")
                        .attr("id", "TlibTableContentsList")
                        .attr("class", "TlibTableC");
    contentDiv.append(listTable);

    $("#listArea").empty().append(contentDiv);
	last_list_hash = location.hash;
	hide_contents();
	hide_null_loading();

	if(document.hasFocus()) {
		$("#TlibTableContentsList").focus();
	}
	initFileListTable();

	highlightRow();
}

function get_list_data() {
	if(last_list_hash === location.hash && !refresh_list_flg) {
		hide_contents();
		return;
	}

    var id = get_page_hash_opt('id');
    if(id.length === 0) {
		return;
	}

	show_null_loading();
	if(document.hasFocus()) {
		$("#listArea").html("Loading...").focus();
	}

	$.ajax({
		url: "get_file_list?view_type=" + cur_view_type + "&db_id=" + $("#db_id").val() + "&id=" + id,
		cache: false,
		complete: post_list_data
	});
}

function initFileListTable() {
    ContentsList = new TlibHeaderFixedTable();
    ContentsList._table_div = 'TlibTableContentsList';
    ContentsList._table_header_div = 'TlibTableHeaderContentsList';
    ContentsList._table_height = -1;
    ContentsList._header_cols = 0;
    ContentsList._header_rows = 0;
    ContentsList._no_resize_bind = 1;
    ContentsList._tr_bg_color = '';
    if ('' !== '') {
        ContentsList._td_border_color = '';
    }
    ContentsList.init();
    ContentsList_resize = function() {
        ContentsList._onResizeWindow();
    };
}

function post_tree_list_data(x, s)
{
	$("#listArea").html(x.responseText);
	last_list_hash = location.hash;
	hide_contents();
	hide_null_loading();

	var id = get_page_hash_opt('tree_data_id') || $('#default_tree_data_id').val();
	$(".tt_tr").removeClass('tt_tr_active');
	$("#" + id + "").addClass('tt_tr_active');

	if(document.hasFocus()) {
		$("#TlibTableContentsList").focus();
	}

	highlightRow();
}

function get_tree_list_data() {
	if(document.hasFocus()) {
		$("#listArea").focus();
	}

	var tree_type = get_page_hash_opt('tree_type');
	var id = get_page_hash_opt('tree_data_id') || $('#default_tree_data_id').val();
	if(id.length === 0) {
		$("#listArea").html("");
		return;
	}
	var page_no = get_page_hash_opt('page_no');
	if(page_no.length === 0) { page_no = 1; }
	var sort_key = get_page_hash_opt('sort_key');
	var sort_order = get_page_hash_opt('sort_order');

	show_null_loading();
	$("#listArea").html("Loading...");

	$.ajax({
		url: "contents_tree.cgi?func=" + tree_type +
			"&tree_data_id=" + id +
			"&page_no=" + page_no + "&sort_key=" + sort_key +
			"&sort_order=" + sort_order,
		cache: false,
		complete: post_tree_list_data
	});
}

function on_hashchange() {
	var h = get_page_hash();
	if(h === '#!l') {
		hide_hsplitter();
		get_list_data();
		refresh_list_flg = false;
	} else {
		hide_contents();
	}

	no_incr_read_cnt_flg = false;
}
/////////////////////////////////////////////////////////////////////

function on_unload() {
}

function reload_all() {
	set_page_hash_reload(location.hash);
}

function set_page_hash_reload(h) {
	// 大きいコンテンツを表示しているとき、on_hashchangeの前で遅くなるため
	// ここで非表示にする
	cur_contents_id = '';
	$("#contentsViewArea").hide();
	$("#contentsView").html("");

	refresh_list_flg = true;
	set_page_hash(h);
}

function reload_list() {
	refresh_list_flg = true;
}

function reload_contents(cid, copy_from_contents_id, force_reload_flg) {
	if(cur_contents_id == cid ||
		cur_contents_id === copy_from_contents_id ||
		force_reload_flg) {
		// cidで指定されたコンテンツを表示中のときは、最新の状態にする
		cur_contents_id = '';
		var new_h = "#!c&contents_id=" + cid;

		no_incr_read_cnt_flg = true;
		set_page_hash_reload(new_h);
	} else {
		// cidで指定されたコンテンツを表示していないとき
		if(get_page_hash() === '#!c') {
			// 別のコンテンツを表示しているときは、画面を更新しない
			// コンテンツを閉じたときにリストを更新するようにする
			refresh_list_flg = true;
		} else {
			// 別のコンテンツを表示しているときは、画面を更新しない
			// リスト表示は更新する
			set_page_hash_reload(location.hash);
		}
	}
}

function show_list(type) {
	var new_h = "#!l&" + type;
	last_list_hash = '';
	set_page_hash(new_h);
}

function resize_contents_body() {
	// FIXME: contentsScrAreaのtopを調整する？
	return;
}

function select_contents(target)
{
	if(!target) return;

	if(document.body.createTextRange) {
		var range = document.body.createTextRange();
		range.collapse(true);
		range.moveToElementText(target);
		range.select();
	} else {
		// FIXME: firefox/chromeでも選択範囲を指定できるようにする
		alert_dlg('Error', 'This function supports IE only');
	}
}

function contents_focused()
{
	var parents = $(document.activeElement).parents();
	var len = parents.length;
	for(var i = 0; i < len; i++) {
		if(parents[i].id === "contentsViewArea") return true;
	}
	return false;
}

function keydown_handler(e)
{
	var KEY_BACK = 8;
	var KEY_DELETE = 46;
	var KEY_F5 = 116;
	var KEY_R = 82;
	var KEY_ESC = 27;
	var KEY_A = 65;
	var KEY_B = 66;
	var KEY_SPACE = 32;

	var h = get_page_hash();
	if(e.which === KEY_ESC) {
		if($('#jqmodal_dlg').is(':visible')) {
			close_jqmodal_dlg();
		} else if($('#folder_select_dlg').is(':visible')) {
			cancel_folder_dlg();
		} else if($('#search_menu_dlg').is(':visible')) {
			close_search_form();
		} else if($('#recipient_dlg').is(':visible')) {
			close_recipient_dlg();
		}
	}

	if(e.ctrlKey && e.keyCode === KEY_A) {
		if($('#recipient_dlg').is(':visible')) {
			select_recipient_dlg_data();
			e.preventDefault();
			return;
		}
	}

	if(h === '#!c' && (e.which === KEY_SPACE || e.which === KEY_B)) {

		var active_elm = document.activeElement;

		if(active_elm.tagName !== 'INPUT' &&
			active_elm.tagName !== 'TEXTAREA') {
			var area = $('#contentsScrArea');
			var t = area.scrollTop();
			var h = area.height();
			if(e.which === KEY_SPACE) {
				var new_t = t + h - 30;
				$('#contentsScrArea').scrollTop(new_t);
			} else {
				var new_t = t - h + 30;
				if(new_t < 0) new_t = 0;
				$('#contentsScrArea').scrollTop(new_t);
			}
			e.preventDefault();
		}
	}

	if(h === '#!c' && e.ctrlKey && e.shiftKey && e.which === KEY_A) {
		select_contents($('#selectTarget')[0]);
		e.preventDefault();
	}
}

function resize_object()
{
	if($("#contentsBody").is(':visible')) {
		resize_contents_body();
	}
	if(typeof window.ContentsList_resize === 'function') {
		ContentsList_resize();
	}
}

function resize_handler(e)
{
	if(vsplitter) {
		vsplitter.trigger('resize');
	} else {
		resize_object();
	}
}

function hide_hsplitter() {
	if(hsplitter) {
		$("#treeArea").hide();
		$("#hsplitbar").hide();
		hsplitter.trigger("resize");
	}
}

function show_hsplitter() {
	if(hsplitter) {
		var treeArea = $("#treeArea");
		treeArea.show();
		if(treeArea.height() < 100) {
			treeArea.height(200);
		}
		$("#hsplitbar").show();
		hsplitter.trigger("resize");
	} else {
		$("#treeArea").show().height(200);
		hsplitter = $("#treeListArea").splitter({
			type: "h",
			outline: true,
			minTop: 0, minBottom: 50,
			width_adjust: 10,
			callback: function(s) {
				resize_object();
			}
		});
		hsplitter.trigger("resize");
	}
}

function focus_contents() {
	if(document.hasFocus()) {
		// scrollbarがあるdivはfocusできる
		// divにscrollbarがない場合、tabindexが設定されていればfocusできる
		$("#contentsScrArea").attr("tabindex", -1).focus();
	}
}

function on_ready() {
	$("body").keydown(keydown_handler);

	$("#contentsViewArea").click(function() {
		focus_contents();
	});

	// splitterを初期化する前に、bindする
	$(window).bind('resize', resize_handler);

	// jquery splitterの初期化
	// trigger("resize")を指定しないと、最初の表示が崩れる
	vsplitter = $("#middleArea").splitter({
		type: "v",
		outline: true,
		minLeft: 260, minRight: 300,
		resizeToWidth: true,
		accessKey: 'I',
		callback: function(s) {
			if(hsplitter) {
				hsplitter.trigger('resize');
			} else {
				resize_object();
			}
		}
	});
	vsplitter.trigger("resize");

	// hashchange eventを登録 (jquery.hashchange)
	$(window).hashchange(function() { on_hashchange(); });

	db_title = document.title;

	// ページロード時に実行
	//if(!location.hash && default_list) {
	//	set_page_hash(default_list);
	//} else {
	//	$(window).hashchange();
	//}

	// ブラウザを閉じたり、リロードする場合に、ロックを解放する
	// (IEのみ動作確認済み)
	$(window).unload(on_unload);
};

/////////////////////////////////////////////////////////////////////
//
function on_load_jqmodal_dlg(h) {
	var w = h.w;
	var l = ($(window).width() / 2) - (w.width() / 2);
	var t = ($(window).height() / 2) - (w.height() / 2);
	w.css('left', l).css('top', t).jqDrag('.jqDnRHandle').
		css('opacity', '1.0');
}

function load_jqmodal_dlg(href) {
	var d = $('#jqmodal_dlg');
	d.jqm({ajax:href, modal: false, onLoad:on_load_jqmodal_dlg}).
		css('opacity', '0').jqmShow();
}

function close_jqmodal_dlg() {
	$('#jqmodal_dlg').jqmHide();
}
/////////////////////////////////////////////////////////////////////
function post_mark_contents_as_read(result) {
	if(result.status === 'Error') {
		alert_dlg('Error', result.msg);
		return;
	}

	reload_all();
}

/////////////////////////////////////////////////////////////////////
// copy from tlib::jquery_util2::print_blockui_js2
function blockUIForDownload(dl_random_str, max_wait_sec) {
	var intervalId;

	var wait_msec = 0;
	var interval_msec = 200;
	var max_wait_msec = max_wait_sec * 1000;

	// polling cookie
	intervalId = window.setInterval(function() {
		wait_msec += interval_msec;

		if ($.cookie('dl_random_str') === dl_random_str) {
			// stop polling
			$.unblockUI();
			clearInterval(intervalId);
		} else if(wait_msec > max_wait_msec) {
			clearInterval(intervalId);
			$.unblockUI();
			return;
		}
	}, interval_msec);
}

// copy from tlib::jquery_util2::print_blockui_js2
function getRandomStrForDownload() {
	var strong = 1000;
	return new Date().getTime().toString(16) +
		Math.floor(strong * Math.random()).toString(16);
}

// copy from tlib::jquery_util2::print_blockui_js2
function doDownloadWithBlockUI(url, wait_msg, img_src, max_wait_sec) {
	$.blockUI({
		message: '<div><img src="' + img_src + '" ' +
			'style="margin-right:5px;">' + wait_msg + '</div>',
		css: {padding: '25px'},
		baseZ: 10000
	});
	var dl_random_str = getRandomStrForDownload();
	location.href = url + '&dl_random_str=' + dl_random_str;
	blockUIForDownload(dl_random_str, max_wait_sec);
	return true;
}

/////////////////////////////////////////////////////////////////////

// CMSプロジェクト用
function _get_location_path() {
    var location = window.location;
    var pathname = location.pathname;
    var url = location.protocol + "//" + location.host;
    var re = new RegExp("/(.+?)/");
    if(pathname.match(re)) {
        url += "/" + RegExp.$1;
    }
    return url;
}
/////////////////////////////////////////////////////////////////////

return {
	set_page_hash: set_page_hash,
	set_page_hash_reload: set_page_hash_reload,
	show_attach_files: show_attach_files,
	close_attach_files: close_attach_files,

	on_ready: on_ready
};

};

