//*********************************************************************//
//                        共通                                         //
//*********************************************************************//
// Dialog用
var dlg; // Dialog Window
var dlg_window; // Dialog Window 情報
var dlg_timer; // Dialogチェック用Interval

// カレントタイム
function getCurrentTime() {
    return new Date().getTime();
}

// blockUI表示
function coverShow(msg) {
    var message = '<div><div class="indicator">' + msg + '</div></div>';
    $.blockUI({
        message: message
        , css: {padding: '25px'}
        , fadeIn: 0
    });
}

// blockUI非表示
function coverHide() {
    $.unblockUI({fadeOut: 0});
}

// 半透明レイヤー(Block UI)がクリックされたとき、ダイアログにfocusする
function onClickDlgOverlay() {
    if (dlg_window) {
        if (!dlg_window.closed) {
            dlg.focus();
        }
    }
}

// Dialogの表示
function openDlg(url, winName) {
    // ウィンドウの2重起動を防止する
    if (typeof (dlg) !== "undefined" && !dlg.closed) {
        dlg.focus();
        return false;
    }

    // BlockUIを表示
    coverShow("");
    // BlockUIをカスタマイズ
    // メッセージ部を非表示
    $("div.blockMsg").hide();
    // クリックされたとき、ダイアログにfocusする
    $("div.blockOverlay").css("z-index", 99999).click(onClickDlgOverlay);

    // 親画面と同じ大きさで開く
    var w = window.innerWidth;
    var h = window.innerHeight;

    if (typeof w === "undefined") {
        w = document.body.clientWidth;
    }
    if (typeof h === "undefined") {
        h = document.body.clientHeight;
    }

    // ダイアログを表示
    dlg = window.open(url, winName, "width=" + w + ",height=" + h + ",scrollbars=yes,resizable=yes,status=yes,location=yes");
    dlg_window = dlg.window;
    dlg.focus();

    // タイマーでダイアログが閉じられたか監視する
    dlg_timer = setInterval(function () {
        checkDlg(winName);
    }, 500);
}

// Dialogの表示
function openDlg2(url, winName, w, h, showCover) {
    // ウィンドウの2重起動を防止する
    if (typeof (dlg) !== "undefined" && !dlg.closed) {
        dlg.focus();
        return false;
    }

    if (showCover) {
        // BlockUIを表示
        coverShow("");
        // BlockUIをカスタマイズ
        // メッセージ部を非表示
        $("div.blockMsg").hide();
        // クリックされたとき、ダイアログにfocusする
        $("div.blockOverlay").css("z-index", 99999).click(onClickDlgOverlay);
    }

    // 表示するウィンドウの位置
    var l_position = Number((window.screen.width - w) / 2);
    var t_position = Number((window.screen.height - h) / 2);

    // ダイアログを表示
    dlg = window.open(url, winName, "width=" + w + ",height=" + h + ", left=" + l_position + ", top=" + t_position + ",scrollbars=no,toolbar=0,menubar=no,resizable=yes,status=no,location=0");
    dlg_window = dlg.window;
    dlg.focus();

    // タイマーでダイアログが閉じられたか監視する
    dlg_timer = setInterval(function () {
        checkDlg(winName);
    }, 500);
}

// Dialogの表示
function openCommentDlg(url, winName) {
    // ウィンドウの2重起動を防止する
    if (typeof (dlg) !== "undefined" && !dlg.closed) {
        dlg.focus();
        return false;
    }

    // BlockUIを表示
    coverShow("");
    // BlockUIをカスタマイズ
    // メッセージ部を非表示
    $("div.blockMsg").hide();
    // クリックされたとき、ダイアログにfocusする
    $("div.blockOverlay").css("z-index", 99999).click(onClickDlgOverlay);

    // 親画面と同じ大きさで開く
    var w = 650;
    var h = 300;

    // 表示するウィンドウの位置
    var l_position = Number((window.screen.width - w) / 2);
    var t_position = Number((window.screen.height - h) / 2);

    // ダイアログを表示
    dlg = window.open(url, winName, "width=" + w + ",height=" + h + ", left=" + l_position + ", top=" + t_position + ",scrollbars=no,toolbar=0,menubar=no,resizable=yes,status=no,location=0");
    dlg_window = dlg.window;
    dlg.focus();

    // タイマーでダイアログが閉じられたか監視する
    dlg_timer = setInterval(function () {
        checkDlg(winName);
    }, 500);
}

// ダイアログが閉じられたかチェックする (intervalタイマーから起動される)
function checkDlg(winName) {
    if (dlg_window) {
        if (dlg_window.closed) {
            dlgClosed(winName);
        }
    }
}

// ダイアログが閉じられたときの処理
function dlgClosed(winName) {
    // Window情報をクリア
    clearInterval(dlg_timer);
    dlg = undefined;
    dlg_window = undefined;
    dlg_timer = undefined;

    dlgCloseMain(winName);
}

// 画面を閉じて、遷移先をコントロールする
function dlgCloseMain(winName) {
    // クリックイベントをクリア
    $("div.blockOverlay").off("click");
    // BlockUIを非表示
    coverHide();

    var formName;
    if (winName.indexOf("CREATE") >= 0) {
        formName = "resultForm";
    } else if (winName.indexOf("SVCDBSYS_EDIT") >= 0) {
        $("#detailform-refreshBtn").click();
    } else if (winName.indexOf("WORKFLOW") >= 0) {
        if (typeof refresh === "function") {
            refresh();
        }
    } else if (winName.indexOf("UPLOAD") >= 0) {
        if (typeof refresh === "function") {
            refresh();
        } else {
            window.location.href = _get_location_path() + '/index';
        }
    }
}

function closeEditDlg() {
    if (checkEdit()) {
        closeWindow();
    }
}

function init_pspromis_datepicker(imgUri) {
    $(".svcdb-datepicker").datepicker({
        showOn: "button",
        buttonImage: imgUri,
        buttonImageOnly: true,
        changeMonth: true,
        changeYear: true
    });

    $(".svcdb-ympicker").ympicker({
        showOn: "button",
        buttonImage: imgUri,
        buttonImageOnly: true,
        changeYear: true,
        yearSuffix: "年",
        monthSuffix: "月",
        dateFormat: "yy/mm"
    });
}

var search_result_list;

function initTlibJSFixedHeaderTable(prop) {
    var obj;
    if (typeof prop === "string") {
        obj = {table_div: prop, no_resize_bind: 0};
    } else if (typeof prop === "object") {
        obj = prop;
    } else {
        return false;
    }
    search_result_list = new TlibHeaderFixedTable();
    if (typeof obj.header_rows !== "undefined" && obj.header_rows !== "") {
        search_result_list._header_rows = obj.header_rows;
    }
    search_result_list._table_div = obj.table_div;
    search_result_list._table_header_div = obj.table_header_div;
    search_result_list._no_resize_bind = !obj.no_resize_bind ? 0 : obj.no_resize_bind;
    if (typeof obj.header_cols !== "undefined" && obj.header_cols !== "") {
        search_result_list._header_cols = obj.header_cols;
    }
    if (typeof obj.bg_color !== "undefined" && obj.bg_color !== "") {
        search_result_list._tr_bg_color = obj.bg_color;
    }
    if (typeof obj.table_height !== "undefined" && obj.table_height !== "") {
        search_result_list._table_height = obj.table_height;
    }
    search_result_list._adjust_right_table_tr_height = true;
    search_result_list._last_child_td_right_color = "#777";
    search_result_list._use_get_bounding_client_rect_on_ie11 = obj.use_get_bounding_client_rect_on_ie11;
    search_result_list.init();
}

function destroyTlibJSFixedHeaderTable(list_name) {
    var $t = $("#" + list_name);
    if (!$t.length) return false;

    $t.prevAll(".TlibFixedHeaderTableDivCol").remove();
    $t.prevAll(".TlibFixedHeaderTableDivTop").remove();
    $t.removeClass("TlibFixedHeaderTableDiv");
    $("#TlibFixedHeaderTable3_CSS").remove();
    $t.children("table").removeClass("TlibFixedHeaderTable");
    $t.children("table").css("top", "");
    search_result_list = null;
}

function adjustFixedHeaderTable() {
    if (search_result_list) search_result_list.adjustTableSize();
}

// ajax実行後ヘッダー固定
function initFixedHeaderTable() {
    if ($("div.search-result-div").is(":visible")) {
        if (search_result_list) search_result_list.init();
    }
}

// 画面を開く共通ファンクション
function openWindow(url, windowNm) {
    var windowTarget = window.open(url, windowNm + getCurrentTime());
    windowTarget.focus();
}

function closeWindow() {
    confirm_before_unload_flg = 0;
    if (document.all) {
        (window.open("", "_self").opener = window).close();
    }
    window.close();
}

// 画面を開く共通ファンクション
function openResizeWindow(url, windowNm) {
    var h = window.screen.height;
    var w = window.screen.width;

    // 表示するウィンドウの位置
    var l_position = Number((window.screen.width - w) / 2);
    var t_position = 0;

    var windowTarget = window.open(url, windowNm + getCurrentTime(), "width=" + w + ",height=" + h + ",left=" + l_position + ",top=" + t_position +
        ",scrollbars=yes,menubar=yes,resizable=yes,status=yes,location=yes");
    windowTarget.focus();
}

// 検索ページを1ページ
function initCurrentPage() {
    $("input[type=hidden]").each(function () {
        var id = $(this).attr("id");
        if (typeof id !== "undefined") {
            if (id.indexOf("currentPage") >= 0) {
                $(this).val(1);
            }
        }
    });
}

// ページャー
function pagination(currentPage) {
    $("#searchForm [name=searchForm-currentPage]").val(currentPage);
    if (typeof (doSearch) === "function") {
        doSearch();
    }
}

//###########jqModal#######################
function on_load_jqmodal_dlg(h) {
    var w = h.w;
    var l = ($(window).width() / 2) - (w.width() / 2);
    var t = ($(window).height() / 2) - (w.height() / 2);
    w.css("left", l).css("top", t).jqDrag(".jqDnRHandle").css("opacity", "1.0");
}

function load_jqmodal_dlg(url, func) {
    $("#jqmWindow").jqm({
        ajax: url,
        onLoad: func,
        trigger: false
    }).css("opacity", "0").jqmShow();
}

function load_jqmodal_dlg_post(url, func) {
    $("#jqmWindow").jqm({
        ajax: url,
        onLoad: func,
        trigger: false
    }).css("opacity", "0").jqmShow();
}

function close_jqmodal_dlg() {
    $("#jqmWindow").jqmHide();
}

function _get_location_path() {
    var location = window.location;
    var pathname = location.pathname;
    var url = location.protocol + "//" + location.host;
    var re = new RegExp("/(.+?)/");
    if (pathname.match(re)) {
        url += "/" + RegExp.$1;
    }
    return url;
}

function popupExcelOutput() {
    var sales_class = $("#sales_class").val();
    var gaikaKbn = $("input:radio[name='disp_currency']:checked").val();
    var url = _get_location_path() + "/ws/excel_output/select_template?sales_class=" + sales_class + "&gaika_kbn=" + gaikaKbn;
    load_jqmodal_dlg(url, on_load_jqmodal_dlg);
}

function excel_download() {
    $("#outputExcel").click();
}

function csv_download() {
    $("#outputCsv").click();
}

function initResultListClick() {
    var $fixedColTrs = $(".search-result-div").find("div.TlibFixedHeaderTableDivCol > table > tbody > tr");
    var $fixedTblTrs = $(".search-result-div").find("div.TlibFixedHeaderTableDiv > table > tbody > tr");
    var lastSelected, isCallback, isHovered, keys;
    lastSelected = {col: null, tbl: null};
    isCallback = {col: false, tbl: false};
    isHovered = {col: false, tbl: false};
    keys = ["col", "tbl"];

    var renderSelectedRows = function (e, $this, $thisObj, $targetObj, keyIdx) {
        var prop = keys[keyIdx];
        var cb, lstSel;
        if (isCallback.hasOwnProperty(prop)) {
            cb = isCallback[prop];
        }
        if (lastSelected.hasOwnProperty(prop)) {
            lstSel = lastSelected[prop];
        }
        if (cb) {
            isCallback.col = false;
            isCallback.tbl = false;
            return;
        }
        if ($this.hasClass("data_selected")) {
            $this.removeClass("data_selected");
        } else {
            $this.addClass("data_selected");
        }

        var start = $thisObj.index($this);
        if (!lstSel) {
            lstSel = $this;
        }
        if (e.shiftKey) {
            var end = $thisObj.index(lstSel);
            $thisObj.slice(Math.min(start, end), Math.max(start, end) + 1).prop("class", lstSel.attr("class"));
        } else if (e.ctrlKey) {
        } else {
            $thisObj.removeClass("data_selected");
            $this.addClass("data_selected");
        }
        lastSelected[prop] = $this;
        isCallback[prop] = true;
        renderSelectedRows(e, $($targetObj.get(start)), $targetObj, $thisObj, Math.abs(keyIdx - 1));
    };
    var rewriteTableHover = function ($this, $thisObj, $targetObj, keyIdx, func) {
        var prop = keys[keyIdx];
        var cb;
        if (isHovered.hasOwnProperty(prop)) {
            cb = isHovered[prop];
        }
        if (cb) {
            isHovered.col = false;
            isHovered.tbl = false;
            return false;
        }
        if ($.isFunction(func)) {
            func.call(this, $this);
        }
        isHovered[prop] = true;
        var start = $thisObj.index($this);
        rewriteTableHover($($targetObj.get(start)), $targetObj, $thisObj, Math.abs(keyIdx - 1), func);
    };

    $fixedColTrs.each(function () {
        var t = $(this);
        t.attr("draggable", "false");
    });

    $fixedTblTrs.each(function () {
        var t = $(this);
        t.attr("draggable", "false");
    });

    var $fixedColTable = $(".search-result-div").find("div.TlibFixedHeaderTableDivCol > table");
    var $fixedTblTable = $(".search-result-div").find("div.TlibFixedHeaderTableDiv > table");
    $fixedColTable.on("dragstart", "tr", dragStartFromList);
    // 20190212 不具合修正、start
    var enkaTotalRow = $("#undefined_HD tr")[0];
    var titleRow = $("#undefined_HD tr")[1];
    $fixedColTable.on("click", "tr", function (e) {
        if (this === enkaTotalRow || this === titleRow) {
            return;
        }
        var tr = $(this);
        renderSelectedRows(e, tr, $fixedColTrs, $fixedTblTrs, 1);
    });
    $fixedColTable.on("mouseenter", "tr", function (e) {
        e.preventDefault();
        if (this === enkaTotalRow || this === titleRow) {
            return;
        }
        // 20190212 不具合修正、end
        var tr = $(this);
        rewriteTableHover(tr, $fixedColTrs, $fixedTblTrs, 0,
            function (t) {
                if (!t.hasClass("data_selected")) {
                    t.addClass("fixedTable_hover");
                }
            }
        );
    });
    $fixedColTable.on("mouseleave", "tr", function (e) {
        e.preventDefault();
        var tr = $(this);
        rewriteTableHover(tr, $fixedColTrs, $fixedTblTrs, 0,
            function (t) {
                t.removeClass("fixedTable_hover");
            }
        );
    });

    $fixedTblTable.on("dragstart", "tr", dragStartFromList);
    $fixedTblTable.on("click", "tr", function (e) {
        if (this === enkaTotalRow || this === titleRow
            || $(this).parents('table').hasClass('inner_table')) {
            return;
        }
        var tr = $(this);
        renderSelectedRows(e, tr, $fixedTblTrs, $fixedColTrs, 1);
    });
    $fixedTblTable.on("mouseenter", "tr", function (e) {
        e.preventDefault();
        if (this === enkaTotalRow || this === titleRow) {
            return;
        }
        var tr = $(this);
        rewriteTableHover(tr, $fixedTblTrs, $fixedColTrs, 1,
            function (t) {
                if (!t.hasClass("data_selected")) {
                    t.addClass("fixedTable_hover");
                }
            }
        );
    });
    $fixedTblTable.on("mouseleave", "tr", function (e) {
        e.preventDefault();
        var tr = $(this);
        rewriteTableHover(tr, $fixedTblTrs, $fixedColTrs, 1,
            function (t) {
                t.removeClass("fixedTable_hover");
            }
        );
    });
}

//###########DRAG & DROP#######################
function dragStartFromList(e) {
    var jobId = $(e.target).attr("id");
    if (!jobId) return false;
    jobId = jobId.replace("_col", "");
    e.originalEvent.dataTransfer.setData("text", jobId);
}

// 条件表示
function openSearch(func) {
    var id = $('input[id*="-tabName"]').val();
    if (!(id && $("div#" + id).length)) return false;

    if (typeof func === "undefined" || func === "" || !$.isFunction(func)) {
        func =
            function () {
                resizeCondition();
                adjustFixedHeaderTable();
            };
    }

    $("#condition_area").show(0);
    $("div#" + id).show("drop", func);
    $(".opencondition").hide();
    $(".closecondition").show();
}

// 条件非表示
function closeSearch(func) {
    var id = $('input[id*="-tabName"]').val();
    if (!(id && $("div#" + id).length)) return false;

    if (typeof func === "undefined" || func === "" || !$.isFunction(func)) {
        func =
            function () {
                adjustFixedHeaderTable();
                hideCover();
            };
    }

    $("#condition_area").hide(0);
    $("div#" + id).hide("drop", func);
    $(".opencondition").show();
    $(".closecondition").hide();
}

function showCover(msg) {
    var message = '<div><div class="indicator">' + msg + '</div></div>';
    $.blockUI({
        message: message,
        css: {padding: "25px"},
        fadeIn: 0
    });
}

function hideCover() {
    $.unblockUI({
        fadeOut: 0
    });
}

function searchResult(formName, url) {
    $("#" + formName).attr("action", url);
    $("#" + formName).submit();
}

function resetCondition(formName, url) {
    $("#" + formName).attr("action", url);
    $("#" + formName).submit();
}

function create_form_data(func) {

    // FormDataオブジェクトを用意
    var fd = new FormData();
    fd.append("func", func);

    return fd;
}

/**
 * ノードを開閉する
 * @param {type} targetId 対象テーブルID
 * @param {type} triangleId アイコンID
 * @returns {undefined}
 */
function nodeChange(targetId, triangleId) {
    $("." + targetId + "-content").toggle();
    $("." + targetId + "-hidbtn").toggle();
    var triangle = $("#" + triangleId);
    if (triangle.length > 0) {
        if (triangle.hasClass("triangle-bottom")) {
            triangle.removeClass("triangle-bottom").addClass("triangle-right");
        } else {
            triangle.removeClass("triangle-right").addClass("triangle-bottom");
        }
    }

    if (typeof (resizeMainContent) === "function") {
        resizeMainContent();
    }
}

function msSaveOrOpenBlob(url, openType, waitMessage, fileName, contentType, sendOption) {
    showCover(waitMessage);

    var xhr = new XMLHttpRequest();
    xhr.open(openType, url, true);
    if (typeof (contentType) !== "undefined" && contentType !== "") {
        xhr.setRequestHeader('Content-Type', contentType);
    }
    xhr.setRequestHeader("If-Modified-Since", "0");
    xhr.setRequestHeader('Cache-Control', 'no-cache');
    xhr.responseType = "blob";
    xhr.onreadystatechange = function () {
        var blob = xhr.response;
        if (typeof (fileName) === "undefined" || fileName === "") {
            fileName = getFileNameFromRsHeader(xhr.getResponseHeader("content-disposition"));
        }

        if (xhr.readyState === 4 && xhr.status === 200) {
            // IEの場合
            if (typeof window.navigator.msSaveOrOpenBlob === "function") {
                window.navigator.msSaveOrOpenBlob(blob, fileName);
            } else {
                var link = document.createElement("a");
                link.href = window.URL.createObjectURL(blob);
                link.download = fileName;

                document.body.appendChild(link);
                link.click();
            }
            hideCover();
        } else if (xhr.status === 204) {
            hideCover();
        } else if (xhr.status === 500) {
            hideCover();
        }
    };
    if (typeof (sendOption) !== "undefined" && sendOption !== "") {
        xhr.send(sendOption);
    } else {
        xhr.send();
    }
}

function getFileNameFromRsHeader(headerstr) {
    if (headerstr === null) {
        return "FileNotFound.json";
    }
    var headers = headerstr.split(';');
    var fname = "tmp.xlsx";
    $.each(headers, function (index, value) {
        var vals = value.split('=');
        if (vals[0].trim() === "filename"
            || vals[0].trim() === "filename*") {
            fname = decodeURI(value.slice((value.indexOf('=') + 1), (value.length)));
        }
    });

    return fname;
}

/////////////////////////////////////////////////////////////////////
// ヘルプ
function openHelpWindow() {
    window.open('../../static/help/svcdb_help.pdf');
}

// リスク詳細画面を開く
function openCommonWindow(url, openType, winNm) {
    // 処理モード「0:参照、1:編集」
    var editMode = "0";
    if (typeof (winNm) == "undefined" || winNm == "") {
        winNm = "SVCDBSYS_WINDOW";
    }
    if (openType === "POP_UP") {
        openDlg(url, winNm);
    } else if (openType === "NEW_WINDOW") {
        openWindow(url, winNm);
    } else {
        window.location.href = url;
    }
}

function getSelectedTrsId() {
    var $selectedTrs = $(".search-result-div").find("div.TlibFixedHeaderTableDiv > table > tbody > tr[class*='data_selected']");
    var arrSelectedEle = [];
    $selectedTrs.each(function () {
        arrSelectedEle.push($(this).attr("id"));
    });
    return arrSelectedEle[0];
}

function getOpenFileDetailUrl(turbine_id) {
    return _get_location_path() + "/files_jqmodal?turbine_id=" + turbine_id;
}

function getDownloadCheckUrl(fileId) {
    return _get_location_path() + "/download_file_check?file_id=" + fileId;
}

function getDownloadFileUrl(turbine_id, fileId) {
    return _get_location_path() + "/download_file?turbine_id=" + turbine_id + "&file_id=" + fileId;
}

function getOpenOutageScheduleListUrl(turbine_id) {
    return _get_location_path() + "/outage_schedule_jqmodal?turbine_id=" + turbine_id;
}

function getOutageScheduleDetailUrl(turbine_id, teiken_id, date_start, date_end) {
    return _get_location_path() + "/outage_schedule_detail?turbine_id=" + turbine_id + "&teiken_id=" + teiken_id + "&date_start=" + date_start + "&date_end=" + date_end;
}

function getOutageScheduleEditlUrl(turbine_id, teiken_id, date_start, date_end) {
    return _get_location_path() + "/outage_schedule_edit?turbine_id=" + turbine_id + "&teiken_id=" + teiken_id + "&date_start=" + date_start + "&date_end=" + date_end;
}

// 添付ファイル編集
function popupFileDetail(turbine_id) {
    var url = getOpenFileDetailUrl(turbine_id);
    load_jqmodal_dlg(url, on_load_jqmodal_dlg);
}

// 予定選択画面を開く
function popupOutageScheduleList(turbine_id) {
    var url = getOpenOutageScheduleListUrl(turbine_id);
    load_jqmodal_dlg(url, on_load_jqmodal_dlg);
}

function decodeHtml(s) {
    var HTML_DECODE = {
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
        "&nbsp;": " ",
        "&quot;": "\"",
        "&copy;": ""
    };

    var REGX_HTML_DECODE = /&\w+;|&#(\d+);/g;
    s = (s !== undefined) ? s : "";
    return (typeof s !== "string") ? s :
        s.replace(REGX_HTML_DECODE,
            function ($0, $1) {
                var c = HTML_DECODE[$0];
                if (c === undefined) {
                    if (!isNaN($1)) {
                        c = String.fromCharCode(($1 === 160) ? 32 : $1);
                    } else {
                        c = $0;
                    }
                }
                return c;
            });
};

// 日付書式チェック
function CheckYMDFormat(itm, bemp, msg, focus) {
    if (!bemp || itm.value.length != 0) {
        if (!Chk_Quotation_Terms_YMD(itm)) {
            ColorSet(itm, true);
            if (msg != null && msg != "") alert(msg);
            if (focus) itm.select();
            return false;
        } else {
            ColorSet(itm, false);   //初期化.
        }
    } else {
        ColorSet(itm, false);   //初期化.
    }
    return true;
}

// 日付のyyyy/mm/ddを設定する
function fmtDate(strDate, name) {
    if (strDate === '' || strDate.split("/").length > 1) {
        return;
    }

    if (strDate.length >= 8) {
        var year = strDate.substring(0, 4);
        var month = strDate.substring(4, 6);
        var day = strDate.substring(6, 8);
        rtnStr = year + '/' + month + '/' + day;
    } else {
        return;
    }

    name.value = rtnStr;
    return;
}

// 日付のチェック（From～To）
function checkFromToDate(fromDate, toDate, msg) {

    var date1 = fromDate;
    var date2 = toDate;
    var val1 = date1.val();
    var val2 = date2.val();

    ColorSet(date1[0], false);
    ColorSet(date2[0], false);

    var rtn1 = CheckYMDFormat(date1[0], true, msg, true);
    var rtn2 = CheckYMDFormat(date2[0], true, msg, true);

    if ((val1.length > 0 && !rtn1) || (val2.length > 0 && !rtn2)) {
        return false;
    }
    return true;
}

// 日付のチェック
function checkDate(date, msg) {

    var date1 = date;
    var val1 = date1.val();

    ColorSet(date1[0], false);

    var rtn1 = CheckYMDFormat(date1[0], true, msg, true);

    if ((val1.length > 0 && !rtn1)) {
        return false;
    }
    return true;
}

// 値の比較チェック（bVal < sVal エラー）
function checkValDiff(bVal, sVal, msg) {

    var diffVal1 = bVal;
    var diffVal2 = sVal;
    var val1 = diffVal1.val();
    var val2 = diffVal2.val();

    if (Trim(val1) === "" || Trim(val2) === "") {
        return true;
    }

    ColorSet(diffVal1[0], false);
    ColorSet(diffVal2[0], false);

    if (val1 < val2) {
        ColorSet(diffVal1[0], true);
        alert(msg);
        return false;
    }
    return true;
}

// 未来日付チェック
function CheckDateFuture(itm, bemp, msg, focus) {

    if (!bemp || itm.value.length !== 0) {
        if (!chk_Date_Now(new Date(itm.value))) {
            ColorSet(itm, true);
            if (msg !== null && msg !== "") alert(msg);
            if (focus) itm.select();
            return false;
        } else {
            ColorSet(itm, false);  //初期化.
        }
    } else {
        ColorSet(itm, false);      //初期化.
    }
    return true;
}

// 現在日時より未来の日付かチェックする。
function chk_Date_Now(vDate) {
    var vN = new Date();
    var Y, M, D;

    Y = vDate.getFullYear() - vN.getFullYear();
    M = vDate.getMonth() - vN.getMonth();
    D = vDate.getDate() - vN.getDate();

    if (Y < 0) {                               //過去年ならエラー
        return false;
    }
    if ((Y === 0) && (M < 0)) {                  //年は同じで過去月ならエラー
        return false;
    }
    if ((Y === 0) && (M === 0) && (D < 0)) {   //年、月は同じで過去日ならエラー
        return false;
    }
    return true;
}

// 郵便番号チェック
function CheckPostalNo(itm, bemp, msg, focus) {
    if (!bemp || itm.value.length !== 0) {
        if ("" === chk_Postal_No(itm.value)) {
            ColorSet(itm, true);
            if (msg !== null && msg !== "") alert(msg);
            if (focus) itm.select();
            return false;
        } else {
            ColorSet(itm, false);   //初期化.
        }
    } else {
        ColorSet(itm, false);       //初期化.
    }
    return true;
}

// 郵便番号チェック
function chk_Postal_No(number) {
    var border = new Array("-", "－", "ー", "―", "ｰ", "‐");   // 棒線を全て配列に設定

    for (var i = 0; i < border.length; i++) {         // 棒線全て取り除く
        number = number.replace(border[i], "");
    }

    if (number.match(/[^0-9]+/)) {                  // 数字以外の文字である場合
        return "";
    } else if (!number.match(/^[0-9]{7}$/)) {       // 数字以外の文字である場合
        return "";
    } else {                                        // 正常に入力された場合
        return number;
    }
}

// 数値チェック
function CheckNumeric(itm, vmin, vmax, bemp, msg, focus) {
    if (!bemp || itm.value.length !== 0) {
        if ("" === NumChk(itm.value)) {
            ColorSet(itm, true);
            if (msg !== null && msg !== "") alert(msg);
            if (focus) itm.select();
            return false;
        } else {
            var vNum, vRet = true;
            vNum = eval(itm.value);
            if (vmin !== null && vmin > vNum) vRet = false
            if (vmax !== null && vmax < vNum) vRet = false
            if (!vRet) {
                ColorSet(itm, true);
                if (msg !== null && msg !== "") alert(msg);
                if (focus) itm.select();
                return false;
            } else {
                ColorSet(itm, false);   //初期化.
            }
        }
    } else {
        ColorSet(itm, false);   //初期化.
    }
    return true;
}

// 入力文字数チェック「英数字」
function CheckNumAlphaLength(itm, vmin, vmax, msg, focus) {
    var item = itm[0];
    if (!chkMojiLength(item.value, vmin, vmax) || !vldNumAlpha(item.value)) {
        ColorSet3(itm, true);
        if (msg !== null && msg !== "") alert(msg);
        if (focus) item.select();
        return false;
    } else {
        ColorSet3(itm, false);   //初期化.
    }
    return true;
}

function setupDisp(formName) {
    $("#" + formName + "-basicEditButton").attr("disabled", false);

    if ($("#" + formName + "-basicEditAvailFlg").val() === "false") {
        $("#" + formName + "-basicEditButton").attr("disabled", true);
    }

    if (formName === "detailform") {
    }
}

function post_save_contents() {

    // メイン画面をrefresh
    // Notes: IE8ではtypeof window.opener.reload_contentsが'function'ではなく、
    //		'object'を返す
    try {
        if (window.opener && !window.opener.closed) {
            window.opener.reload_parent_contents();
        }
    } catch (e) {
        alert(e);
    }
}

function outage_schedule_detail(turbine_id, teiken_id, type) {
    var date_start = $("#date_start").val();
    var date_end = $("#date_end").val();
    var url = getOutageScheduleDetailUrl(turbine_id, teiken_id, date_start, date_end);
    if (type == 'NEWWINDOW') {
        openWindow(url, "OUTAGE_SCHEDULE_DETAIL");
    } else {
        window.location.href = url;
    }
}

function outage_schedule_edit(turbine_id, teiken_id, date_start, date_end) {
    window.location.href = getOutageScheduleEditlUrl(turbine_id, teiken_id, date_start, date_end);
}

// 前後スペース削除
String.prototype.trim = function () {
    return this.replace(/(^\s*)|(\s*$)/g, "");
}

//　日付フォーマットチェック
function validator(target) {
    if (isDate(target[0].value.trim()) == false) {
        target[0].select();
        return false;
    }
    return true;
}

// 日付フォーマットチェック（yyyy/mm/dd）
function isDate(dateString) {
    if (dateString.trim() == "") return true;
    // 正規表現チェック（yyyy/mm/dd）
    var r = dateString.match(/^(\d{1,4})\/(\d{1,2})\/(\d{1,2})$/);
    if (r == null) {
        alert("日付指定に不正な値があります。半角YYYY/MM/DD形式で指定してください。");
        return false;
    }
    var d = new Date(r[1], r[2] - 1, r[3]);
    var num = (d.getFullYear() == r[1] && (d.getMonth() + 1) == r[2] && d.getDate() == r[3]);
    if (num == 0) {
        alert("日付指定に不正な値があります。半角YYYY/MM/DD形式で指定してください。");
    }
    return (num != 0);
}

//フォマード文字
String.prototype.format = function () {
    if (arguments.length == 0) return this;
    var param = arguments[0];
    var s = this;
    if (typeof (param) == 'object') {
        for (var key in param)
            s = s.replace(new RegExp("\\{" + key + "\\}", "g"), param[key]);
        return s;
    } else {
        for (var i = 0; i < arguments.length; i++)
            s = s.replace(new RegExp("\\{" + i + "\\}", "g"), arguments[i]);
        return s;
    }
};

//type:success,info,warning,danger
function showMsg(type, msg) {
    var msg_str = '<div class="alert alert-{0} alert-dismissable" style="width:60%;margin-bottom: 0px;">\n' +
        '            <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>\n' +
        '            {1}\n' +
        '          </div>';
    $("#msgDiv").append(msg_str.format(type, msg));
}

function showSaveMsg() {
    showMsg("success", "保存に成功しました");
}

Date.prototype.format = function (fmt) { //author: meizz
    var o = {
        "M+": this.getMonth() + 1,                 //月份
        "d+": this.getDate(),                    //日
        "h+": this.getHours(),                   //小时
        "m+": this.getMinutes(),                 //分
        "s+": this.getSeconds(),                 //秒
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度
        "S": this.getMilliseconds()             //毫秒
    };
    if (/(y+)/.test(fmt))
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt))
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
};