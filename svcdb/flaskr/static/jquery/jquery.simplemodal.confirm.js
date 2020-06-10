/*
 * SimpleModal Confirm Modal Dialog
 * http://simplemodal.com
 *
 * Copyright (c) 2013 Eric Martin - http://ericmmartin.com
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 */

function _adjust_confirm_height(dialog) {
	var header_div = $('.header', dialog.data[0]);
	var msg_div = $('.message', dialog.data[0]);
	var btn_div = $('.buttons', dialog.data[0]);

	$(dialog.container[0]).height(
		header_div.outerHeight(true) +
		msg_div.outerHeight(true) +
		btn_div.outerHeight(true));
}

function confirm_2cb(message, yes_callback, cancel_callback) {
	$('#confirm').modal({
		closeHTML: "<a href='#' title='Close' class='modal-close'>x</a>",
		position: ["20%"],
		overlayId: 'confirm-overlay',
		containerId: 'confirm-container',

		onYes: function(dialog) {
			// close the dialog
			$.modal.close();
			// call the callback
			if ($.isFunction(yes_callback)) {
				yes_callback.apply();
			}
		},
		onCancel: function(dialog) {
			// close the dialog
			$.modal.close();
			// call the callback
			if ($.isFunction(cancel_callback)) {
				cancel_callback.apply();
			}
		},
		onClose: function (dialog) {
			$(document).unbind('keydown.confirm');
			var modal = this;
			modal.close();
		},
		onShow: function (dialog) {
			var modal = this;
			$('.message', dialog.data[0]).append(message);
			_adjust_confirm_height(dialog);

			// if the user clicks "yes"
			$('.yes', dialog.data[0]).click(modal.o.onYes);
			$('.no', dialog.data[0]).click(modal.o.onCancel);

			$(document).bind('keydown.confirm', function (e) {
				var KEY_Y = 89;
				var KEY_N = 78;
				if(e.keyCode === KEY_Y) modal.o.onYes();
				if(e.keyCode === KEY_N) modal.o.onCancel();
			});
		}
	});
}

function confirm_2cb_noclose(message, yes_callback, cancel_callback) {
	$('#confirm').modal({
		position: ["20%"],
		overlayId: 'confirm-overlay',
		containerId: 'confirm-container',

		onYes: function(dialog) {
			// close the dialog
			$.modal.close();
			// call the callback
			if ($.isFunction(yes_callback)) {
				yes_callback.apply();
			}
		},
		onCancel: function(dialog) {
			// close the dialog
			$.modal.close();
			// call the callback
			if ($.isFunction(cancel_callback)) {
				cancel_callback.apply();
			}
		},
		onShow: function (dialog) {
			var modal = this;
			$('.message', dialog.data[0]).append(message);
			_adjust_confirm_height(dialog);

			// if the user clicks "yes"
			$('.yes', dialog.data[0]).click(modal.o.onYes);
			$('.no', dialog.data[0]).click(modal.o.onCancel);

			$(document).bind('keydown.confirm', function (e) {
				var KEY_Y = 89;
				var KEY_N = 78;
				if(e.keyCode === KEY_Y) modal.o.onYes();
				if(e.keyCode === KEY_N) modal.o.onCancel();
			});
		}
	});
}

//function confirm(message, callback) {
//	confirm_2cb(message, callback, null);
//}

function alert_dlg(title, message) {
	$('#alert').modal({
		closeHTML: "<a href='#' title='Close' class='modal-close'>x</a>",
		position: ["20%"],
		overlayId: 'confirm-overlay',
		containerId: 'confirm-container',
		onShow: function (dialog) {
			var modal = this;
			$('.header > span', dialog.data[0]).text(title);
			$('.message', dialog.data[0]).append(message);
			_adjust_confirm_height(dialog);
		}
	});
}

