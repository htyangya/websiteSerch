
var TlibTableFilter = function() { }

TlibTableFilter.prototype = {
	_first_search_flg: 0,
	_timer: 0,
	_table_src: 0,

	_adjust_rowspan: function(rowspan_tr, span_rows) {
		if(!rowspan_tr) return;

		if(span_rows == 0) {
			$(rowspan_tr).remove();
		} else {
			$('td:nth-child(1)', rowspan_tr).attr('rowSpan', span_rows + 1);
		}
	},

	_do_filter: function(tbl, txt) {
		if(!this._first_search_flg) {
			var th = $('th', tbl);
			for(i = 0; i < th.length; i++) {
				$(th[i]).width($(th[i]).width());
			}
			this._table_src = tbl.html();
			this._first_search_flg = 1;
		}

		if(txt.length == 0) {
			tbl.html(this._table_src);
			return;
		}

		tbl.hide();
		tbl.html(this._table_src);
		var txt = txt.toUpperCase();

		var tr = $('tr', tbl);
		var rowspan_tr = null;
		var span_rows = 0;
		var i, j;

		for(i = 0; i < tr.length; i++) {
			if($('td:nth-child(2)', tr[i]).hasClass("blank_row")) {
				$(tr[i]).highlight(txt);
				this._adjust_rowspan(rowspan_tr, span_rows);

				rowspan_tr = tr[i];
				span_rows = 0;

				var d = $('td:nth-child(1)', tr[i]).text().toUpperCase();
				if(txt.length > 0 && d.indexOf(txt) != -1) {
					for(j = 0, i++; i < tr.length; j++, i++) {
						if($('td:nth-child(2)', tr[i]).hasClass("blank_row")) {
							i--;
							break;
						}
						$(tr[i]).highlight(txt);
						span_rows++;
					}
				}
				continue;
			}

			var td = $('td', tr[i]);
			if(td.length == 0) continue;

			for(j = 0; j < td.length; j++) {
				if(txt.length == 0) break;
				var d = $(td[j]).text().toUpperCase();
				if(d.indexOf(txt) != -1) break;
			}
			if(j == td.length) {
				$(tr[i]).remove();
			} else {
				$(tr[i]).highlight(txt);
				span_rows++;
			}
		}
		this._adjust_rowspan(rowspan_tr, span_rows);
		tbl.show();
	},

	init: function(table_id, search_id) {
		var obj = this;

		$('#' + search_id).keyup(function() {
			if(obj._gtfj_timer) clearTimeout(obj._gtfj_timer);
			tlib_gtfj_timer = setTimeout(
				function() {
					obj._do_filter($('#' + table_id), $('#' + search_id).val());
				},
				250);
        });
	}
}


