$(function() {
    // 選択可能テーブルのclickイベント追加
    selectedTableTr();
    
    // IE9バグ－テーブルセルずれ対応
    //var browser = $.browser;
    //if ( browser.msie && browser.version.slice(0,3) == "9.0" ) {
    /*
        $('table').each(function(index) {
                var replace = $(this).html().replace(/td>\s+<td/g,'td><td'); 
                $(this).html(replace);
        });
    */
    //}
});

function get_browser() {
    var userAgent = window.navigator.userAgent.toLowerCase();

    if (userAgent.indexOf('opera') !== -1) {
        return 'opera';
    } else if (userAgent.indexOf('msie') !== -1) {
        return 'ie';
    } else if (userAgent.indexOf('trident/7.0') !== -1) {
        return 'ie11';	//IE11
    } else if (userAgent.indexOf('chrome') !== -1) {
        return 'chrome';
    } else if (userAgent.indexOf('safari') !== -1) {
        return 'safari';
    } else if (userAgent.indexOf('gecko') !== -1) {
        return 'gecko';
    } else {
        return '';
    }
}

function ajax_post(url, data, success_func, err_func_name)
{
    $.ajax({
        type: 'post',
        url: url,
        data: data,
        dataType: 'json',
        success: success_func,
        error: function (xmlhttprequest, textstatus, errorThrown) {
            // ファンクションが存在する場合
            if (typeof alert_dlg === "function") {
                alert_dlg("Error", "Error at " + err_func_name + "<br>\n" +
                    xmlhttprequest.responseText + "<br>\n" +
                    "HttpStatus: " + xmlhttprequest.status + "<br>\n" +
                    "TextStatus: " + textstatus + "<br>\n" +
                    "Error: " + errorThrown.message);
            } else {
                alert("Error at " + err_func_name + "<br>\n" +
                    xmlhttprequest.responseText + "<br>\n" +
                    "HttpStatus: " + xmlhttprequest.status + "<br>\n" +
                    "TextStatus: " + textstatus + "<br>\n" +
                    "Error: " + errorThrown.message);
            }
        },
        cache: false,
        async: false
    });
}

/**
 * 選択可能テーブルのclickイベント追加
 */
function selectedTableTr(){
    $("table.selectedTable tr").on('click', function() {
        selectedTr(this);
    });
}

/**
 * 表示（フェードイン）
 * @param {type} targetId
 * @returns {undefined}
 */
function showContent(targetId) {
    // フェードイン
    $("." + targetId + "-content").show("drop");
    // ボタン制御
    $("." + targetId + "-showbtn").css("display", "none");
    $("." + targetId + "-hidbtn").css("display", "inline");
}

/**
 * 非表示（フェードアウト）
 * @param {type} targetId
 * @returns {undefined}
 */
function hidContent(targetId) {
    // フェードアウト
    $("." + targetId + "-content").hide("drop");
    // ボタン制御
    $("." + targetId + "-showbtn").css("display", "inline");
    $("." + targetId + "-hidbtn").css("display", "none");
}

/**
 * 検索条件の表示（フェードイン）
 * @returns {undefined}
 */
function openCondition() {
    $(".search-condition").show("drop");
    // ボタン制御
    $(".opencondition").css("display", "none");
    $(".closecondition").css("display", "inline");
}

/**
 * 検索条件の非表示（フェードアウト）
 * @returns {undefined}
 */
function closeCondition() {
    $(".search-condition").hide("drop");
    // ボタン制御
    $(".opencondition").css("display", "inline");
    $(".closecondition").css("display", "none");
}

/**
 * selectedTableクラスがあるテーブルの行選択制御
 * @param thisObj
 */
function selectedTr(thisObj) {
    $(thisObj).parents("table").find("tr.selected").removeClass("selected");
    $(thisObj).addClass("selected");
}

/**
 * selectedTableクラスがあるテーブルの選択されている行オブジェクトを取得
 *
 * ＜使用例＞
 *  var selectedPlantTr = getSelectedTr($("#plantCodeTable"));
 *  if (selectedPlantTr === null || selectedPlantTr.length == 0) {
 *      alert("対象プラントを選択してください。");
 *      return;
 *  } else {
 *      var selectPlant = selectedPlantTr.find("td").html();
 *      if (selectPlant == null) {
 *          output['plantCode'] = selectPlant;
 *          // 親画面へ返却
 *          opener.closePlantCodeWindow(output);
 *          window.close();
 *      }
 *  }
 *
 * @param tableObj
 * @returns trObj
 */
function getSelectedTr(tableObj) {
    return $(tableObj).find("tr.selected");
}

var isEditFlg = false;
function checkEdit() {
    if (isEditFlg) {
        if (confirm(contentDataChangedMessage)) {
            return true;
        }
    } else {
        return true;
    }
    return false;
}
function checkEditCloseWindow() {
    if (isEditFlg) {
        if (confirm(contentDataChangedMessage)) {
            return true;
        }
    }
    window.open('about:blank', '_self').close();
}
function checkEditTabClick() {
    if (isEditFlg) {
        return confirm(contentEditDataDeleteMessage);
    }
    return true;
}

/**
 * 確認ダイアログ
 *
 * @param {type} message メッセージ本文
 * @param {type} callback コールバック関数を指定する。引数ボタン選択の結果が入る。
 *                OK:true / キャンセル:false
 * @returns {confirmDialog}
 */
function confirmDialog(message, callback){
    var _dlg = $('<div>'+message+'</div>');
    var _buttons = {};
    
    _buttons[buttonYesMessage] = function(){$(this).dialog('close');callback(true);};
    _buttons[buttonNoMessage]  = function(){$(this).dialog('close');callback(false);};
    
    _dlg.dialog({
        modal:true,
        draggable:true,
        title:labelCheckdMessage,
        height:130,
        width:320,
        resizable:false,
        closeOnEscape: false,
        buttons:_buttons,
        overlay:{ opacity:5.0},
        open:function(event, ui){ $(".ui-dialog-titlebar-close").hide();}
    });
}

function returnLogin(loginUrl) {
    window.open(loginUrl);
    closeWindow();
}

function closeWindow(){
    confirm_before_unload_flg = 0;
    window.open("about:blank","_self").close();
}

/**
 * 小数点第n位で四捨五入した値を返します。
 * @param value
 * @param n
 */
function round(value, n) {
  return Math.round(value * Math.pow(10, n)) / Math.pow(10, n);
}

/**
 * 整数をカンマ区切りにします。
 * @param val
 */
function addFigureVal(val) {
    if (val !== "") {
        val = Trim(val);
        var v = UnformatNumber(val);
        var num = new String(v).replace(/,/g, "");
        while (num !== (num = num.replace(/^(-?\d+)(\d{3})/, "$1,$2")));
        return num;
    }
    return val;
}

/**
 * 書式化された数値を戻す
 * @param sVal
 */
function UnformatNumber(sVal) {
    var nVal = new String();
    sVal = String(sVal);
    var half = "-.0123456789";
    var full = "-.０１２３４５６７８９";
    for (i = 0; i <= sVal.length; i++) {
        if (full.indexOf(sVal.charAt(i), 0) > 0) {
            nVal += half.charAt(full.indexOf(sVal.charAt(i), 0));
        } else if ( "-.0123456789".indexOf(sVal.charAt(i), 0 ) !== -1) {
            nVal += sVal.charAt(i);
        }
    }
    if (nVal.length === 0) {
        nVal = "";
    }

    return nVal;
}

/**
 * 文字列から空白を削除する
 * @param val
 */
function Trim(val) {
    var sTemp = String(val);
    var sVal = "";
    var i;
    for (i = 0; i < sTemp.length; i++) {
        if (sTemp.charAt(i) !== " " && sTemp.charAt(i) !== "　") {
            sVal += sTemp.charAt(i);
        }
    }
    return sVal;
}