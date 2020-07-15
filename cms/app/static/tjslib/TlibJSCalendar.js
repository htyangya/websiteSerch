//
// Tlib Calendar.js
//
// Ver.1.01

var TlibJSCalendar = function() { }

TlibJSCalendar.prototype = {
	date_format: 'DD/Mon/YYYY',
	header_format: 'Mon YYYY',
	top_div_name: false,
	no_adjust_top_pos: false,
	date_changed: false,
	cal_div_name: 'TlibJSCalendarInternalDiv',
	cal_shim_name: 'TlibJSCalendarShim',
	cal_bk_layer_name: 'TlibJSCalendarBkLayer',

	_dayOfWeek: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
	_month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 
			'Oct', 'Nov', 'Dec'],

	_events: false,
	_global_events: false,

	_date_cache: false,
	_table_header_cache: false,
	_btn_cache: false,
	_blank_td_cache: false,
	_blank_td_idx: 0,

	_createBlankTdCache: function(parent) {
		if(this._blank_td_cache) return true;
		this._blank_td_cache = [];

		for (var i = 0; i < 20; i++) {
			var td = document.createElement('td');
			if(!td) return false;

			td.className = 'TlibJSCalendarNull';
			td.appendChild(document.createTextNode('.'));

			this._blank_td_cache[i] = td;
		}
		return true;
	},

	_makeBtn: function(cls, id, txt, func) {
		var btn = document.createElement('div');
		if(!btn) return null;

		btn.className = cls;
		btn.setAttribute('id', id);
		btn.appendChild(document.createTextNode(txt));
		this._addEvent(btn, 'mousedown', func, 1);
		this._setHover(btn, 1);
		return btn;
	},

	_createBtnCache: function(parent) {
		if(this._btn_cache) return true;
		this._btn_cache = [];

		var obj = this;
		this._btn_cache[0] = this._makeBtn('TlibJSCalendarBtn', 
			'TlibJSCalendarPrevYear', '<<', function() { obj._prevYear(); });
		this._btn_cache[1] = this._makeBtn('TlibJSCalendarBtn', 
			'TlibJSCalendarPrevMonth', '<', function() { obj._prevMonth(); });
		this._btn_cache[2] = this._makeBtn('TlibJSCalendarBtn', 
			'TlibJSCalendarNextMonth', '>', function() { obj._nextMonth(); });
		this._btn_cache[3] = this._makeBtn('TlibJSCalendarBtn', 
			'TlibJSCalendarNextYear', '>>', function() { obj._nextYear(); });

		for (var i = 0; i < 4; i++) {
			if(!this._btn_cache[i]) return false;
		}
		return true;
	},

	_createTableHeaderCache: function() {
		if(this._table_header_cache) return true;

		var tr = document.createElement('tr');
		if(!tr) return false;
		for(i = 0; i < this._dayOfWeek.length; i++) {
			th = document.createElement('th');
			if(!th) return false;
			th.appendChild(document.createTextNode(this._dayOfWeek[i]));
			tr.appendChild(th);
		}

		this._table_header_cache = tr;
		return true;
	},

	_setDateEvent: function(td, date) {
		var obj = this;
		if(this._getBrowser() === 'BlackBerry') {
			// for blackberry: use mouseup event (instead of mousedown event)
			// because <select> object is active.
			this._addEvent(td, 'mouseup',
				function(ev) { obj._setDate(date); }, 1);
		} else {
			this._addEvent(td, 'mousedown',
				function(ev) { obj._setDate(date); }, 1);
		}
	},

	_createDateCache: function() {
		if(this._date_cache) return true;

		this._date_cache = [];
		for (var date = 1; date <= 31; date++) {
			var td = document.createElement('td');
			if(!td) return false;
			td.appendChild(document.createTextNode(date));
			this._setDateEvent(td, date);
			this._setHover(td, 1);

			this._date_cache[date] = td;
		}
		return true;
	},

	_elem: function(id) {
		if(document.all) return document.all(id);
		return document.getElementById(id);
	},

	_getBrowser: function() {
		if(navigator.userAgent.indexOf('BlackBerry') !== -1) return 'BlackBerry';
		if(navigator.userAgent.indexOf('AppleWebKit') !== -1) return 'AppleWebKit';
		if(navigator.userAgent.indexOf('Gecko') !== -1) return 'Gecko';
		if(window.opera) return 'Opera';
		if(navigator.userAgent.indexOf('MSIE') !== -1) return 'MSIE';
	},

	_getWindowHeight: function() {
		if(this._getBrowser() === 'MSIE') {
			if(document.documentElement.clientHeight) {
				return document.documentElement.clientHeight;
			} else {
				return document.body.clientHeight;
			}
		} else {
			return window.innerHeight;
		}
	},

	_getAbsoluteOffsetTop: function(obj) {
		var top_div = document.body;
		if(this.top_div_name) top_div = this._elem(this.top_div_name);

		var top = obj.offsetTop;
		var parent = obj.offsetParent;
		while (parent && parent !== top_div) {
			top += parent.offsetTop;
			parent = parent.offsetParent;
		}
		top += obj.offsetHeight;

		var div_height = top_div.clientHeight;
		if(top_div === document.body) {
			div_height = this._getWindowHeight();
		}

		if(!this.no_adjust_top_pos &&
			top + this._cal.offsetHeight > top_div.scrollTop + div_height) {
			top = top - this._cal.offsetHeight - obj.offsetHeight;
			if(top < 0) top = 0;
        }
		return top;
	},

	_getAbsoluteOffsetLeft: function(obj) {
		var top_div = document.body;
		if(this.top_div_name) top_div = this._elem(this.top_div_name);

		var left = obj.offsetLeft;
		var parent = obj.offsetParent;
		while (parent && parent !== top_div) {
			left += parent.offsetLeft;
			parent = parent.offsetParent;
		}

		if(left + this._cal.offsetWidth >
			top_div.scrollLeft + top_div.clientWidth) {
			left = top_div.scrollLeft + top_div.clientWidth -
				this._cal.offsetWidth;
			if(left < 0) left = 0;
        }
		return left;
	},

	_addEvent: function(e, ev, func, global_flg) {
		if(global_flg) {
			if (!this._global_events) this._global_events = [];
			this._global_events.push([e, ev, func]);
		} else {
			if (!this._events) this._events = [];
			this._events.push([e, ev, func]);
		}

		if(window.addEventListener) {
			e.addEventListener(ev, func, false);
		} else {
			// for Internet Explorer
			e.attachEvent('on' + ev, func);
		}
	},

	_removeEvent: function(e, ev, func) {
		if(window.removeEventListener) {
			e.removeEventListener(ev, func, false);
		} else {
			// for Internet Explorer
			e.detachEvent('on' + ev, func);
		}
	},

	_removeAllEvents: function() {
		if (!this._events) return;
		for (var i = 0; i < this._events.length; i++) {
			this._removeEvent.apply(this, this._events[i]);
			this._events[i][0] = null;
		}
		this._events = false;
	},

	_setHover: function(e, global_flg) {
		this._addEvent(e, 'mouseover',
			function() {
				if(e.className.indexOf('_Hover') !== -1) return;
				e.className = e.className + '_Hover';
			},
			global_flg);
		this._addEvent(e, 'mouseout',
			function() {
				e.className = e.className.replace('_Hover', '');
			},
			global_flg);
	},

	_isLeapYear: function() {
		var y = this._date.getFullYear();
		if(((y % 4 === 0) && (y % 100 !== 0)) || (y % 400 === 0)) return true;
		return false;
	},

	_getLastDate: function() {
		var daysOfMonth =     [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
		var daysOfMonthLeap = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
		if (this._isLeapYear()) {
			return daysOfMonthLeap[this._date.getMonth()];
		}
		return daysOfMonth[this._date.getMonth()];
	},

	_getMonth: function() {
		return this._month[this._date.getMonth()];
	},

	_getFirstDay: function() {
		this._date.setDate(1);
		return this._date.getDay();
	},

	_appendTDDate: function(parent, date, dayOfWeek) {
		var cls = 'TlibJSCalendarDate';
		if(dayOfWeek === 0) cls = 'TlibJSCalendarSun';
		if(dayOfWeek === 6) cls = 'TlibJSCalendarSat';

		var td = this._date_cache[date];
		td.className = cls;
		parent.appendChild(td);
	},

	_appendTDBlank: function(parent) {
		parent.appendChild(this._blank_td_cache[this._blank_td_idx]);
		this._blank_td_idx++;
	},

	_prevYear: function() {
		this._date.setFullYear(this._date.getFullYear() - 1);
		this._refresh();
	},

	_prevMonth: function() {
		var pre = this._date.getMonth() - 1;
		if (pre < 0) {
			pre = 11;
			this._date.setFullYear(this._date.getFullYear() - 1);
		}
		this._date.setMonth(pre);
		this._refresh();
	},

	_nextMonth: function() {
		var next = this._date.getMonth() + 1;
		if (next > 11) {
			next = 0;
			this._date.setFullYear(this._date.getFullYear() + 1);
		}
		this._date.setMonth(next);
		this._refresh();
	},

	_nextYear: function() {
		this._date.setFullYear(this._date.getFullYear() + 1);
		this._refresh();
	},

	_makeBtns: function(parent) {
		for (var i = 0; i < 4; i++) parent.appendChild(this._btn_cache[i]);
	},

	_buildCalendar: function() {
		if(!this._createDateCache()) return;
		if(!this._createTableHeaderCache()) return;
		if(!this._createBtnCache()) return;
		if(!this._createBlankTdCache()) return;
		this._blank_td_idx = 0;

		this._clearCalendar();

		var cal_df = document.createDocumentFragment();

		var header_div = document.createElement('div');
		if(!header_div) return;
		header_div.setAttribute('id', 'TlibJSCalendarHeader');
		cal_df.appendChild(header_div);

		var yymm = document.createElement('div');
		if(!yymm) return;
		yymm.setAttribute('id', 'TlibJSCalendarYearMonth');
		yymm.appendChild(document.createTextNode(this._makeHeader()));
		header_div.appendChild(yymm);

		this._makeBtns(header_div);

		var table_div = document.createElement('div');
		if(!table_div) return;
		cal_df.appendChild(table_div);

		var table = document.createElement('table');
		if(!table) return;
		table.setAttribute('id', 'TlibJSCalendarTable');
		table_div.appendChild(table);

		var tbody = document.createElement('tbody');
		if(!tbody) return;
		table.appendChild(tbody);

		var firstDay = this._getFirstDay();
		var lastDate = this._getLastDate();
		var i, date;
		var tr, th, td;

		tbody.appendChild(this._table_header_cache);

		var row = 0;
		tr = document.createElement('tr');
		if(!tr) return;
		tbody.appendChild(tr);
		for(i = 0; i < firstDay; i++) {
			this._appendTDBlank(tr);
		}
		for(date = 1; date <= lastDate; i++) {
			if (i > 0 && i % 7 === 0) {
				row++;
				tr = document.createElement('tr');
				if(!tr) return;
				tbody.appendChild(tr);
			}
			this._appendTDDate(tr, date, i % 7);
			date++;
		}
		for(; (i % 7 !== 0); i++) {
			 this._appendTDBlank(tr);
		}
		row++;

		for(; row < 6; row++) {
			tr = document.createElement('tr');
			if(!tr) return;
			tbody.appendChild(tr);
			for(i = 0; i < 7; i++) {
				this._appendTDBlank(tr);
			}
		}

		this._cal.appendChild(cal_df);

		this._header_div = header_div;
		this._table_div = table_div;
	},

	_setShim: function() {
		// for Internet Explorer
		if(this._shim) {
			this._shim.style.top = this._cal.offsetTop + 'px';
			this._shim.style.left = this._cal.offsetLeft + 'px';
			this._shim.style.width = this._cal.offsetWidth + 'px';
			this._shim.style.height = this._cal.offsetHeight + 'px';
			this._shim.style.display = 'block';
		}
	},

	_setBkLayer: function() {
		if(this._bk_layer) {
			this._bk_layer.style.width = document.body.scrollWidth;
			this._bk_layer.style.height = document.body.scrollHeight;
			this._bk_layer.style.display = 'block';
		}
	},

	_refresh: function() {
		this._buildCalendar();
		this._setShim();
	},

	_clearCalendar: function() {
		this._removeAllEvents();

		if(this._header_div) {
			this._cal.removeChild(this._header_div);
			this._header_div = null;
		}
		if(this._table_div) {
			this._cal.removeChild(this._table_div);
			this._table_div = null;
		}
	},

	_makeYM: function(fmt) {
		var ym = fmt;
		ym = ym.replace(/YYYY/, this._date.getFullYear());
		ym = ym.replace(/YY/, 
			this._date.getFullYear().toString().substring(2,4));
		ym = ym.replace(/Mon/, this._getMonth());

		var mm = this._date.getMonth() + 1;
		if(mm < 10) {
			ym = ym.replace(/MM/, '0' + mm);
		} else {
			ym = ym.replace(/MM/, mm);
		}
		return ym;
	},

	_makeHeader: function() {
		return this._makeYM(this.header_format);
	},

	_setDate: function(date) {
		var date_str = this._makeYM(this.date_format);
		if(date < 10) {
			date_str = date_str.replace(/DD/, '0' + date);
		} else {
			date_str = date_str.replace(/DD/, date);
		}

		this._target.value = date_str;

		this._hide();
		if(this.date_changed) this.date_changed(this._target);
	},

	_createCalendarDiv: function() {
        this._cal = this._elem(this.cal_div_name);
	},

	_createShim: function() {
        this._shim = this._elem(this.cal_shim_name);
	},

	_createBkLayer: function() {
        this._bk_layer = this._elem(this.cal_bk_layer_name);
	},

	_adjustWindowPos: function() {
		// for Netscape 7.X and Firefox
		if(this._getBrowser() === 'Gecko') {
			var width = 200;
			var table = this._elem('TlibJSCalendarTable');
			if(table) width = table.offsetWidth;
			this._header_div.style.width = width;
			this._cal.style.width = width;
		}

		this._cal.style.top = this._getAbsoluteOffsetTop(this._target) + 'px';
		this._cal.style.left = this._getAbsoluteOffsetLeft(this._target) + 'px';
	},

	show: function(form_name, input_name) {
		if(!this._shim && this._getBrowser() === 'MSIE') this._createShim();
		if(!this._bk_layer && this._getBrowser() === 'BlackBerry') this._createBkLayer();
		if(!this._cal) this._createCalendarDiv();
		this._target = document.forms[form_name].elements[input_name];

		this._date = new Date();
		this._buildCalendar();

		this._cal.style.top = 0;
		this._cal.style.left = 0;

		this._cal.style.display = 'block';

		this._adjustWindowPos();
		this._setShim();
		this._setBkLayer();
		this._setMouseDownHandler();
	},

	_hide: function() {
		document.onmousedown = null;
		this._clearCalendar();
		this._cal.style.display = 'none'
		if(this._shim) this._shim.style.display = 'none';
		if(this._bk_layer) this._bk_layer.style.display = 'none';
	},

	_setMouseDownHandler: function() {
		var obj = this;
		document.onmousedown = function(ev) {
			obj._mouseDownHandler(ev);
		};
	},

	_mouseDownHandler: function(ev) {
		var x, y;

		if(ev) {
			x = ev.pageX;
			y = ev.pageY;
		} else {
			// for Internet Explorer
			x = event.x + document.body.scrollLeft;
			y = event.y + document.body.scrollTop;
		}

		if(this.top_div_name) {
		    x = x - this._elem(this.top_div_name).offsetLeft;
		    y = y - this._elem(this.top_div_name).offsetTop;
		}

		if(x > this._cal.offsetLeft && 
		   x < this._cal.offsetLeft + this._cal.offsetWidth &&
		   y > this._cal.offsetTop && 
		   y < this._cal.offsetTop + this._cal.offsetHeight) {
			return;
		}

		this._hide();
	}
}


