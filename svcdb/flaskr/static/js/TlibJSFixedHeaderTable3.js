/**
 TlibJSFixedHeaderTable3.js	Fixed the header of the table.

 Version: 3.10 (20170221)
  - Add TlibFixedColTableRight class for adjust layout of fixed column table.
  - Add TlibFixedColTableLeft class for change table sepalator color. 

 Version: 3.11 (20170406)
  - Add _adjust_right_table_tr_height parameter for fixed column table.
  - Do not add TlibFixedColTableRight when borderCollapse of table is collapse.

 Version: 3.12 (20170417)
  - Add _last_child_td_right_color parameter for fixed column table.

 Version: 3.13 (20170424)
  - Reduce reflow at initialize table.

 Version: 3.14 (20170425)
  - _initCSS() execute only once.
  - Remove resize window event listener after unload the table.

 Version: 3.15 (20170427)
  - Adjust column width of multi-line header.

 Version: 3.16 (20170818)
  - Tuning _adjustTableHeight(): Reduce reflow.
  - Remove _adjustScroll from init()

 Version: 3.17 (20171023)
  - Support colspan cell in data row

 Version: 3.18 (20171027)
  - Add _use_get_bounding_client_rect_on_ie11 option for adjusting cell
    width on IE11 exactly

 Version: 3.19 (20171212)
  - Comment out table.style.position = 'relative'; at init().
    Add CSS Rule position: relative; to .TlibFixedHeaderTable.

 Version: 3.20 (20180713)
  - Fix: does not work Ctrl+C when fixed column mode.

 Version: 3.21 (20180804)
  - Fix: _adjust_right_table_tr_height for header_div_top.

 Version: 3.22 (20181205)
  - Fix: add unnecessary ths when fixed column mode and header has rowspan.

 Version: 3.23 (20181224)
  - Allow set _header_rows at initialze code.

 Version: 3.24 (20190626)
  - Fix: invalid array index for ths[] at _createTableHeaderCol
  - Fix: header is broken when _header_rows setted

 Version: 3.25 (20190627)
  - Fix: header is broken when rowspan and colspan are used in the header.

 Version: 3.26 (20190701)
  - Fix: wrong width of header on chrome when zooming in.

 Version: 3.27 (20190706)
  - Fix: wrong height of left header with complex rowspan/colspan.

 Version: 3.28 (20190717)
  - Add _td_border_color option.
*/

var TlibHeaderFixedTable = function() { }

TlibHeaderFixedTable.prototype = {
	_header_rows: 0,
	_header_cols: 0,
	_table_div: 'TlibTable',
	_table_header_div: 'TlibFixedTableHeader',
	_table_header_div_col: '',
	_table_header_div_hd: '',
	_table_height: 0,
	_table_height_calc: '',
	_td_adjust: 0,
	_td_adjust_y: 0,
	_td_adjust_hd: 0,
	_td_adjust_hd_y: 3,
	_th_adjust_cospan: 9,	// padding-left + padding-right + border-right
	_browser: '',
	_no_resize_bind: '',
	_ie_backcompat_width: '97%',

	_tr_bg_color: '',
	_td_border_color: '#999999',

	_adjust_right_table_tr_height: false,
    _last_child_td_right_color: false,
	_clientHeight: 0,
	_uuid: '',
	_onResizeFunc: undefined,
	_use_get_bounding_client_rect_on_ie11: 0,
	_use_get_bounding_client_rect: 0,

	_generateUUID: function() {
		var d = new Date().getTime();
		if (typeof performance !== 'undefined' &&
			typeof performance.now === 'function'){
			d += performance.now();
		}
		return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,
			function (c) {
				var r = (d + Math.random() * 16) % 16 | 0;
				d = Math.floor(d / 16);
				return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
			}
		);
	},
	_setTop: function(e, t) {
		e.style.top = t + 'px';
	},
	_setLeft: function(e, t) {
		e.style.left = t + 'px';
	},
	_setHeight: function(e, t) {
		if(t < 0) return;
		e.style.height = t + 'px';
	},
	_setWidth: function(e, t) {
		if(t < 0) return;
		e.style.width = t + 'px';
	},
	_getBrowser: function() {
		var userAgent = window.navigator.userAgent.toLowerCase();

		if (userAgent.indexOf('opera') != -1) {
			return 'opera';
		} else if (userAgent.indexOf('msie') != -1) {
			return 'ie';
		} else if (userAgent.indexOf('trident/7.0') != -1) {
			return 'ie11';	//IE11
		} else if (userAgent.indexOf('chrome') != -1) {
			return 'chrome';
		} else if (userAgent.indexOf('safari') != -1) {
			return 'safari';
		} else if (userAgent.indexOf('gecko') != -1) {
			return 'gecko';
		} else {
			return false;
		}
	},
	_isIE6: function() {
		if (typeof document.documentElement.style.maxHeight != "undefined") {
			return false;
		} else {
			return true;
		}
	},
	_elem: function(id) {
		if(document.all) return document.all(id);
		return document.getElementById(id);
	},
	_calc_header_rows: function() {
		var table_div = this._elem(this._table_div);
		var table = table_div.getElementsByTagName('TABLE')[0];
		var table_trs = table.getElementsByTagName('TR');

		if(this._header_rows > 0) {
			if(this._header_rows === table_trs.length) return false;
			return true;
		}

		this._header_rows = 0;
		var r = 0;
		for(this._header_rows = 0; r < table_trs.length; r++, this._header_rows++) {
			ths = table_trs[r].getElementsByTagName('TH');
			if(ths.length === 0) break;
		}

		if(this._header_rows === table_trs.length) return false;
		return true;
	},
	_createTableHeader: function() {
		var table_div = this._elem(this._table_div);
		table_div.className = 'TlibFixedHeaderTableDiv';

		var table = table_div.getElementsByTagName('TABLE')[0];
		var table_style = table.style;
		var org_class_name = table.className || '';
		table.className = org_class_name + ' TlibFixedHeaderTable';
		table_style.width = '100%';
		var table_trs = table.getElementsByTagName('TR');

		var header_df = document.createDocumentFragment();

		var header_div = document.createElement('div');
		header_div.id = this._table_header_div;
		header_div.className = 'TlibFixedHeaderTableDivTop';
		header_div.style.zIndex = 110;
		header_df.appendChild(header_div);

		var header_table = document.createElement('table');
		var header_table_style = header_table.style;
		header_table.className = table.className;
		header_table_style.width = '100%';
		header_div.appendChild(header_table);

		if(this._browser === 'ie' && document.compatMode !== 'BackCompat'
			&& document.documentMode === 7) {
			// When document mode is IE7, the h-scroll bar being always
			// displayed at table width = 100%.
			table_style.width = this._ie_backcompat_width;
			header_table_style.width = this._ie_backcompat_width;
		}

		var thead = document.createElement('thead');
		header_table.appendChild(thead);

		var r, c, tr, ths, th, fht_cell;
		var temp_tr = document.createElement('tr');
		var temp_div = document.createElement('div');
		for(r = 0; r < this._header_rows; r++) {
			tr = temp_tr.cloneNode(false);
			tr.style.height = table_trs[r].style.height;
			thead.appendChild(tr);

			ths = table_trs[r].getElementsByTagName('TH');

			for(c = 0; c < ths.length; c++) {
				th = ths[c].cloneNode(true);
				// when _header_rows >= 2 rows, fixes the column width by div.
				if(this._header_rows > 1) {
					fht_cell = temp_div.cloneNode(false);
					th.appendChild(fht_cell);
				}
				tr.appendChild(th);
			}
		}

		header_table_style.tableLayout = 'fixed';

		table_div.parentNode.insertBefore(header_df, table_div);
	},
	_createTableHeaderCol: function() {
		if(this._header_cols === 0) return;

		this._table_header_div_col = this._table_header_div + '_COL';
		this._table_header_div_hd = this._table_header_div + '_HD';

		var table_div = this._elem(this._table_div);
		var table = table_div.getElementsByTagName('TABLE')[0];
		var table_trs = table.getElementsByTagName('TR');
		var header_div = this._elem(this._table_header_div);
		var header_table = header_div.getElementsByTagName('TABLE')[0];
		var header_trs = header_table.getElementsByTagName('TR');

		var header_df_col = document.createDocumentFragment();
		var header_df_hd = document.createDocumentFragment();

		var header_div_col = document.createElement('div');
		var header_div_col_style = header_div_col.style;
		header_div_col.id = this._table_header_div_col;
		header_div_col.className = 'TlibFixedHeaderTableDivCol';
		header_div_col_style.position = 'absolute';
		header_div_col_style.zIndex = 111;
		header_df_col.appendChild(header_div_col);

		var header_div_hd = document.createElement('div');
		var header_div_hd_style = header_div_hd.style;
		header_div_hd.id = this._table_header_div_hd;
		header_div_hd.className = 'TlibFixedHeaderTableDivCol';
		header_div_hd_style.position = 'absolute';
		header_div_hd_style.zIndex = 112;
		header_df_hd.appendChild(header_div_hd);

		var header_table_col = document.createElement('table');
		var header_table_col_style = header_table_col.style;
		header_table_col.className = table.className;
		header_table_col_style.position = 'relative';
		header_div_col.appendChild(header_table_col);
		var thead = document.createElement('thead');
		header_table_col.appendChild(thead);
		var tbody = document.createElement('tbody');
		header_table_col.appendChild(tbody);

		var header_table_hd = document.createElement('table');
		var header_table_hd_style = header_table_hd.style;
		header_table_hd.className = table.className;
		header_table_hd_style.position = 'relative';
		header_div_hd.appendChild(header_table_hd);
		var thead_hd = document.createElement('thead');
		header_table_hd.appendChild(thead_hd);

		var r, c, tr, tr_hd, ths, row_span, th, th_hd, height_col, tds, td, col_idx, col_span;
		var header_rows = this._header_rows;
		var header_cols = this._header_cols;
		var rowspan_arr = [];
		var rowspan_arr_c = [];
		var temp_tr = document.createElement('tr');
		for(r = 0; r < header_rows; r++) {
			tr = temp_tr.cloneNode(false);
			thead.appendChild(tr);

			tr_hd = temp_tr.cloneNode(false);
			thead_hd.appendChild(tr_hd);

			ths = table_trs[r].getElementsByTagName('TH');

			col_idx = 0;
			copy_th_idx = 0;
			for(c = 0; c < header_cols; c++) {
				col_span = ths[copy_th_idx].colSpan;
				row_span = ths[copy_th_idx].rowSpan;

				if(r === 0){
					rowspan_arr[c] = row_span;
					rowspan_arr_c[c] = col_span;
				} else {
					if(rowspan_arr[c] <= r) {
						rowspan_arr[c] = row_span + r;
						rowspan_arr_c[c] = col_span;
					} else {
						col_idx = col_idx + rowspan_arr_c[c];
						if(col_idx >= header_cols) { break; }
						continue;
					}
				}

				th = ths[copy_th_idx].cloneNode(true);
				tr.appendChild(th);

				th_hd = ths[copy_th_idx].cloneNode(true);
				tr_hd.appendChild(th_hd);

				copy_th_idx++;
				col_idx = col_idx + col_span;
				if(col_idx >= header_cols) { break; }
			}
		}

		var start_r = r;
		var copy_td_idx = 0;
		for(; r < table_trs.length; r++) {
			tr = temp_tr.cloneNode(false);
			tbody.appendChild(tr);

			if(table_trs[r].id) tr.id = table_trs[r].id + '_col';
			if(table_trs[r].title) tr.title = table_trs[r].title;
			tr.className = table_trs[r].className;

			tds = table_trs[r].getElementsByTagName('TD');

			col_idx = 0;
			copy_td_idx = 0;
			for(c = 0; c < header_cols; c++) {
				if(tds[c] === undefined) break;
				col_span = tds[copy_td_idx].colSpan;
				row_span = tds[copy_td_idx].rowSpan;

				if(r === start_r){
					rowspan_arr[c] = row_span + start_r;
					rowspan_arr_c[c] = col_span;
				} else {
					if(rowspan_arr[c] <= r) {
						rowspan_arr[c] = row_span + r;
						rowspan_arr_c[c] = col_span;
					} else {
						col_idx = col_idx + rowspan_arr_c[c];
						if(col_idx >= header_cols) { break; }
						continue;
					}
				}

				td = tds[copy_td_idx].cloneNode(true);
				tr.appendChild(td);

				copy_td_idx++;
				col_idx = col_idx + col_span;
				if(col_idx >= header_cols) { break; }
			}
		}

		header_table_col_style.tableLayout = 'fixed';
		header_table_hd_style.tableLayout = 'fixed';

		var borderCollapse = (table.currentStyle ||
			document.defaultView.getComputedStyle(table, '')).borderCollapse;
		if(borderCollapse !== 'collapse') {
			this._addClass(table, 'TlibFixedColTableRight');
			this._addClass(header_table, 'TlibFixedColTableRight');
		}
		this._addClass(header_table_col, 'TlibFixedColTableLeft');
		this._addClass(header_table_hd, 'TlibFixedColTableLeft');

		table_div.parentNode.insertBefore(header_df_col, table_div);
		table_div.parentNode.insertBefore(header_df_hd, header_div);
	},
	_adjustTableWidth: function() {
		var table_div = this._elem(this._table_div);
		var table = table_div.getElementsByTagName('TABLE')[0];
		var table_trs = table.getElementsByTagName('TR');

		var header_div = this._elem(this._table_header_div);
		var header_table = header_div.getElementsByTagName('TABLE')[0];
		var header_trs = header_table.getElementsByTagName('TR');

		var header_rows = this._header_rows;
		var header_cols = this._header_cols;
		var r, c;
		var row_w_arr = [];
		var width_arr = [];
		var header_ths, table_ths, cols, th, col_span;

		for(r = 0; r < header_rows; r++) {
			table_ths = table_trs[r].getElementsByTagName('TH');
			cols = table_ths.length;
			width_arr = [];

			if(this._use_get_bounding_client_rect ||
				(this._use_get_bounding_client_rect_on_ie11 && this._browser === 'ie11')) {
				for(c = 0; c < cols; c++) {
					width_arr[c] = table_ths[c].getBoundingClientRect().width -
						this._td_adjust_hd;
				}
			} else {
				for(c = 0; c < cols; c++) {
					width_arr[c] = table_ths[c].offsetWidth -
						this._td_adjust_hd;
				}
			}
			row_w_arr[r] = width_arr;
		}

		for(r = 0; r < header_rows; r++) {
			header_ths = header_trs[r].getElementsByTagName('TH');
			cols = header_ths.length;
			width_arr = row_w_arr[r];

			for(c = 0; c < cols; c++) {
				th = header_ths[c];
				col_span = th.colSpan;
				if(col_span > 1) {
					this._setWidth(th, width_arr[c] - (col_span - 1) * 2);
				} else {
					this._setWidth(th, width_arr[c]);
				}
			}
		}

		if(this._header_cols > 0) {
			var header_div_col = this._elem(this._table_header_div_col);
			var header_table_col = header_div_col.getElementsByTagName('TABLE')[0];
			var header_trs_col = header_table_col.getElementsByTagName('TR');

			var header_div_hd = this._elem(this._table_header_div_hd);
			var header_table_hd = header_div_hd.getElementsByTagName('TABLE')[0];
			var header_trs_hd = header_table_hd.getElementsByTagName('TR');

			var ths_col, ths_hd;
			var width_tbl = 0;
			for(r = 0; r < header_rows; r++) {
				ths_col = header_trs_col[r].getElementsByTagName('TH');
				ths_hd = header_trs_hd[r].getElementsByTagName('TH');
				if(ths_hd.length === 0)  continue;
				width_arr = row_w_arr[r];

				cols = ths_col.length;

				for(c = 0; c < cols; c++) {
					if(r === 0) width_tbl += width_arr[c];
					this._setWidth(ths_col[c], width_arr[c]);
					this._setWidth(ths_hd[c], width_arr[c]);
				}
			}
			this._setWidth(header_table_col, width_tbl + 1);
			this._setWidth(header_table_hd, width_tbl + 1);
		}

		if(this._browser === 'gecko') {
			header_div.style.overflowY = 'hidden';
			this._setWidth(header_div, table_div.clientWidth);
		}
	},
	_adjustTableHeight: function() {
		var table_div = this._elem(this._table_div);
		var table = table_div.getElementsByTagName('TABLE')[0];
		var table_trs = table.getElementsByTagName('TR');

		var header_div = this._elem(this._table_header_div);
		var header_table = header_div.getElementsByTagName('TABLE')[0];
		var header_trs = header_table.getElementsByTagName('TR');

		var header_rows = this._header_rows;
		var header_cols = this._header_cols;
		var table_length = table_trs.length;
		var trs_height_arr = [];
		var r;
		var header_div_col, header_table_col;
		var clientHeight;
		var table_div_top;
		var h_scr_height = 0;

		var header_div_height = header_table.offsetHeight;
		var table_top = -table_trs[header_rows].offsetTop;

		if(header_cols > 0) {
			// Reduce reflow at setHeight for header_div_col.
			h_scr_height = table_div.offsetHeight - table_div.clientHeight;
		}

		if(this._browser === 'ie' || this._browser === 'ie11') {
			clientHeight = document.documentElement.clientHeight ||
						   document.body.clientHeight;
		} else {
			clientHeight = window.innerHeight;
		}
		table_div_top = table_div.offsetTop;

		if(header_cols > 0) {
			for(r = 0; r < table_length; r++) {
				trs_height_arr[r] = table_trs[r].offsetHeight;
			}

			var header_div_top = this._elem(this._table_header_div);
			var header_table_top = header_div_top.getElementsByTagName('TABLE')[0];
			var header_trs_top = header_table_top.getElementsByTagName('TR');

			header_div_col = this._elem(this._table_header_div_col);
			header_table_col = header_div_col.getElementsByTagName('TABLE')[0];
			var header_trs_col = header_table_col.getElementsByTagName('TR');

			var header_div_hd = this._elem(this._table_header_div_hd);
			var header_table_hd = header_div_hd.getElementsByTagName('TABLE')[0];
			var header_trs_hd = header_table_hd.getElementsByTagName('TR');

			var height_col;

			for(r = 0; r < table_length; r++) {
				height_col = trs_height_arr[r];

				if(r < header_rows) {
					this._setHeight(header_trs_hd[r], height_col);
					this._setHeight(header_trs_top[r], height_col);
				}
				this._setHeight(header_trs_col[r], height_col);

				if(this._adjust_right_table_tr_height) {
					this._setHeight(table_trs[r], height_col);
				}
			}
		}

		this._setHeight(header_div, header_div_height);
		this._setTop(table, table_top);

		var table_div_height;
		if(this._table_height === -1) {
			table_div_height = table_div.parentNode.offsetHeight -
				table_div.offsetTop;
		} else if(this._table_height > 0) {
			table_div_height = this._table_height;
		} else {
			if(this._browser === 'ie' || this._browser === 'ie11') {
				table_div_height = clientHeight - table_div_top - 2;
			} else {
				table_div_height = clientHeight - table_div_top - 15;
			}
		}
		this._setHeight(table_div, table_div_height);

		if(header_cols > 0) {
			this._setTop(header_table_col, table_top);
			// set header_div_col.offsetHeight to table_div.clientHeight
			this._setHeight(header_div_col, table_div_height - h_scr_height);
		}
	},
	_adjustTableSize: function() {
		if(this._header_rows <= 0) return;

		var table_div = this._elem(this._table_div);
		if(!table_div) return;
		var table = table_div.getElementsByTagName('TABLE')[0];
		var table_trs = table.getElementsByTagName('TR');
		var header_div = this._elem(this._table_header_div);
		if(!header_div) return;

		if(table_trs.length <= this._header_rows) return;

		this._adjustTableWidth();
		this._adjustTableHeight();
	},
	adjustTableSize: function() {
		this._adjustTableSize();
	},
	_onResizeWindow: function() {
		// check uuid
		var table_div = this._elem(this._table_div);
		if(table_div && this._uuid !== table_div.getAttribute('uuid')) {
			// remove event listener
			if(this._onResizeFunc) {
				if(window.addEventListener) {
					window.removeEventListener('resize', this._onResizeFunc,
						false);
				} else {
					window.detachEvent('onresize', this._onResizeFunc);
				}
			}
			this._onResizeFunc = undefined;
			return;
		}

		this.adjustTableSize();
		this._adjustScroll();
	},
	_initScroll: function() {
		// do nothing...
	},
	_adjustScroll: function() {
		var header_div = this._elem(this._table_header_div);
		if(!header_div) return;

		var table_div = this._elem(this._table_div);
		header_div.scrollLeft = table_div.scrollLeft;

		if(this._header_cols > 0) {
			var header_div_col = this._elem(this._table_header_div_col);
			header_div_col.scrollTop = table_div.scrollTop;
		}
	},
	_onScrollTable: function() {
		this._adjustScroll();
	},
	_hasClass: function(ele, cls) {
		return ele.className.match(new RegExp('(\\s|^)' + cls + '(\\s|$)'));
	},
	_addClass: function(ele, cls) {
		if(!this._hasClass(ele,cls)) {
			var eleClassName = ele.className || '';
			if(eleClassName !== "") eleClassName += " ";
			eleClassName += cls;
			ele.className = eleClassName;
		}
	},
	_removeClass: function(ele, cls) {
		if(this._hasClass(ele, cls)) {
			var reg = new RegExp('(\\s|^)' + cls + '(\\s|$)');
			ele.className=ele.className.replace(reg,' ').replace(/^\s/, '');
		}
	},
	_onMouseOver: function(src_tr, table_flg) {
		var table_div = this._elem(this._table_div);
		var head_div_col = this._elem(this._table_header_div_col);

		var table = table_div.getElementsByTagName('TABLE')[0];
		var thead = table.getElementsByTagName('THEAD');
		var head_table_col = head_div_col.getElementsByTagName('TABLE')[0];

		var r, dest_table_trs;
		if(table_flg === 1 && thead.length === 0) {
			r = src_tr.sectionRowIndex;
		} else {
			r = this._header_rows + src_tr.sectionRowIndex;
		}
		if(r < this._header_rows) return;
		if(table_flg === 1) {
			dest_table_trs = head_table_col.getElementsByTagName('TR');
		} else {
			dest_table_trs = table.getElementsByTagName('TR');
		}

		var dest_tr = dest_table_trs[r];
		this._addClass(dest_tr, 'TlibFixedHeaderTableHover');
		this._addClass(src_tr, 'TlibFixedHeaderTableHover');
	},
	_onMouseOut: function(src_tr, table_flg) {
		var table_div = this._elem(this._table_div);
		var head_div_col = this._elem(this._table_header_div_col);

		var table = table_div.getElementsByTagName('TABLE')[0];
		var thead = table.getElementsByTagName('THEAD');
		var head_table_col = head_div_col.getElementsByTagName('TABLE')[0];

		var r, dest_table_trs;
		if(table_flg === 1 && thead.length === 0) {
			r = src_tr.sectionRowIndex;
		} else {
			r = this._header_rows + src_tr.sectionRowIndex;
		}
		if(r < this._header_rows) return;
		if(table_flg === 1) {
			dest_table_trs = head_table_col.getElementsByTagName('TR');
		} else {
			dest_table_trs = table.getElementsByTagName('TR');
		}

		var dest_tr = dest_table_trs[r];
		this._removeClass(dest_tr, 'TlibFixedHeaderTableHover');
		this._removeClass(src_tr, 'TlibFixedHeaderTableHover');
	},
	_onHoverTable: function() {
		var obj = this;
		var table_div = this._elem(this._table_div);
		var table = table_div.getElementsByTagName('TABLE')[0];
		var table_trs = table.getElementsByTagName('TR');

		var header_div_col = this._elem(this._table_header_div_col);
		var header_table_col = header_div_col.getElementsByTagName('TABLE')[0];
		var header_trs_col = header_table_col.getElementsByTagName('TR');
		var r, table_tr, header_tr_col;
		var header_trs_length = header_trs_col.length;
		for(r = this._header_rows; r < header_trs_length; r++) {
			header_tr_col = header_trs_col[r];
			table_tr = table_trs[r];
			if(window.addEventListener) {
				table_tr.addEventListener('mouseover',
					function() { obj._onMouseOver(this, 1); }, false);
				header_tr_col.addEventListener('mouseover',
					function() { obj._onMouseOver(this, 2); }, false);
				table_tr.addEventListener('mouseout',
					function() { obj._onMouseOut(this, 1); }, false);
				header_tr_col.addEventListener('mouseout',
					function() { obj._onMouseOut(this, 2); }, false);
			} else {
				table_tr.onmouseover = function() { obj._onMouseOver(this, 1); }
				header_tr_col.onmouseover = function() { obj._onMouseOver(this, 2); }
				table_tr.onmouseout = function() { obj._onMouseOut(this, 1); }
				header_tr_col.onmouseout = function() { obj._onMouseOut(this, 2); }
			}
		}
	},
	_onWheelFixedCol: function(e) {
		var delta = 0;
		if(e.wheelDelta) {
			// for IE / Chrome
			delta = e.wheelDelta / 2;
		} else {
			// for Firefox
			if(e.deltaMode === 1) {
				delta = - (e.deltaY * 20);
			}
		}
		e.preventDefault();
		if(delta !== 0) {
			var table_div = this._elem(this._table_div);
			table_div.scrollTop = table_div.scrollTop - delta;
			this._adjustScroll();
		}
	},
        _onKeydownFixedCol: function(e) {
            var r, delta = 0;
            var header_div_col = this._elem(this._table_header_div_col);
            var header_table_col = header_div_col.getElementsByTagName('TABLE')[0];
            var header_trs_col = header_table_col.getElementsByTagName('TR');
            var tr_length = header_trs_col.length < this._header_rows + 3 ? header_trs_col.length : this._header_rows + 3;
            // the height of the front 3 rows.
            var rowDelta = 0;
            for(r = this._header_rows; r < tr_length; r++) {
                rowDelta += header_trs_col[r].offsetHeight - 2;
            }
            var pageDelta = header_div_col.offsetHeight - rowDelta;
            switch (e.which) {
                // PageUp
                case 33 :
                    delta = pageDelta ;
                    break;
                // PageDown
                case 34 :
                    delta = -pageDelta;
                    break;
                // Up Allow
                case 38 :
                    delta = rowDelta;
                    break;
                // Down Allow
                case 40 :
                    delta = -rowDelta;
                    break;
            }
            if(delta !== 0) {
                e.preventDefault();
                var table_div = this._elem(this._table_div);
                table_div.scrollTop = table_div.scrollTop - delta;
                this._adjustScroll();
            }
            return false;
        },
	_addCSSRule: function(sheet, selector, declaration) {
		if(sheet.insertRule) {
			sheet.insertRule(selector + '{' + declaration + '}',
				sheet.cssRules.length);
		} else if(sheet.addRule) {
			sheet.addRule(selector, declaration);
		}
	},
	_bindEvent: function() {
		var obj = this;
		var table_div = this._elem(this._table_div);

		if(!this._no_resize_bind) {
			this._onResizeFunc = function() { obj._onResizeWindow(); };
			if(window.addEventListener) {
				window.addEventListener('resize', this._onResizeFunc, false);
			} else {
				window.attachEvent('onresize', this._onResizeFunc);
			}
		}
		if(window.addEventListener) {
			table_div.addEventListener('scroll',
				function() { obj._onScrollTable(); }, false);
		} else {
			table_div.onscroll = function() { obj._onScrollTable(); }
		}
		if(this._tr_bg_color.length > 0 && this._header_cols > 0) {
			obj._onHoverTable();
		}

		// support scroll by mouse wheel event on fixed col table
		if(this._header_cols > 0) {
			var header_div_col = this._elem(this._table_header_div_col);
			var mousewheelevent = 'onwheel' in document ?
				'wheel' : 'onmousewheel' in document ?
					'mousewheel' : 'DOMMouseScroll';
			header_div_col.addEventListener (mousewheelevent,
				function(e) { obj._onWheelFixedCol(e); }, false);
                        table_div.tabIndex = '112';
                        table_div.addEventListener ('keydown',
                                function(e) { obj._onKeydownFixedCol(e); }, false);
                        header_div_col.tabIndex = '111';
                        header_div_col.addEventListener ('keydown',
                                function(e) { obj._onKeydownFixedCol(e); }, false);
		}
	},
	_initCSS: function() {
		var css_id = "TlibFixedHeaderTable3_CSS";
		var css_elem = this._elem(css_id);
		if(css_elem) { return; }

		var style = document.createElement('style');
		style.setAttribute('type', 'text/css');
		style.setAttribute("id", css_id);

		document.getElementsByTagName('head')[0].appendChild(style);
		var sheet = document.styleSheets[document.styleSheets.length - 1];

		var tableStyle = '';
		var tableTdStyle = 'padding: 1px 3px;';
		if(this._header_cols > 0) {
			tableStyle = 'line-height: 1 !important;';
			tableTdStyle = 'padding-left: 3px; padding-right: 3px; padding-top: 4px !important; padding-bottom: 4px !important;';
		}

		this._addCSSRule(sheet, '.TlibFixedHeaderTableDiv',
			'position: relative; width: 100%; height: 80%; overflow-x: auto; overflow-y: scroll; ');

		this._addCSSRule(sheet, '.TlibFixedHeaderTableDivTop',
			'position: relative; width: 100%; overflow-x: hidden; overflow-y: scroll; scrollbar-face-color: white; scrollbar-shadow-color: white; scrollbar-darkshadow-color: white; scrollbar-3dlight-color: white; scrollbar-arrow-color: white; ');

		this._addCSSRule(sheet, '.TlibFixedHeaderTableDivCol',
			'position: relative; overflow-x: hidden; overflow-y: hidden; ');

		this._addCSSRule(sheet, '.TlibFixedHeaderTable',
			'position: relative; margin: 0; padding: 0; border: 1px #444444 solid; background: #ffffff; width: auto; height: auto; ' + tableStyle);

		this._addCSSRule(sheet, '.TlibFixedHeaderTable th',
			'padding-top: 1px; padding-left: 3px; padding-right: 3px; padding-bottom: 2px; ');

		this._addCSSRule(sheet, '.TlibFixedHeaderTable td',
			tableTdStyle + ' border-bottom: 1px solid ' + this._td_border_color + '; ');

		this._addCSSRule(sheet, '.TlibFixedHeaderTable td.last',
			'border-bottom: 3px double #666666; ');

		this._addCSSRule(sheet, '.TlibFixedHeaderTableDivTop *',
			'-webkit-box-sizing: border-box; -moz-box-sizing: border-box; -o-box-sizing: border-box; -ms-box-sizing: border-box; box-sizing:border-box; ');

		this._addCSSRule(sheet, '.TlibFixedHeaderTableDivCol *',
			'-webkit-box-sizing: border-box; -moz-box-sizing: border-box; -o-box-sizing: border-box; -ms-box-sizing: border-box; box-sizing:border-box; ');

		this._addCSSRule(sheet, '.TlibFixedColTableRight',
			'position: relative; left: 3px;');
		this._addCSSRule(sheet, '.TlibFixedColTableLeft',
			'border-right: 1px solid #999');

		if(this._last_child_td_right_color) {
			this._addCSSRule(sheet,
				'.TlibFixedHeaderTableDivCol > table td:last-child',
				'border-right: 1px solid ' + this._last_child_td_right_color);
		}

		if(this._tr_bg_color.length > 0) {
			this._addCSSRule(sheet, '.TlibFixedHeaderTableHover', 'background-color: ' + this._tr_bg_color + ' !important; ');
		}
	},
	init: function() {
		if(!this._calc_header_rows()) return;

		this._initCSS();

		this._browser = this._getBrowser();
		if(this._browser === 'ie') {
			if(document.compatMode === 'BackCompat') {
				this._td_adjust = 0;
				this._td_adjust_y = 0;
				this._td_adjust_hd = 0;
				this._td_adjust_hd_y = 0;
			} else {
				this._td_adjust = 6;
				if(this._isIE6()) {
					this._td_adjust_hd = 6;
				}
				//this._td_adjust_y = 3;
				//this._td_adjust_hd = 6;
				//this._td_adjust_hd_y = 3;
			}
		} else if(this._browser === 'gecko') {
			this._td_adjust = 6;
			//this._td_adjust_hd = 6;
			if(document.compatMode === 'BackCompat') {
				this._td_adjust_y = 3;
				this._td_adjust_hd_y = 0;
			} else {
				//this._td_adjust_y = 3;
				this._td_adjust_hd_y = 3;
			}
		} else if(this._browser === 'chrome') {
			this._td_adjust = 6;
			//this._td_adjust_hd = 6;
			if(this._use_get_bounding_client_rect) {
				this._td_adjust_hd = -0.5;
			}
			if(document.compatMode === 'BackCompat') {
				this._td_adjust_y = 0;
				this._td_adjust_hd_y = 0;
			} else {
				//this._td_adjust_y = 3;
				//this._td_adjust_hd_y = 3;
			}
		} else if(this._browser === 'safari') {
			this._td_adjust = 6;
			//this._td_adjust_hd = 6;
			if(document.compatMode === 'BackCompat') {
				this._td_adjust_y = 0;
				this._td_adjust_hd_y = 0;
			} else {
				//this._td_adjust_y = 3;
				//this._td_adjust_hd_y = 3;
			}
		} else if(this._browser === 'ie11') {
			if(document.compatMode === 'BackCompat') {
				this._td_adjust = 0;
				this._td_adjust_y = 0;
				this._td_adjust_hd = 0;
				this._td_adjust_hd_y = 0;
			} else {
				//this._td_adjust = 6;
				//this._td_adjust_y = 3;
				//this._td_adjust_hd = 6;
				//this._td_adjust_hd_y = 3;
			}
		}

		var table_div = this._elem(this._table_div);
		// set uuid for remove global events (onResizeWindow)
		this._uuid = this._generateUUID();
		table_div.setAttribute('uuid', this._uuid);

		var table = table_div.getElementsByTagName('TABLE')[0];

		this._createTableHeader();
		this._createTableHeaderCol();
		//table.style.position = 'relative';

		this._adjustTableSize();
		this._initScroll();

		this._bindEvent();
	},
	scrollTo: function(id) {
		var e = fixed_table._elem(id);
		if(!e) return;

		var table_div = this._elem(this._table_div);
		var table = table_div.getElementsByTagName('TABLE')[0];
		var table_trs = table.getElementsByTagName('TR');

		var y = e.offsetTop - table_trs[this._header_rows].offsetTop;
		table_div.scrollTop = y;
		this._adjustScroll();
	}
}