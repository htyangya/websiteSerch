
var sys_admin_col_list_dnd = function() {

	var project_id;
	var object_type;
	var format_name;
	var form_name;
	var col_list_name;
	var preview_url;
	var list_type;

    var drag_obj;
    var drag_obj_next;
    var drag_obj_clone;

	var prev_obj_clone_y;
	var prev_obj_clone_x;

    function setDragImagePos(e) {
        if(drag_obj_clone) {
            var x = e.originalEvent.pageX;
            var y = e.originalEvent.pageY;

			if(x === prev_obj_clone_x && y === prev_obj_clone_y) return;

            drag_obj_clone.css({top: y - 12, left: x - 2});

			prev_obj_clone_y = y;
			prev_obj_clone_x = x;
        }
    }

	function clearDragImage() {
        if(drag_obj_clone) {
			prev_obj_clone_y = -1;
			prev_obj_clone_x = -1;
            drag_obj_clone.remove();
            drag_obj_clone = null;
		}
	}

    function dragStart(e) {
        $(this).addClass('dragitem');
        e.originalEvent.dataTransfer.effectAllowed = 'move';
        e.originalEvent.dataTransfer.dropEffect = 'move';
        //e.originalEvent.dataTransfer.setData("text", $(this).text());
        drag_obj = this;

        var parent_id = $(drag_obj).parent().attr('id');
        if(parent_id === 'col_list') {
            drag_obj_next = $(this).next()[0];
        }

        drag_obj_clone = $(this).clone();

        var x = e.originalEvent.pageX;
        var y = e.originalEvent.pageY;
        drag_obj_clone.css({
            position: 'absolute',
            display: 'block',
            opacity: 0.7,
            zIndex: 9999,
            pointerEvents: 'none'});

        setDragImagePos(e);

        $("body").append(drag_obj_clone);
    }

    function dragEnd(e) {
        if(e.stopPropagation) {
            e.stopPropagation();
        }
        $(this).removeClass('dragitem');

        drag_obj = null;
        drag_obj_next = null;

		clearDragImage();
    }

    function bodyDragOver(e) {
        e.preventDefault();
        e.originalEvent.dataTransfer.dropEffect = 'move';

        setDragImagePos(e);
        return false;
    }

    function dragOver(e) {
        e.preventDefault();
        e.originalEvent.dataTransfer.dropEffect = 'move';

        setDragImagePos(e);
        return false;
    }

    function dragEnter(e) {
        e.preventDefault();
        if(this === drag_obj) {
            e.originalEvent.dataTransfer.dropEffect = 'none';
            return false;
        }
        if(drag_obj_next && this === drag_obj_next) {
            e.originalEvent.dataTransfer.dropEffect = 'none';
            return false;
        }
        e.originalEvent.dataTransfer.dropEffect = 'move';

        var target_id = $(this).attr('id');

        if(target_id === 'drop_target_bottom') {
            $(this).addClass('dragon_bottom');
        } else if(target_id === 'trashcan') {
            var parent_id = $(drag_obj).parent().attr('id');
            if(parent_id === 'col_list') {
                $(this).addClass('dragon_trashcan');
            }
        } else {
            $(this).addClass('dragon');
            $(this).children('.col_div').before('<div class="dropzone"></div>')
;
        }
        return false;
    }

    function dragLeave(e) {
        e.preventDefault();
        $(this).removeClass('dragon_bottom');
        $(this).removeClass('dragon_trashcan');
        $(this).removeClass('dragon');
        $('.dropzone').remove();
        return false;
    }

	function changeCandidateColor(cname, color) {
		var item = $('#col_candidates').children('.colitem[data-cname="' + cname + '"]').children('.col_div');
		$(item).css('background-color', color);
	}

	function initCandidateColor(cname, color) {
		var items = $('#col_list').children('.colitem');
		var i;
		var cols = items.length;
		var selected = {};
		var cname;
		for(i = 0; i < cols; i++) {
			cname = $(items[i]).attr('data-cname');
			selected[cname] = 1;
		}

		var candidates = $('#col_candidates').children('.colitem');
		var cols = candidates.length;
		for(i = 0; i < cols; i++) {
			cname = $(candidates[i]).attr('data-cname');
			if(selected[cname] === 1) {
				$(candidates[i]).children('.col_div').css('background-color', '#ccc');
			}
		}
	}

    function drop(e) {
        if(e.stopPropagation) {
            e.stopPropagation();
        }

		clearDragImage();

        $(this).removeClass('dragon_bottom');
        $(this).removeClass('dragon_trashcan');
        $(this).removeClass('dragon');
        $('.dropzone').remove();

        if(this === drag_obj) {
            return false;
        }

        var target_id = $(this).attr('id');
        var parent_id = $(drag_obj).parent().attr('id');

		if(parent_id === 'col_candidates') {
			var cname = $(drag_obj).attr('data-cname');
			if(!cname.match(/^_/)) {
				var z = $('#col_list').children("[data-cname='" + cname + "']");
				if(z.length > 0) {
					var txt = $(drag_obj).text();
					alert_dlg('Alert',
						'[' + txt + '] is already exists in format list.');
            		return false;
				}
			}
		}

        if(target_id === 'trashcan') {
            if(parent_id === 'col_list') {
                $(drag_obj).remove();
				changeCandidateColor($(drag_obj).attr('data-cname'), '');
            }
            return false;
        }

        var new_item = $(drag_obj).clone().
            removeClass('dragitem').
            removeClass('dragon');
        new_item.on('dragstart', dragStart);
        new_item.on('dragend', dragEnd);
        new_item.on('dragover', dragOver);
        new_item.on('dragenter', dragEnter);
        new_item.on('dragleave', dragLeave);
        new_item.on('drop', drop);

		changeCandidateColor($(drag_obj).attr('data-cname'), '#ccc');

        if(parent_id === 'col_list') {
            $(drag_obj).remove();
        }

        if(target_id === 'drop_target_bottom') {
            $('#col_list').append(new_item);
        } else {
            $(this).before(new_item);
        }

        return false;
    }

	function onSubmitForm() {
		var form = $('#' + form_name);
		$('#col_list').children('li').each(function(i, e) {
			var cname = $(e).attr('data-cname');
			$('<input />').attr('type', 'hidden').
				attr('name', col_list_name).
				attr('value', cname).
				appendTo(form);	
		});
		return true;
	}

	function showPreview(result) {
		$('#preview_dlg > .message').html(result.html);

		$('#preview_user_group_id').on('change', onChangeUserGroup);

		$('#preview_dlg').modal( {
			closeHTML: "<a href='#' title='Close' class='modal-close'>x</a>",
			position: ["15%"],
			minWidth: 900,
			minHeight: 300,
			overlayId: 'confirm-overlay',
			containerId: 'confirm-container',
			onShow: function (dialog) { _adjust_confirm_height(dialog, 400); }
		} );
	}

	function preview(preview_user_group_id) {
		var col_list = [];

		$('#col_list').children('li').each(function(i, e) {
			var cname = $(e).attr('data-cname');
			col_list.push(cname);
		});

		console.log(col_list);

		var data = {
			project_id: project_id,
			object_type: object_type,
			format_name: format_name,
			list_type: list_type,
			preview_user_group_id: preview_user_group_id,
			func: 'preview_list_format',
			col_list: col_list
		};
		dlg_common.ajax_post(preview_url, data, showPreview,
			'onPreviewBtn');
	}

	function onChangeUserGroup(e) {
		var preview_user_group_id = $('#preview_user_group_id').val();
		preview(preview_user_group_id);
	}

	function onPreviewBtn() {
		preview('');
	};

	function escapeRegExp(string) {
		return string.replace(/[.*+?^=!:${}()|[\]\/\\]/g, '\\$&'); // $&はマッチした部分文字列全体を意味します
	}
	function doFilter() {
		var txt = $('#available_cols_filter').val();

		var items = $('#col_candidates').children('.colitem');
		var regexp = new RegExp(escapeRegExp(txt), 'i');

		for (i = 0; i < items.length; i++) {
			var item_txt = $(items[i]).text();
			if(txt === '' || item_txt.match(regexp)) {
				$(items[i]).show();
			} else {
				$(items[i]).hide();
			}
		}
	}

	function onKeydownFilter(e) {
		if(e.keyCode === 13) {
			doFilter();
			e.preventDefault();
		}
	}

	function init(pj_id, obj_type, fmt_name, frm_name, list_name, url,
		_list_type) {
		project_id = pj_id;
		object_type = obj_type;
		format_name = fmt_name;
		form_name = frm_name;
		col_list_name = list_name;
		preview_url = url;
		list_type = _list_type;

        $("body").on('dragover', bodyDragOver);

        $('#col_candidates li').on('dragstart', dragStart);
        $('#col_candidates li').on('dragend', dragEnd);

        $('#col_list li').on('dragstart', dragStart);
        $('#col_list li').on('dragend', dragEnd);
        $('#col_list li').on('dragenter', dragEnter);
        $('#col_list li').on('dragleave', dragLeave);
        $('#col_list li').on('dragover', dragOver);
        $('#col_list li').on('drop', drop);

        $('#drop_target_bottom').on('dragenter', dragEnter);
        $('#drop_target_bottom').on('dragleave', dragLeave);
        $('#drop_target_bottom').on('dragover', dragOver);
        $('#drop_target_bottom').on('drop', drop);

        $('#trashcan').on('dragenter', dragEnter);
        $('#trashcan').on('dragleave', dragLeave);
        $('#trashcan').on('dragover', dragOver);
        $('#trashcan').on('drop', drop);

		$('#' + form_name).on('submit', onSubmitForm);
		$('#preview_btn_div1').on('click', onPreviewBtn);

		$('#available_cols_filter').on('keydown', onKeydownFilter);

		initCandidateColor();
    }

	return {
		onSubmitForm: onSubmitForm,
		init: init
	};

};

var dlg_common = cms_dialog_common();
var g_sys_admin_col_list_dnd = sys_admin_col_list_dnd();


