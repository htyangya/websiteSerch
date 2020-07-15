(function (c) {
  c.fn.splitter = function (h) {
    h = h || {};
    return this.each(function () {
      function q(b) {
        b = f._posSplit + b[a.eventPos];
        a.outline ? (b = Math.max(0, Math.min(b, d._DA - e._DA)), e.css(a.origin, b)) : m(b)
      }

      function r(b) {
        e.removeClass(a.activeClass);
        b = f._posSplit + b[a.eventPos];
        a.outline && (n.remove(), n = null, m(b));
        l.css("-webkit-user-select", "text");
        c(document).unbind("mousemove", q).unbind("mouseup", r)
      }

      function m(b) {
        b = Math.max(f._min, d._DA - g._max, Math.min(b, f._max, d._DA - e._DA - g._min));
        e._DA = e[0][a.pxSplit];
        e.css(a.origin, b).css(a.fixed, d._DF);
        var c = d._DF;
        "width" === a.fixed && 0 < a.width_adjust && (c -= a.width_adjust);
        f.css(a.origin, 0).css(a.split, b).css(a.fixed, c);
        g.css(a.origin, b + e._DA).css(a.split, d._DA - e._DA - b).css(a.fixed, c);
        a.callback && a.callback(d)
      }

      function p(a, d) {
        for (var c = 0, e = 1; e < arguments.length; e++) c += Math.max(parseInt(a.css(arguments[e])) || 0, 0);
        return c
      }
      var n, a = c.extend({
          activeClass: "active",
          pxPerKey: 8,
          tabIndex: 0,
          accessKey: ""
        }, {
          v: {
            keyLeft: 39,
            keyRight: 37,
            cursor: "e-resize",
            splitbarClass: "vsplitbar",
            outlineClass: "voutline",
            id: "vsplitbar",
            type: "v",
            eventPos: "pageX",
            origin: "left",
            split: "width",
            pxSplit: "offsetWidth",
            side1: "Left",
            side2: "Right",
            fixed: "height",
            pxFixed: "offsetHeight",
            side3: "Top",
            side4: "Bottom"
          },
          h: {
            keyTop: 40,
            keyBottom: 38,
            cursor: "n-resize",
            splitbarClass: "hsplitbar",
            outlineClass: "houtline",
            id: "hsplitbar",
            type: "h",
            eventPos: "pageY",
            origin: "top",
            split: "height",
            pxSplit: "offsetHeight",
            side1: "Top",
            side2: "Bottom",
            fixed: "width",
            pxFixed: "offsetWidth",
            side3: "Left",
            side4: "Right"
          }
        }[(h.splitHorizontal ? "h" : h.splitVertical ? "v" : h.type) || "v"], h),
        d = c(this).css({
          position: "relative"
        }),
        l = c(">*", d[0]).css({
          position: "absolute",
          "z-index": "1",
          "-moz-outline-style": "none"
        }),
        f = c(l[0]),
        g = c(l[1]),
        k = c('<a href="javascript:void(0)"></a>').attr({
          accessKey: a.accessKey,
          tabIndex: a.tabIndex,
          title: a.splitbarClass
        }).bind("focus", function () {
          this.focus();
          e.addClass(a.activeClass)
        }).bind("keydown", function (b) {
          b = b.which || b.keyCode;
          (b = b == a["key" + a.side1] ? 1 : b == a["key" + a.side2] ? -1 : 0) && m(f[0][a.pxSplit] + b * a.pxPerKey, !1)
        }).bind("blur", function () {
          e.removeClass(a.activeClass)
        }),
        e = c(l[2] || "<div></div>").insertAfter(f).css("z-index", "100").append(k).attr("id", a.id).attr({
          "class": a.splitbarClass,
          unselectable: "on"
        }).css({
          position: "absolute",
          "user-select": "none",
          "-webkit-user-select": "none",
          "-khtml-user-select": "none",
          "-moz-user-select": "none"
        }).bind("mousedown", function (b) {
          a.outline && (n = n || e.clone(!1).insertAfter(f));
          l.css("-webkit-user-select", "none");
          e.addClass(a.activeClass);
          f._posSplit = f[0][a.pxSplit] - b[a.eventPos];
          c(document).bind("mousemove", q).bind("mouseup", r)
        });
      /^(auto|default|)$/.test(e.css("cursor")) && e.css("cursor", a.cursor);
      e._DA = e[0][a.pxSplit];
      d._PBF = c.boxModel ? p(d, "border" + a.side3 + "Width", "border" + a.side4 + "Width") : 0;
      d._PBA = c.boxModel ? p(d, "border" + a.side1 + "Width", "border" + a.side2 + "Width") : 0;
      f._pane = a.side1;
      g._pane = a.side2;
      c.each([f, g], function () {
        this._min = a["min" + this._pane] || p(this, "min-" + a.split);
        this._max = a["max" + this._pane] || p(this, "max-" + a.split) || 9999;
        this._init = !0 === a["size" + this._pane] ? parseInt(c.curCSS(this[0], a.split)) : a["size" + this._pane]
      });
      k = f._init;
      isNaN(g._init) || (k = d[0][a.pxSplit] - d._PBA - g._init - e._DA);
      if (a.cookie) {
        c.cookie || alert("jQuery.splitter(): jQuery cookie plugin required");
        var s = parseInt(c.cookie(a.cookie));
        isNaN(s) || (k = s);
        c(window).bind("unload", function () {
          var b = String(e.css(a.origin));
          c.cookie(a.cookie, b, {
            expires: a.cookieExpires || 365,
            path: a.cookiePath || document.location.pathname
          })
        })
      }
      isNaN(k) && (k = Math.round((d[0][a.pxSplit] - d._PBA - e._DA) / 2));
      d.bind("resize", function (b, c) {
        b.stopPropagation();
        d._DF = d[0][a.pxFixed] - d._PBF;
        d._DA = d[0][a.pxSplit] - d._PBA;
        0 >= d._DF || 0 >= d._DA || m(!isNaN(c) ? c : !a.sizeRight && !a.sizeBottom ? f[0][a.pxSplit] : d._DA - g[0][a.pxSplit] - e._DA)
      })
    })
  }
})(jQuery);
(function (a, r, s) {
  function d(a) {
    a = a || location.href;
    return "#" + a.replace(/^[^#]*#?(.*)$/, "$1")
  }
  "$:nomunge";
  var c = "hashchange",
    l = document,
    e, g = a.event.special,
    t = l.documentMode,
    n = "on" + c in r && (t === s || 7 < t);
  a.fn[c] = function (a) {
    return a ? this.bind(c, a) : this.trigger(c)
  };
  a.fn[c].delay = 50;
  g[c] = a.extend(g[c], {
    setup: function () {
      if (n) return !1;
      a(e.start)
    },
    teardown: function () {
      if (n) return !1;
      a(e.stop)
    }
  });
  e = function () {
    function e() {
      var f = d(),
        b = g(m);
      f !== m ? (p(m = f, b), a(r).trigger(c)) : b !== m && (location.href = location.href.replace(/#.*/, "") + b);
      h = setTimeout(e, a.fn[c].delay)
    }
    var k = {},
      h, m = d(),
      q = function (a) {
        return a
      },
      p = q,
      g = q;
    k.start = function () {
      h || e()
    };
    k.stop = function () {
      h && clearTimeout(h);
      h = s
    };
    "Microsoft Internet Explorer" === navigator.appName && !n && function () {
      var f, b;
      k.start = function () {
        f || (b = (b = a.fn[c].src) && b + d(), f = a('<iframe tabindex="-1" title="empty"/>').hide().one("load", function () {
          b || p(d());
          e()
        }).attr("src", b || "javascript:0").insertAfter("body")[0].contentWindow, l.onpropertychange = function () {
          try {
            "title" === event.propertyName && (f.document.title = l.title)
          } catch (a) {}
        })
      };
      k.stop = q;
      g = function () {
        return d(f.location.href)
      };
      p = function (b, e) {
        var d = f.document,
          g = a.fn[c].domain;
        b !== e && (d.title = l.title, d.open(), g && d.write('<script>document.domain="' + g + '"</script>'), d.close(), f.location.hash = b)
      }
    }();
    return k
  }()
})(jQuery, this);
(function (b) {
  "function" === typeof define && define.amd ? define(["jquery"], b) : b(jQuery)
})(function (b) {
  var l = [],
    q = b(document),
    m = navigator.userAgent.toLowerCase(),
    n = b(window),
    g = [],
    r = null,
    s = /msie/.test(m) && !/opera/.test(m),
    t = /opera/.test(m),
    p, u;
  p = s && /msie 6./.test(m) && "object" !== typeof window.XMLHttpRequest;
  u = s && /msie 7.0/.test(m);
  b.modal = function (a, h) {
    return b.modal.impl.init(a, h)
  };
  b.modal.close = function () {
    b.modal.impl.close()
  };
  b.modal.focus = function (a) {
    b.modal.impl.focus(a)
  };
  b.modal.setContainerDimensions = function () {
    b.modal.impl.setContainerDimensions()
  };
  b.modal.setPosition = function () {
    b.modal.impl.setPosition()
  };
  b.modal.update = function (a, h) {
    b.modal.impl.update(a, h)
  };
  b.fn.modal = function (a) {
    return b.modal.impl.init(this, a)
  };
  b.modal.defaults = {
    appendTo: "body",
    focus: !0,
    opacity: 50,
    overlayId: "simplemodal-overlay",
    overlayCss: {},
    containerId: "simplemodal-container",
    containerCss: {},
    dataId: "simplemodal-data",
    dataCss: {},
    minHeight: null,
    minWidth: null,
    maxHeight: null,
    maxWidth: null,
    autoResize: !1,
    autoPosition: !0,
    zIndex: 12E3,
    close: !0,
    closeHTML: '<a class="modalCloseImg" title="Close"></a>',
    closeClass: "simplemodal-close",
    escClose: !0,
    overlayClose: !1,
    fixed: !0,
    position: null,
    persist: !1,
    modal: !0,
    onOpen: null,
    onShow: null,
    onClose: null
  };
  b.modal.impl = {
    d: {},
    init: function (a, h) {
      if (this.d.data) return !1;
      r = s && !b.support.boxModel;
      this.o = b.extend({}, b.modal.defaults, h);
      this.zIndex = this.o.zIndex;
      this.occb = !1;
      if ("object" === typeof a) a = a instanceof b ? a : b(a), this.d.placeholder = !1, 0 < a.parent().parent().size() && (a.before(b("<span></span>").attr("id", "simplemodal-placeholder").css({
        display: "none"
      })), this.d.placeholder = !0, this.display = a.css("display"), this.o.persist || (this.d.orig = a.clone(!0)));
      else if ("string" === typeof a || "number" === typeof a) a = b("<div></div>").html(a);
      else return alert("SimpleModal Error: Unsupported data type: " + typeof a), this;
      this.create(a);
      this.open();
      b.isFunction(this.o.onShow) && this.o.onShow.apply(this, [this.d]);
      return this
    },
    create: function (a) {
      this.getDimensions();
      this.o.modal && p && (this.d.iframe = b('<iframe src="javascript:false;"></iframe>').css(b.extend(this.o.iframeCss, {
        display: "none",
        opacity: 0,
        position: "fixed",
        height: g[0],
        width: g[1],
        zIndex: this.o.zIndex,
        top: 0,
        left: 0
      })).appendTo(this.o.appendTo));
      this.d.overlay = b("<div></div>").attr("id", this.o.overlayId).addClass("simplemodal-overlay").css(b.extend(this.o.overlayCss, {
        display: "none",
        opacity: this.o.opacity / 100,
        height: this.o.modal ? l[0] : 0,
        width: this.o.modal ? l[1] : 0,
        position: "fixed",
        left: 0,
        top: 0,
        zIndex: this.o.zIndex + 1
      })).appendTo(this.o.appendTo);
      this.d.container = b("<div></div>").attr("id", this.o.containerId).addClass("simplemodal-container").css(b.extend({
        position: this.o.fixed ? "fixed" : "absolute"
      }, this.o.containerCss, {
        display: "none",
        zIndex: this.o.zIndex + 2
      })).append(this.o.close && this.o.closeHTML ? b(this.o.closeHTML).addClass(this.o.closeClass) : "").appendTo(this.o.appendTo);
      this.d.wrap = b("<div></div>").attr("tabIndex", -1).addClass("simplemodal-wrap").css({
        height: "100%",
        outline: 0,
        width: "100%"
      }).appendTo(this.d.container);
      this.d.data = a.attr("id", a.attr("id") || this.o.dataId).addClass("simplemodal-data").css(b.extend(this.o.dataCss, {
        display: "none"
      })).appendTo("body");
      this.setContainerDimensions();
      this.d.data.appendTo(this.d.wrap);
      (p || r) && this.fixIE()
    },
    bindEvents: function () {
      var a = this;
      b("." + a.o.closeClass).bind("click.simplemodal", function (b) {
        b.preventDefault();
        a.close()
      });
      a.o.modal && (a.o.close && a.o.overlayClose) && a.d.overlay.bind("click.simplemodal", function (b) {
        b.preventDefault();
        a.close()
      });
      q.bind("keydown.simplemodal", function (b) {
        a.o.modal && 9 === b.keyCode ? a.watchTab(b) : a.o.close && a.o.escClose && 27 === b.keyCode && (b.preventDefault(), a.close())
      });
      n.bind("resize.simplemodal orientationchange.simplemodal", function () {
        a.getDimensions();
        a.o.autoResize ? a.setContainerDimensions() : a.o.autoPosition && a.setPosition();
        p || r ? a.fixIE() : a.o.modal && (a.d.iframe && a.d.iframe.css({
          height: g[0],
          width: g[1]
        }), a.d.overlay.css({
          height: l[0],
          width: l[1]
        }))
      })
    },
    unbindEvents: function () {
      b("." + this.o.closeClass).unbind("click.simplemodal");
      q.unbind("keydown.simplemodal");
      n.unbind(".simplemodal");
      this.d.overlay.unbind("click.simplemodal")
    },
    fixIE: function () {
      var a = this.o.position;
      this.removeExpression && b.each([this.d.iframe || null, !this.o.modal ? null : this.d.overlay, "fixed" === this.d.container.css("position") ? this.d.container : null], function (b, e) {
        if (e) {
          var f = e[0].style;
          f.position = "absolute";
          if (2 > b) f.removeExpression("height"), f.removeExpression("width"), f.setExpression("height", 'document.body.scrollHeight > document.body.clientHeight ? document.body.scrollHeight : document.body.clientHeight + "px"'), f.setExpression("width", 'document.body.scrollWidth > document.body.clientWidth ? document.body.scrollWidth : document.body.clientWidth + "px"');
          else {
            var c, d;
            a && a.constructor === Array ? (c = a[0] ? "number" === typeof a[0] ? a[0].toString() : a[0].replace(/px/, "") : e.css("top").replace(/px/, ""), c = -1 === c.indexOf("%") ? c + ' + (t = document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop) + "px"' : parseInt(c.replace(/%/, "")) + ' * ((document.documentElement.clientHeight || document.body.clientHeight) / 100) + (t = document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop) + "px"', a[1] && (d = "number" === typeof a[1] ? a[1].toString() : a[1].replace(/px/, ""), d = -1 === d.indexOf("%") ? d + ' + (t = document.documentElement.scrollLeft ? document.documentElement.scrollLeft : document.body.scrollLeft) + "px"' : parseInt(d.replace(/%/, "")) + ' * ((document.documentElement.clientWidth || document.body.clientWidth) / 100) + (t = document.documentElement.scrollLeft ? document.documentElement.scrollLeft : document.body.scrollLeft) + "px"')) : (c = '(document.documentElement.clientHeight || document.body.clientHeight) / 2 - (this.offsetHeight / 2) + (t = document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop) + "px"', d = '(document.documentElement.clientWidth || document.body.clientWidth) / 2 - (this.offsetWidth / 2) + (t = document.documentElement.scrollLeft ? document.documentElement.scrollLeft : document.body.scrollLeft) + "px"');
            f.removeExpression("top");
            f.removeExpression("left");
            f.setExpression("top", c);
            f.setExpression("left", d)
          }
        }
      })
    },
    focus: function (a) {
      var h = this;
      a = a && -1 !== b.inArray(a, ["first", "last"]) ? a : "first";
      var e = b(":input:enabled:visible:" + a, h.d.wrap);
      setTimeout(function () {
        0 < e.length ? e.focus() : h.d.wrap.focus()
      }, 10)
    },
    getDimensions: function () {
      var a = "undefined" === typeof window.innerHeight ? n.height() : window.innerHeight;
      l = [q.height(), q.width()];
      g = [a, n.width()]
    },
    getVal: function (a, b) {
      return a ? "number" === typeof a ? a : "auto" === a ? 0 : 0 < a.indexOf("%") ? parseInt(a.replace(/%/, "")) / 100 * ("h" === b ? g[0] : g[1]) : parseInt(a.replace(/px/, "")) : null
    },
    update: function (a, b) {
      if (!this.d.data) return !1;
      this.d.origHeight = this.getVal(a, "h");
      this.d.origWidth = this.getVal(b, "w");
      this.d.data.hide();
      a && this.d.container.css("height", a);
      b && this.d.container.css("width", b);
      this.setContainerDimensions();
      this.d.data.show();
      this.o.focus && this.focus();
      this.unbindEvents();
      this.bindEvents()
    },
    setContainerDimensions: function () {
      var a = p || u,
        b = this.d.origHeight ? this.d.origHeight : t ? this.d.container.height() : this.getVal(a ? this.d.container[0].currentStyle.height : this.d.container.css("height"), "h"),
        a = this.d.origWidth ? this.d.origWidth : t ? this.d.container.width() : this.getVal(a ? this.d.container[0].currentStyle.width : this.d.container.css("width"), "w"),
        e = this.d.data.outerHeight(!0),
        f = this.d.data.outerWidth(!0);
      this.d.origHeight = this.d.origHeight || b;
      this.d.origWidth = this.d.origWidth || a;
      var c = this.o.maxHeight ? this.getVal(this.o.maxHeight, "h") : null,
        d = this.o.maxWidth ? this.getVal(this.o.maxWidth, "w") : null,
        c = c && c < g[0] ? c : g[0],
        d = d && d < g[1] ? d : g[1],
        k = this.o.minHeight ? this.getVal(this.o.minHeight, "h") : "auto",
        b = b ? this.o.autoResize && b > c ? c : b < k ? k : b : e ? e > c ? c : this.o.minHeight && "auto" !== k && e < k ? k : e : k,
        c = this.o.minWidth ? this.getVal(this.o.minWidth, "w") : "auto",
        a = a ? this.o.autoResize && a > d ? d : a < c ? c : a : f ? f > d ? d : this.o.minWidth && "auto" !== c && f < c ? c : f : c;
      this.d.container.css({
        height: b,
        width: a
      });
      this.d.wrap.css({
        overflow: e > b || f > a ? "auto" : "visible"
      });
      this.o.autoPosition && this.setPosition()
    },
    setPosition: function () {
      var a, b;
      a = g[0] / 2 - this.d.container.outerHeight(!0) / 2;
      b = g[1] / 2 - this.d.container.outerWidth(!0) / 2;
      var e = "fixed" !== this.d.container.css("position") ? n.scrollTop() : 0;
      this.o.position && "[object Array]" === Object.prototype.toString.call(this.o.position) ? (a = e + (this.o.position[0] || a), b = this.o.position[1] || b) : a = e + a;
      this.d.container.css({
        left: b,
        top: a
      })
    },
    watchTab: function (a) {
      if (0 < b(a.target).parents(".simplemodal-container").length) {
        if (this.inputs = b(":input:enabled:visible:first, :input:enabled:visible:last", this.d.data[0]), !a.shiftKey && a.target === this.inputs[this.inputs.length - 1] || a.shiftKey && a.target === this.inputs[0] || 0 === this.inputs.length) a.preventDefault(), this.focus(a.shiftKey ? "last" : "first")
      } else a.preventDefault(), this.focus()
    },
    open: function () {
      this.d.iframe && this.d.iframe.show();
      b.isFunction(this.o.onOpen) ? this.o.onOpen.apply(this, [this.d]) : (this.d.overlay.show(), this.d.container.show(), this.d.data.show());
      this.o.focus && this.focus();
      this.bindEvents()
    },
    close: function () {
      if (!this.d.data) return !1;
      this.unbindEvents();
      if (b.isFunction(this.o.onClose) && !this.occb) this.occb = !0, this.o.onClose.apply(this, [this.d]);
      else {
        if (this.d.placeholder) {
          var a = b("#simplemodal-placeholder");
          this.o.persist ? a.replaceWith(this.d.data.removeClass("simplemodal-data").css("display", this.display)) : (this.d.data.hide().remove(), a.replaceWith(this.d.orig))
        } else this.d.data.hide().remove();
        this.d.container.hide().remove();
        this.d.overlay.hide();
        this.d.iframe && this.d.iframe.hide().remove();
        this.d.overlay.remove();
        this.d = {}
      }
    }
  }
});

function _adjust_confirm_height(c, b) {
  var a = $(".header", c.data[0]),
    d = $(".message", c.data[0]),
    e = $(".buttons", c.data[0]),
    a = a.outerHeight(!0) + d.outerHeight(!0) + e.outerHeight(!0);
  void 0 != b && b < a && (a = b);
  $(c.container[0]).height(a)
}

function confirm_2cb(c, b, a) {
  $("#confirm").modal({
    closeHTML: "<a href='#' title='Close' class='modal-close'>x</a>",
    position: ["20%"],
    overlayId: "confirm-overlay",
    containerId: "confirm-container",
    onYes: function (a) {
      $.isFunction(b) && b.apply();
      $.modal.close()
    },
    onCancel: function (b) {
      $.isFunction(a) && a.apply();
      $.modal.close()
    },
    onClose: function (a) {
      $(document).unbind("keydown.confirm");
      this.close()
    },
    onShow: function (a) {
      var b = this;
      $(".message", a.data[0]).append(c);
      _adjust_confirm_height(a);
      $(".yes", a.data[0]).click(b.o.onYes);
      $(".no", a.data[0]).click(b.o.onCancel);
      $(document).bind("keydown.confirm", function (a) {
        if (89 === a.keyCode) b.o.onYes();
        if (78 === a.keyCode) b.o.onCancel()
      })
    }
  })
}

function confirm_dlg(c, b) {
  void 0 === b && console.log("warning: confirm is overwrited function in current environment! This function require callback function");
  confirm_2cb(c, b, null)
}

function alert_dlg(c, b) {
  $("#alert").modal({
    closeHTML: "<a href='#' title='Close' class='modal-close'>x</a>",
    position: ["20%"],
    overlayId: "confirm-overlay",
    containerId: "confirm-container",
    onShow: function (a) {
      $(".header > span", a.data[0]).text(c);
      $(".message", a.data[0]).append(b);
      _adjust_confirm_height(a)
    }
  })
}
window.org_confirm = window.confirm;
window.confirm = confirm_dlg;
(function (b) {
  b.fn.jqm = function (a) {
    var m = {
      overlay: 50,
      overlayClass: "jqmOverlay",
      closeClass: "jqmClose",
      trigger: ".jqModal",
      ajax: d,
      ajaxText: "",
      target: d,
      modal: d,
      toTop: d,
      onShow: d,
      onHide: d,
      onLoad: d
    };
    return this.each(function () {
      if (this._jqm) return k[this._jqm].c = b.extend({}, k[this._jqm].c, a);
      g++;
      this._jqm = g;
      k[g] = {
        c: b.extend(m, b.jqm.params, a),
        a: d,
        w: b(this).addClass("jqmID" + g),
        s: g
      };
      m.trigger && b(this).jqmAddTrigger(m.trigger)
    })
  };
  b.fn.jqmAddClose = function (a) {
    return q(this, a, "jqmHide")
  };
  b.fn.jqmAddTrigger = function (a) {
    return q(this, a, "jqmShow")
  };
  b.fn.jqmShow = function (a) {
    return this.each(function () {
      a = a || window.event;
      b.jqm.open(this._jqm, a)
    })
  };
  b.fn.jqmHide = function (a) {
    return this.each(function () {
      a = a || window.event;
      b.jqm.close(this._jqm, a)
    })
  };
  b.jqm = {
    hash: {},
    open: function (a, m) {
      var c = k[a],
        e = c.c,
        n = "." + e.closeClass,
        h = parseInt(c.w.css("z-index")),
        h = 0 < h ? h : 3E3,
        f = b("<div></div>").css({
          height: "100%",
          width: "100%",
          position: "fixed",
          left: 0,
          top: 0,
          "z-index": h - 1,
          opacity: e.overlay / 100,
          display: "none"
        });
      if (c.a) return d;
      c.t = m;
      c.a = !0;
      c.w.css("z-index", h);
      e.modal ? (l[0] || r("bind"), l.push(a)) : 0 < e.overlay ? c.w.jqmAddClose(f) : f = d;
      c.o = f ? f.addClass(e.overlayClass).prependTo("body").show() : d;
      if (s && (b("html,body").css({
          height: "100%",
          width: "100%"
        }), f)) {
        var f = f.css({
            position: "absolute"
          })[0],
          g;
        for (g in {
            Top: 1,
            Left: 1
          }) f.style.setExpression(g.toLowerCase(), "(_=(document.documentElement.scroll" + g + " || document.body.scroll" + g + "))+'px'")
      }
      e.ajax ? (h = e.target || c.w, f = e.ajax, h = "string" == typeof h ? b(h, c.w) : b(h), f = "@" == f.substr(0, 1) ? b(m).attr(f.substring(1)) : f, h.html(e.ajaxText).load(f, function () {
        e.onLoad && e.onLoad.call(this, c);
        n && c.w.jqmAddClose(b(n, c.w));
        t(c)
      })) : n && c.w.jqmAddClose(b(n, c.w));
      e.toTop && c.o && c.w.before('<span id="jqmP' + c.w[0]._jqm + '"></span>').insertAfter(c.o);
      e.onShow ? e.onShow(c) : c.w.show();
      t(c);
      return d
    },
    close: function (a) {
      a = k[a];
      if (!a.a) return d;
      a.a = d;
      l[0] && (l.pop(), l[0] || r("unbind"));
      a.c.toTop && a.o && b("#jqmP" + a.w[0]._jqm).after(a.w).remove();
      if (a.c.onHide) a.c.onHide(a);
      else a.w.hide(), a.o && a.o.remove();
      return d
    },
    params: {}
  };
  var g = 0,
    k = b.jqm.hash,
    l = [],
    s = !1,
    d = !1,
    u = b('<iframe src="javascript:false;document.write(\'\');" class="jqm"></iframe>').css({
      opacity: 0
    }),
    t = function (a) {
      s && (a.o ? a.o.html('<p style="width:100%;height:100%"/>').prepend(u) : b("iframe.jqm", a.w)[0] || a.w.prepend(u));
      v(a)
    },
    v = function (a) {
      try {
        b(":input:visible", a.w)[0].focus()
      } catch (d) {}
    },
    r = function (a) {
      b()[a]("keypress", p)[a]("keydown", p)[a]("mousedown", p)
    },
    p = function (a) {
      var d = k[l[l.length - 1]];
      (a = !b(a.target).parents(".jqmID" + d.s)[0]) && v(d);
      return !a
    },
    q = function (a, g, c) {
      return a.each(function () {
        var a = this._jqm;
        b(g).each(function () {
          this[c] || (this[c] = [], b(this).click(function () {
            for (var a in {
                jqmShow: 1,
                jqmHide: 1
              })
              for (var b in this[a])
                if (k[this[a][b]]) k[this[a][b]].w[a](this);
            return d
          }));
          this[c].push(a)
        })
      })
    }
})(jQuery);
(function (b) {
  b.fn.jqDrag = function (a) {
    return f(this, a, "d")
  };
  b.fn.jqResize = function (a) {
    return f(this, a, "r")
  };
  b.jqDnR = {
    dnr: {},
    e: 0,
    drag: function (b) {
      "d" == d.k ? a.css({
        left: d.X + b.pageX - d.pX,
        top: d.Y + b.pageY - d.pY
      }) : a.css({
        width: Math.max(b.pageX - d.pX + d.W, 0),
        height: Math.max(b.pageY - d.pY + d.H, 0)
      });
      return !1
    },
    stop: function () {
      a.css("opacity", d.o);
      b(document).unbind("mousemove", c.drag).unbind("mouseup", c.stop)
    }
  };
  var c = b.jqDnR,
    d = c.dnr,
    a = c.e,
    f = function (c, e, f) {
      return c.each(function () {
        e = e ? b(e, c) : c;
        e.bind("mousedown", {
          e: c,
          k: f
        }, function (c) {
          var f = c.data,
            e = {};
          a = f.e;
          if ("relative" != a.css("position")) try {
            a.position(e)
          } catch (g) {}
          d = {
            X: e.left || parseInt(a.css("left")) || !1 || 0,
            Y: e.top || parseInt(a.css("top")) || !1 || 0,
            W: parseInt(a.css("width")) || !1 || a[0].scrollWidth || 0,
            H: parseInt(a.css("height")) || !1 || a[0].scrollHeight || 0,
            pX: c.pageX,
            pY: c.pageY,
            k: f.k,
            o: a.css("opacity")
          };
          a.css({
            opacity: 0.6
          });
          b(document).mousemove(b.jqDnR.drag).mouseup(b.jqDnR.stop);
          return !1
        })
      })
    }
})(jQuery);
(function () {
  var e, k, l, h;
  e = jQuery;
  k = function () {
    function a(b, c, a) {
      this.row = b;
      this.tree = c;
      this.settings = a;
      this.id = this.row.data(this.settings.nodeIdAttr);
      b = this.row.data(this.settings.parentIdAttr);
      null != b && "" !== b && (this.parentId = b);
      this.treeCell = e(this.row.children(this.settings.columnElType)[this.settings.column]);
      this.expander = e(this.settings.expanderTemplate);
      this.indenter = e(this.settings.indenterTemplate);
      this.children = [];
      this.initialized = !1;
      this.treeCell.prepend(this.indenter)
    }
    a.prototype.addChild = function (b) {
      return this.children.push(b)
    };
    a.prototype.ancestors = function () {
      var b, c;
      c = this;
      for (b = []; c = c.parentNode();) b.push(c);
      return b
    };
    a.prototype.collapse = function () {
      this._hideChildren();
      this.row.removeClass("expanded").addClass("collapsed");
      this.expander.attr("title", this.settings.stringExpand);
      this.initialized && null != this.settings.onNodeCollapse && this.settings.onNodeCollapse.apply(this);
      return this
    };
    a.prototype.expand = function () {
      this.initialized && null != this.settings.onNodeExpand && this.settings.onNodeExpand.apply(this);
      this.row.removeClass("collapsed").addClass("expanded");
      this._showChildren();
      this.expander.attr("title", this.settings.stringCollapse);
      return this
    };
    a.prototype.expanded = function () {
      return this.row.hasClass("expanded")
    };
    a.prototype.hide = function () {
      this._hideChildren();
      this.row.hide();
      return this
    };
    a.prototype.isBranchNode = function () {
      return 0 < this.children.length || !0 === this.row.data(this.settings.branchAttr) ? !0 : !1
    };
    a.prototype.level = function () {
      return this.ancestors().length
    };
    a.prototype.parentNode = function () {
      return null != this.parentId ? this.tree[this.parentId] : null
    };
    a.prototype.removeChild = function (b) {
      b = e.inArray(b, this.children);
      return this.children.splice(b, 1)
    };
    a.prototype.render = function () {
      var b = this.settings,
        c;
      !0 === b.expandable && this.isBranchNode() && (this.indenter.html(this.expander), c = !0 === b.clickableNodeNames ? this.treeCell : this.expander, c.unbind("click.treetable").bind("click.treetable", function (c) {
        e(this).parents("table").treetable("node", e(this).parents("tr").data(b.nodeIdAttr)).toggle();
        c.stopPropagation();
        return c.preventDefault()
      }));
      !0 === b.expandable && "collapsed" === b.initialState ? this.collapse() : this.expand();
      this.indenter[0].style.paddingLeft = "" + this.level() * b.indent + "px";
      return this
    };
    a.prototype.reveal = function () {
      null != this.parentId && this.parentNode().reveal();
      return this.expand()
    };
    a.prototype.setParent = function (b) {
      null != this.parentId && this.tree[this.parentId].removeChild(this);
      this.parentId = b.id;
      this.row.data(this.settings.parentIdAttr, b.id);
      return b.addChild(this)
    };
    a.prototype.show = function () {
      this.initialized || this._initialize();
      this.row.show();
      this.expanded() && this._showChildren();
      return this
    };
    a.prototype.toggle = function () {
      this.expanded() ? this.collapse() : this.expand();
      return this
    };
    a.prototype._hideChildren = function () {
      var b, c, a, d, f;
      d = this.children;
      f = [];
      c = 0;
      for (a = d.length; c < a; c++) b = d[c], f.push(b.hide());
      return f
    };
    a.prototype._initialize = function () {
      this.render();
      null != this.settings.onNodeInitialized && this.settings.onNodeInitialized.apply(this);
      return this.initialized = !0
    };
    a.prototype._showChildren = function () {
      var b,
        c, a, d, f;
      d = this.children;
      f = [];
      c = 0;
      for (a = d.length; c < a; c++) b = d[c], f.push(b.show());
      return f
    };
    return a
  }();
  l = function () {
    function a(b, c) {
      this.table = b;
      this.settings = c;
      this.tree = {};
      this.nodes = [];
      this.roots = []
    }
    a.prototype.collapseAll = function () {
      var b, c, a, d, f;
      d = this.nodes;
      f = [];
      c = 0;
      for (a = d.length; c < a; c++) b = d[c], f.push(b.collapse());
      return f
    };
    a.prototype.expandAll = function () {
      var b, c, a, d, f;
      d = this.nodes;
      f = [];
      c = 0;
      for (a = d.length; c < a; c++) b = d[c], f.push(b.expand());
      return f
    };
    a.prototype.loadRows = function (b) {
      var c, a;
      if (null != b)
        for (a = 0; a < b.length; a++) c = e(b[a]), null != c.data(this.settings.nodeIdAttr) && (c = new k(c, this.tree, this.settings), this.nodes.push(c), this.tree[c.id] = c, null != c.parentId ? this.tree[c.parentId].addChild(c) : this.roots.push(c));
      return this
    };
    a.prototype.move = function (b, a) {
      b !== a && (a.id !== b.parentId && -1 === e.inArray(b, a.ancestors())) && (b.setParent(a), this._moveRows(b, a), 1 === b.parentNode().children.length && b.parentNode().render());
      return this
    };
    a.prototype.render = function () {
      var b, a, g, d;
      d = this.roots;
      a = 0;
      for (g = d.length; a < g; a++) b = d[a], b.show();
      return this
    };
    a.prototype._moveRows = function (b, a) {
      var g, d, f, e, h;
      b.row.insertAfter(a.row);
      b.render();
      e = b.children;
      h = [];
      d = 0;
      for (f = e.length; d < f; d++) g = e[d], h.push(this._moveRows(g, b));
      return h
    };
    a.prototype.unloadBranch = function (a) {
      var c, g;
      for (g = 0; g < a.children.length; g++) c = a.children[g], this.unloadBranch(c), c.row.remove(), delete this.tree[c.id], this.nodes.splice(e.inArray(c, this.nodes), 1);
      a.children = [];
      return this
    };
    return a
  }();
  h = {
    init: function (a) {
      var b;
      b = e.extend({
        branchAttr: "ttBranch",
        clickableNodeNames: !1,
        column: 0,
        columnElType: "td",
        expandable: !1,
        expanderTemplate: "<a href='#'>&nbsp;</a>",
        indent: 19,
        indenterTemplate: "<span class='indenter'></span>",
        initialState: "collapsed",
        nodeIdAttr: "ttId",
        parentIdAttr: "ttParentId",
        stringExpand: "Expand",
        stringCollapse: "Collapse",
        onInitialized: null,
        onNodeCollapse: null,
        onNodeExpand: null,
        onNodeInitialized: null
      }, a);
      return this.each(function () {
        var a, g;
        g = new l(this, b);
        g.loadRows(this.rows).render();
        a = e(this).addClass("treetable").data("treetable", g);
        null != b.onInitialized && b.onInitialized.apply(g);
        return a
      })
    },
    destroy: function () {
      return this.each(function () {
        return e(this).removeData("treetable").removeClass("treetable")
      })
    },
    collapseAll: function () {
      this.data("treetable").collapseAll();
      return this
    },
    collapseNode: function (a) {
      var b = this.data("treetable").tree[a];
      if (b) b.collapse();
      else throw Error("Unknown node '" + a + "'");
      return this
    },
    expandAll: function () {
      this.data("treetable").expandAll();
      return this
    },
    expandNode: function (a) {
      var b = this.data("treetable").tree[a];
      if (b) b.expand();
      else throw Error("Unknown node '" + a + "'");
      return this
    },
    loadBranch: function (a, b) {
      b = e(b);
      b.insertAfter(a.row);
      this.data("treetable").loadRows(b);
      return this
    },
    move: function (a, b) {
      var c, e;
      e = this.data("treetable").tree[a];
      c = this.data("treetable").tree[b];
      this.data("treetable").move(e, c);
      return this
    },
    node: function (a) {
      return this.data("treetable").tree[a]
    },
    reveal: function (a) {
      var b = this.data("treetable").tree[a];
      if (b) b.reveal();
      else throw Error("Unknown node '" + a + "'");
      return this
    },
    unloadBranch: function (a) {
      this.data("treetable").unloadBranch(a);
      return this
    }
  };
  e.fn.treetable = function (a) {
    return h[a] ? h[a].apply(this, Array.prototype.slice.call(arguments, 1)) : "object" === typeof a || !a ? h.init.apply(this, arguments) : e.error("Method " + a + " does not exist on jQuery.treetable")
  };
  this.TreeTable || (this.TreeTable = {});
  this.TreeTable.Node = k;
  this.TreeTable.Tree = l
}).call(this);
jQuery.fn.highlightFade = function (a) {
  var b = a && a.constructor == String ? {
      start: a
    } : a || {},
    c = jQuery.highlightFade.defaults,
    e = b.interval || c.interval,
    d = b.attr || c.attr;
  a = {
    linear: function (a, b, c, d) {
      return parseInt(a + d / c * (b - a))
    },
    sinusoidal: function (a, b, c, d) {
      return parseInt(a + Math.sin(90 * (d / c) * (Math.PI / 180)) * (b - a))
    },
    exponential: function (a, b, c, d) {
      return parseInt(a + Math.pow(d / c, 2) * (b - a))
    }
  };
  var f = b.iterator && b.iterator.constructor == Function ? b.iterator : a[b.iterator] || a[c.iterator] || a.linear;
  c.iterator && c.iterator.constructor == Function && (f = c.iterator);
  return this.each(function () {
    this.highlighting || (this.highlighting = {});
    var a = this.highlighting[d] ? this.highlighting[d].end : jQuery.highlightFade.getBaseValue(this, d) || [255, 255, 255],
      k = jQuery.highlightFade.getRGB(b.start || b.colour || b.color || c.start || [255, 255, 128]),
      l = jQuery.speed(b.speed || c.speed),
      g = b["final"] || this.highlighting[d] && this.highlighting[d].orig ? this.highlighting[d].orig : jQuery.css(this, d);
    if (b.end || c.end) g = jQuery.highlightFade.asRGBString(a = jQuery.highlightFade.getRGB(b.end || c.end));
    "undefined" != typeof b["final"] && (g = b["final"]);
    this.highlighting[d] && this.highlighting[d].timer && window.clearInterval(this.highlighting[d].timer);
    this.highlighting[d] = {
      steps: l.duration / e,
      interval: e,
      currentStep: 0,
      start: k,
      end: a,
      orig: g,
      attr: d
    };
    jQuery.highlightFade(this, d, b.complete, f)
  })
};
jQuery.highlightFade = function (a, b, c, e) {
  a.highlighting[b].timer = window.setInterval(function () {
    var d = e(a.highlighting[b].start[0], a.highlighting[b].end[0], a.highlighting[b].steps, a.highlighting[b].currentStep),
      f = e(a.highlighting[b].start[1], a.highlighting[b].end[1], a.highlighting[b].steps, a.highlighting[b].currentStep),
      h = e(a.highlighting[b].start[2], a.highlighting[b].end[2], a.highlighting[b].steps, a.highlighting[b].currentStep);
    jQuery(a).css(b, jQuery.highlightFade.asRGBString([d, f, h]));
    a.highlighting[b].currentStep++ >= a.highlighting[b].steps && (jQuery(a).css(b, a.highlighting[b].orig || ""), window.clearInterval(a.highlighting[b].timer), a.highlighting[b] = null, c && c.constructor == Function && c.call(a))
  }, a.highlighting[b].interval)
};
jQuery.highlightFade.defaults = {
  start: [255, 255, 128],
  interval: 50,
  speed: 1500,
  attr: "backgroundColor"
};
jQuery.highlightFade.getRGB = function (a, b) {
  var c;
  return a && a.constructor == Array && 3 == a.length ? a : (c = /rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)/.exec(a)) ? [parseInt(c[1]), parseInt(c[2]), parseInt(c[3])] : (c = /rgb\(\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*\)/.exec(a)) ? [2.55 * parseFloat(c[1]), 2.55 * parseFloat(c[2]), 2.55 * parseFloat(c[3])] : (c = /#([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})/.exec(a)) ? [parseInt("0x" + c[1]), parseInt("0x" + c[2]),
    parseInt("0x" + c[3])
  ] : (c = /#([a-fA-F0-9])([a-fA-F0-9])([a-fA-F0-9])/.exec(a)) ? [parseInt("0x" + c[1] + c[1]), parseInt("0x" + c[2] + c[2]), parseInt("0x" + c[3] + c[3])] : jQuery.highlightFade.checkColorName(a) || b || null
};
jQuery.highlightFade.asRGBString = function (a) {
  return "rgb(" + a.join(",") + ")"
};
jQuery.highlightFade.getBaseValue = function (a, b, c) {
  var e, d;
  c = c || !1;
  d = b = b || jQuery.highlightFade.defaults.attr;
  do {
    e = jQuery(a).css(d || "backgroundColor");
    if ("" != e && "transparent" != e || "body" == a.tagName.toLowerCase() || !c && a.highlighting && a.highlighting[b] && a.highlighting[b].end) break;
    d = !1
  } while (a = a.parentNode);
  !c && (a.highlighting && a.highlighting[b] && a.highlighting[b].end) && (e = a.highlighting[b].end);
  if (void 0 == e || "" == e || "transparent" == e) e = [255, 255, 255];
  return jQuery.highlightFade.getRGB(e)
};
jQuery.highlightFade.checkColorName = function (a) {
  if (!a) return null;
  switch (a.replace(/^\s*|\s*$/g, "").toLowerCase()) {
  case "aqua":
    return [0, 255, 255];
  case "black":
    return [0, 0, 0];
  case "blue":
    return [0, 0, 255];
  case "fuchsia":
    return [255, 0, 255];
  case "gray":
    return [128, 128, 128];
  case "green":
    return [0, 128, 0];
  case "lime":
    return [0, 255, 0];
  case "maroon":
    return [128, 0, 0];
  case "navy":
    return [0, 0, 128];
  case "olive":
    return [128, 128, 0];
  case "purple":
    return [128, 0, 128];
  case "red":
    return [255, 0, 0];
  case "silver":
    return [192, 192, 192];
  case "teal":
    return [0, 128, 128];
  case "white":
    return [255, 255, 255];
  case "yellow":
    return [255, 255, 0]
  }
};
(function (f) {
  function h(b) {
    return "object" == typeof b ? b : {
      top: b,
      left: b
    }
  }
  var k = f.scrollTo = function (b, g, a) {
    f(window).scrollTo(b, g, a)
  };
  k.defaults = {
    axis: "xy",
    duration: 1.3 <= parseFloat(f.fn.jquery) ? 0 : 1
  };
  k.window = function (b) {
    return f(window).scrollable()
  };
  f.fn.scrollable = function () {
    return this.map(function () {
      if (this.nodeName && -1 == f.inArray(this.nodeName.toLowerCase(), ["iframe", "#document", "html", "body"])) return this;
      var b = (this.contentWindow || this).document || this.ownerDocument || this;
      return "BackCompat" == b.compatMode ? b.body : b.documentElement
    })
  };
  f.fn.scrollTo = function (b, g, a) {
    "object" == typeof g && (a = g, g = 0);
    "function" == typeof a && (a = {
      onAfter: a
    });
    "max" == b && (b = 9E9);
    a = f.extend({}, k.defaults, a);
    g = g || a.speed || a.duration;
    a.queue = a.queue && 1 < a.axis.length;
    a.queue && (g /= 2);
    a.offset = h(a.offset);
    a.over = h(a.over);
    return this.scrollable().each(function () {
      function k(d) {
        n.animate(c, g, a.easing, d && function () {
          d.call(this, b, a)
        })
      }

      function s(a) {
        var c = "scroll" + a;
        if (!q) return m[c];
        a = "client" + a;
        var d = m.ownerDocument.documentElement,
          b = m.ownerDocument.body;
        return Math.max(d[c], b[c]) - Math.min(d[a], b[a])
      }
      var m = this,
        n = f(m),
        d = b,
        p, c = {},
        q = n.is("html,body");
      switch (typeof d) {
      case "number":
      case "string":
        if (/^([+-]=)?\d+(\.\d+)?(px)?$/.test(d)) {
          d = h(d);
          break
        }
        d = f(d, this);
      case "object":
        if (d.is || d.style) p = (d = f(d)).offset()
      }
      f.each(a.axis.split(""), function (b, f) {
        var g = "x" == f ? "Left" : "Top",
          l = g.toLowerCase(),
          e = "scroll" + g,
          h = m[e],
          r = "x" == f ? "Width" : "Height";
        p ? (c[e] = p[l] + (q ? 0 : h - n.offset()[l]), a.margin && (c[e] -= parseInt(d.css("margin" + g)) || 0, c[e] -= parseInt(d.css("border" + g + "Width")) || 0), c[e] += a.offset[l] || 0, a.over[l] && (c[e] += d[r.toLowerCase()]() * a.over[l])) : c[e] = d[l];
        /^\d+$/.test(c[e]) && (c[e] = 0 >= c[e] ? 0 : Math.min(c[e], s(r)));
        !b && a.queue && (h != c[e] && k(a.onAfterFirst), delete c[e])
      });
      k(a.onAfter)
    }).end()
  }
})(jQuery);
var TlibHeaderFixedTable = function () {};
TlibHeaderFixedTable.prototype = {
  _header_rows: 0,
  _header_cols: 0,
  _table_div: "TlibTable",
  _table_header_div: "TlibFixedTableHeader",
  _table_header_div_col: "",
  _table_header_div_hd: "",
  _table_height: 0,
  _table_height_calc: "",
  _td_adjust: 0,
  _td_adjust_y: 0,
  _td_adjust_hd: 0,
  _td_adjust_hd_y: 3,
  _th_adjust_cospan: 9,
  _browser: "",
  _no_resize_bind: "",
  _ie_backcompat_width: "97%",
  _tr_bg_color: "",
  _adjust_right_table_tr_height: !1,
  _last_child_td_right_color: !1,
  _clientHeight: 0,
  _uuid: "",
  _onResizeFunc: void 0,
  _generateUUID: function () {
    var a = (new Date).getTime();
    "undefined" !== typeof performance && "function" === typeof performance.now && (a += performance.now());
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (b) {
      var c = (a + 16 * Math.random()) % 16 | 0;
      a = Math.floor(a / 16);
      return ("x" === b ? c : c & 3 | 8).toString(16)
    })
  },
  _setTop: function (a, b) {
    a.style.top = b + "px"
  },
  _setLeft: function (a, b) {
    a.style.left = b + "px"
  },
  _setHeight: function (a, b) {
    0 > b || (a.style.height = b + "px")
  },
  _setWidth: function (a, b) {
    0 > b || (a.style.width = b + "px")
  },
  _getBrowser: function () {
    var a = window.navigator.userAgent.toLowerCase();
    return -1 != a.indexOf("opera") ? "opera" : -1 != a.indexOf("msie") ? "ie" : -1 != a.indexOf("trident/7.0") ? "ie11" : -1 != a.indexOf("chrome") ? "chrome" : -1 != a.indexOf("safari") ? "safari" : -1 != a.indexOf("gecko") ? "gecko" : !1
  },
  _isIE6: function () {
    return "undefined" != typeof document.documentElement.style.maxHeight ? !1 : !0
  },
  _elem: function (a) {
    return document.all ? document.all(a) : document.getElementById(a)
  },
  _calc_header_rows: function () {
    var a = this._elem(this._table_div).getElementsByTagName("TABLE")[0].getElementsByTagName("TR"),
      b = this._header_rows = 0;
    for (this._header_rows = 0; b < a.length && !(ths = a[b].getElementsByTagName("TH"), 0 === ths.length); b++, this._header_rows++);
    return this._header_rows === a.length ? !1 : !0
  },
  _createTableHeader: function () {
    var a = this._elem(this._table_div);
    a.className = "TlibFixedHeaderTableDiv";
    var b = a.getElementsByTagName("TABLE")[0],
      c = b.style;
    b.className = (b.className || "") + " TlibFixedHeaderTable";
    c.width = "100%";
    var h = b.getElementsByTagName("TR"),
      g = document.createDocumentFragment(),
      f = document.createElement("div");
    f.id = this._table_header_div;
    f.className = "TlibFixedHeaderTableDivTop";
    f.style.zIndex = 110;
    g.appendChild(f);
    var e = document.createElement("table"),
      l = e.style;
    e.className = b.className;
    l.width = "100%";
    f.appendChild(e);
    "ie" === this._browser && ("BackCompat" !== document.compatMode && 7 === document.documentMode) && (c.width = this._ie_backcompat_width, l.width = this._ie_backcompat_width);
    b = document.createElement("thead");
    e.appendChild(b);
    for (var k, d, m, n = document.createElement("tr"), p = document.createElement("div"), e = 0; e < this._header_rows; e++) {
      f = n.cloneNode(!1);
      f.style.height = h[e].style.height;
      b.appendChild(f);
      k = h[e].getElementsByTagName("TH");
      for (c = 0; c < k.length; c++) d = k[c].cloneNode(!0), 1 < this._header_rows && (m = p.cloneNode(!1), d.appendChild(m)), f.appendChild(d)
    }
    l.tableLayout = "fixed";
    a.parentNode.insertBefore(g, a)
  },
  _createTableHeaderCol: function () {
    if (0 !== this._header_cols) {
      this._table_header_div_col = this._table_header_div + "_COL";
      this._table_header_div_hd = this._table_header_div + "_HD";
      var a = this._elem(this._table_div),
        b = a.getElementsByTagName("TABLE")[0],
        c = b.getElementsByTagName("TR"),
        h = this._elem(this._table_header_div),
        g = h.getElementsByTagName("TABLE")[0];
      g.getElementsByTagName("TR");
      var f = document.createDocumentFragment(),
        e = document.createDocumentFragment(),
        l = document.createElement("div"),
        k = l.style;
      l.id = this._table_header_div_col;
      l.className = "TlibFixedHeaderTableDivCol";
      k.position = "absolute";
      k.zIndex = 111;
      f.appendChild(l);
      var d = document.createElement("div"),
        k = d.style;
      d.id = this._table_header_div_hd;
      d.className = "TlibFixedHeaderTableDivCol";
      k.position = "absolute";
      k.zIndex = 112;
      e.appendChild(d);
      var k = document.createElement("table"),
        m = k.style;
      k.className = b.className;
      m.position = "relative";
      l.appendChild(k);
      var n = document.createElement("thead");
      k.appendChild(n);
      l = document.createElement("tbody");
      k.appendChild(l);
      var p = document.createElement("table"),
        t = p.style;
      p.className = b.className;
      t.position = "relative";
      d.appendChild(p);
      var s = document.createElement("thead");
      p.appendChild(s);
      for (var q, r, w, v, u, y = this._header_rows, z = this._header_cols, A = [], x = document.createElement("tr"),
          d = 0; d < y; d++) {
        r = x.cloneNode(!1);
        n.appendChild(r);
        w = x.cloneNode(!1);
        s.appendChild(w);
        v = c[d].getElementsByTagName("TH");
        for (q = 0; q < z; q++) {
          u = v[q].rowSpan;
          if (0 === d) A[q] = u === y ? !1 : !0;
          else if (!A[q]) continue;
          u = v[q].cloneNode(!0);
          r.appendChild(u);
          u = v[q].cloneNode(!0);
          w.appendChild(u)
        }
      }
      for (; d < c.length; d++) {
        r = x.cloneNode(!1);
        l.appendChild(r);
        c[d].id && (r.id = c[d].id + "_col");
        c[d].title && (r.title = c[d].title);
        r.className = c[d].className;
        n = c[d].getElementsByTagName("TD");
        for (q = 0; q < z; q++) s = n[q].cloneNode(!0), r.appendChild(s)
      }
      m.tableLayout = "fixed";
      t.tableLayout = "fixed";
      if ("collapse" !== (b.currentStyle || document.defaultView.getComputedStyle(b, "")).borderCollapse) this._addClass(b, "TlibFixedColTableRight"), this._addClass(g, "TlibFixedColTableRight");
      this._addClass(k, "TlibFixedColTableLeft");
      this._addClass(p, "TlibFixedColTableLeft");
      a.parentNode.insertBefore(f, a);
      a.parentNode.insertBefore(e, h)
    }
  },
  _adjustTableWidth: function () {
    var a = this._elem(this._table_div),
      b = a.getElementsByTagName("TABLE")[0].getElementsByTagName("TR"),
      c = this._elem(this._table_header_div),
      h = c.getElementsByTagName("TABLE")[0].getElementsByTagName("TR"),
      g = this._header_rows,
      f, e, l = [],
      k = [],
      d, m, n;
    for (f = 0; f < g; f++) {
      d = b[f].getElementsByTagName("TH");
      m = d.length;
      k = [];
      for (e = 0; e < m; e++) k[e] = d[e].offsetWidth - this._td_adjust_hd;
      l[f] = k
    }
    for (f = 0; f < g; f++) {
      b = h[f].getElementsByTagName("TH");
      m = b.length;
      k = l[f];
      for (e = 0; e < m; e++) d = b[e], n = d.colSpan, 1 < n ? this._setWidth(d, k[e] - 2 * (n - 1)) : this._setWidth(d, k[e])
    }
    if (0 < this._header_cols) {
      h = this._elem(this._table_header_div_col).getElementsByTagName("TABLE")[0];
      b = h.getElementsByTagName("TR");
      d = this._elem(this._table_header_div_hd).getElementsByTagName("TABLE")[0];
      n = d.getElementsByTagName("TR");
      var p, t, s = 0;
      for (f = 0; f < g; f++)
        if (p = b[f].getElementsByTagName("TH"), t = n[f].getElementsByTagName("TH"), 0 !== t.length) {
          k = l[f];
          m = p.length;
          for (e = 0; e < m; e++) 0 === f && (s += k[e]), this._setWidth(p[e], k[e]), this._setWidth(t[e], k[e])
        }
      this._setWidth(h, s + 1);
      this._setWidth(d, s + 1)
    }
    "gecko" === this._browser && (c.style.overflowY = "hidden", this._setWidth(c, a.clientWidth))
  },
  _adjustTableHeight: function () {
    var a = this._elem(this._table_div),
      b = a.getElementsByTagName("TABLE")[0],
      c = b.getElementsByTagName("TR"),
      h = this._elem(this._table_header_div),
      g = h.getElementsByTagName("TABLE")[0];
    g.getElementsByTagName("TR");
    var f = this._header_rows,
      e = this._header_cols,
      l = c.length,
      k = [],
      d, m, n, p, t;
    p = "ie" === this._browser || "ie11" === this._browser ? document.documentElement.clientHeight || document.body.clientHeight : window.innerHeight;
    t = a.offsetTop;
    if (0 < e) {
      for (d = 0; d < l; d++) k[d] = c[d].offsetHeight;
      m = this._elem(this._table_header_div_col);
      n = m.getElementsByTagName("TABLE")[0];
      var s = n.getElementsByTagName("TR"),
        q = this._elem(this._table_header_div_hd).getElementsByTagName("TABLE")[0].getElementsByTagName("TR"),
        r;
      for (d = 0; d < l; d++) r = k[d], d < f && this._setHeight(q[d], r), this._setHeight(s[d], r), this._adjust_right_table_tr_height && this._setHeight(c[d], r)
    }
    c = -c[f].offsetTop;
    this._setHeight(h, g.offsetHeight);
    this._setTop(b, c);
    this._setHeight(a, -1 === this._table_height ? a.parentNode.offsetHeight - a.offsetTop : 0 < this._table_height ? this._table_height : "ie" === this._browser || "ie11" === this._browser ? p - t - 2 : p - t - 15);
    0 < e && (this._setTop(n, c), this._setHeight(m, a.clientHeight))
  },
  _adjustTableSize: function () {
    if (!(0 >= this._header_rows)) {
      var a = this._elem(this._table_div);
      a && (a = a.getElementsByTagName("TABLE")[0].getElementsByTagName("TR"), this._elem(this._table_header_div) && !(a.length <= this._header_rows) && (this._adjustTableWidth(), this._adjustTableHeight()))
    }
  },
  adjustTableSize: function () {
    this._adjustTableSize()
  },
  _onResizeWindow: function () {
    var a = this._elem(this._table_div);
    a && this._uuid !== a.getAttribute("uuid") ? (this._onResizeFunc && (window.addEventListener ? window.removeEventListener("resize", this._onResizeFunc, !1) : window.detachEvent("onresize", this._onResizeFunc)), this._onResizeFunc = void 0) : (this.adjustTableSize(), this._adjustScroll())
  },
  _adjustScroll: function () {
    var a = this._elem(this._table_header_div);
    if (a) {
      var b = this._elem(this._table_div);
      a.scrollLeft = b.scrollLeft;
      0 < this._header_cols && (this._elem(this._table_header_div_col).scrollTop = b.scrollTop)
    }
  },
  _onScrollTable: function () {
    this._adjustScroll()
  },
  _hasClass: function (a, b) {
    return a.className.match(RegExp("(\\s|^)" + b + "(\\s|$)"))
  },
  _addClass: function (a, b) {
    if (!this._hasClass(a, b)) {
      var c = a.className || "";
      "" !== c && (c += " ");
      a.className = c + b
    }
  },
  _removeClass: function (a, b) {
    this._hasClass(a, b) && (a.className = a.className.replace(RegExp("(\\s|^)" + b + "(\\s|$)"), " ").replace(/^\s/, ""))
  },
  _onMouseOver: function (a, b) {
    var c = this._elem(this._table_div),
      h = this._elem(this._table_header_div_col),
      c = c.getElementsByTagName("TABLE")[0],
      g = c.getElementsByTagName("THEAD"),
      h = h.getElementsByTagName("TABLE")[0],
      g = 1 === b && 0 === g.length ? a.sectionRowIndex : this._header_rows + a.sectionRowIndex;
    g < this._header_rows || (c = 1 === b ? h.getElementsByTagName("TR") : c.getElementsByTagName("TR"), this._addClass(c[g], "TlibFixedHeaderTableHover"), this._addClass(a, "TlibFixedHeaderTableHover"))
  },
  _onMouseOut: function (a, b) {
    var c = this._elem(this._table_div),
      h = this._elem(this._table_header_div_col),
      c = c.getElementsByTagName("TABLE")[0],
      g = c.getElementsByTagName("THEAD"),
      h = h.getElementsByTagName("TABLE")[0],
      g = 1 === b && 0 === g.length ? a.sectionRowIndex : this._header_rows + a.sectionRowIndex;
    g < this._header_rows || (c = 1 === b ? h.getElementsByTagName("TR") : c.getElementsByTagName("TR"), this._removeClass(c[g], "TlibFixedHeaderTableHover"), this._removeClass(a, "TlibFixedHeaderTableHover"))
  },
  _onHoverTable: function () {
    var a = this,
      b = this._elem(this._table_div).getElementsByTagName("TABLE")[0].getElementsByTagName("TR"),
      c = this._elem(this._table_header_div_col).getElementsByTagName("TABLE")[0].getElementsByTagName("TR"),
      h, g, f, e = c.length;
    for (h = this._header_rows; h < e; h++) f = c[h], g = b[h], window.addEventListener ? (g.addEventListener("mouseover", function () {
      a._onMouseOver(this, 1)
    }, !1), f.addEventListener("mouseover", function () {
      a._onMouseOver(this, 2)
    }, !1), g.addEventListener("mouseout", function () {
      a._onMouseOut(this, 1)
    }, !1), f.addEventListener("mouseout", function () {
      a._onMouseOut(this, 2)
    }, !1)) : (g.onmouseover = function () {
      a._onMouseOver(this, 1)
    }, f.onmouseover = function () {
      a._onMouseOver(this, 2)
    }, g.onmouseout = function () {
      a._onMouseOut(this, 1)
    }, f.onmouseout = function () {
      a._onMouseOut(this, 2)
    })
  },
  _onWheelFixedCol: function (a) {
    var b = 0;
    a.wheelDelta ? b = a.wheelDelta / 2 : 1 === a.deltaMode && (b = -(20 * a.deltaY));
    a.preventDefault();
    0 !== b && (a = this._elem(this._table_div), a.scrollTop -= b, this._adjustScroll())
  },
  _onKeydownFixedCol: function (a) {
    var b, c = 0,
      h = this._elem(this._table_header_div_col),
      g = h.getElementsByTagName("TABLE")[0].getElementsByTagName("TR"),
      f = g.length < this._header_rows + 3 ? g.length : this._header_rows + 3,
      e = 0;
    for (b = this._header_rows; b < f; b++) e += g[b].offsetHeight - 2;
    b = h.offsetHeight - e;
    switch (a.which) {
    case 33:
      c = b;
      break;
    case 34:
      c = -b;
      break;
    case 38:
      c = e;
      break;
    case 40:
      c = -e
    }
    a.preventDefault();
    0 !== c && (a = this._elem(this._table_div), a.scrollTop -= c, this._adjustScroll());
    return !1
  },
  _addCSSRule: function (a, b, c) {
    a.insertRule ? a.insertRule(b + "{" + c + "}", a.cssRules.length) : a.addRule && a.addRule(b, c)
  },
  _bindEvent: function () {
    var a = this,
      b = this._elem(this._table_div);
    this._no_resize_bind || (this._onResizeFunc = function () {
      a._onResizeWindow()
    }, window.addEventListener ? window.addEventListener("resize", this._onResizeFunc, !1) : window.attachEvent("onresize", this._onResizeFunc));
    window.addEventListener ? b.addEventListener("scroll", function () {
      a._onScrollTable()
    }, !1) : b.onscroll = function () {
      a._onScrollTable()
    };
    0 < this._tr_bg_color.length && 0 < this._header_cols && a._onHoverTable();
    if (0 < this._header_cols) {
      var c = this._elem(this._table_header_div_col);
      c.addEventListener("onwheel" in document ? "wheel" : "onmousewheel" in document ? "mousewheel" : "DOMMouseScroll", function (b) {
        a._onWheelFixedCol(b)
      }, !1);
      b.tabIndex = "112";
      b.addEventListener("keydown", function (b) {
        a._onKeydownFixedCol(b)
      }, !1);
      c.tabIndex = "111";
      c.addEventListener("keydown", function (b) {
        a._onKeydownFixedCol(b)
      }, !1)
    }
  },
  _initCSS: function () {
    if (!this._elem("TlibFixedHeaderTable3_CSS")) {
      var a = document.createElement("style");
      a.setAttribute("type", "text/css");
      a.setAttribute("id", "TlibFixedHeaderTable3_CSS");
      document.getElementsByTagName("head")[0].appendChild(a);
      var a = document.styleSheets[document.styleSheets.length - 1],
        b = "",
        c = "padding: 1px 3px;";
      0 < this._header_cols && (b = "line-height: 1 !important;", c = "padding-left: 3px; padding-right: 3px; padding-top: 4px !important; padding-bottom: 4px !important;");
      this._addCSSRule(a, ".TlibFixedHeaderTableDiv", "position: relative; width: 100%; height: 80%; overflow-x: auto; overflow-y: scroll; ");
      this._addCSSRule(a, ".TlibFixedHeaderTableDivTop", "position: relative; width: 100%; overflow-x: hidden; overflow-y: scroll; scrollbar-face-color: white; scrollbar-shadow-color: white; scrollbar-darkshadow-color: white; scrollbar-3dlight-color: white; scrollbar-arrow-color: white; ");
      this._addCSSRule(a, ".TlibFixedHeaderTableDivCol", "position: relative; overflow-x: hidden; overflow-y: hidden; ");
      this._addCSSRule(a, ".TlibFixedHeaderTable", "margin: 0; padding: 0; border: 1px #444444 solid; background: #ffffff; width: auto; height: auto; " + b);
      this._addCSSRule(a, ".TlibFixedHeaderTable th", "padding-top: 1px; padding-left: 3px; padding-right: 3px; padding-bottom: 2px; ");
      this._addCSSRule(a, ".TlibFixedHeaderTable td", c + " border-bottom: 1px solid #999999; ");
      this._addCSSRule(a, ".TlibFixedHeaderTable td.last", "border-bottom: 3px double #666666; ");
      this._addCSSRule(a, ".TlibFixedHeaderTableDivTop *", "-webkit-box-sizing: border-box; -moz-box-sizing: border-box; -o-box-sizing: border-box; -ms-box-sizing: border-box; box-sizing:border-box; ");
      this._addCSSRule(a, ".TlibFixedHeaderTableDivCol *", "-webkit-box-sizing: border-box; -moz-box-sizing: border-box; -o-box-sizing: border-box; -ms-box-sizing: border-box; box-sizing:border-box; ");
      this._addCSSRule(a, ".TlibFixedColTableRight", "position: relative; left: 3px;");
      this._addCSSRule(a, ".TlibFixedColTableLeft", "border-right: 1px solid #999");
      this._last_child_td_right_color && this._addCSSRule(a, ".TlibFixedHeaderTableDivCol > table td:last-child", "border-right: 1px solid " + this._last_child_td_right_color);
      0 < this._tr_bg_color.length && this._addCSSRule(a, ".TlibFixedHeaderTableHover", "background-color: " + this._tr_bg_color + " !important; ")
    }
  },
  init: function () {
    if (this._calc_header_rows()) {
      this._initCSS();
      this._browser = this._getBrowser();
      "ie" === this._browser ? "BackCompat" === document.compatMode ? this._td_adjust_hd_y = this._td_adjust_hd = this._td_adjust_y = this._td_adjust = 0 : (this._td_adjust = 6, this._isIE6() && (this._td_adjust_hd = 6)) : "gecko" === this._browser ? (this._td_adjust = 6, "BackCompat" === document.compatMode ? (this._td_adjust_y = 3, this._td_adjust_hd_y = 0) : this._td_adjust_hd_y = 3) : "chrome" === this._browser ? (this._td_adjust = 6, "BackCompat" === document.compatMode && (this._td_adjust_hd_y = this._td_adjust_y = 0)) : "safari" === this._browser ? (this._td_adjust = 6, "BackCompat" === document.compatMode && (this._td_adjust_hd_y = this._td_adjust_y = 0)) : "ie11" === this._browser && "BackCompat" === document.compatMode && (this._td_adjust_hd_y = this._td_adjust_hd = this._td_adjust_y = this._td_adjust = 0);
      var a = this._elem(this._table_div);
      this._uuid = this._generateUUID();
      a.setAttribute("uuid", this._uuid);
      a = a.getElementsByTagName("TABLE")[0];
      this._createTableHeader();
      this._createTableHeaderCol();
      a.style.position = "relative";
      this._adjustTableSize();
      this._adjustScroll();
      this._bindEvent()
    }
  },
  scrollTo: function (a) {
    if (a = fixed_table._elem(a)) {
      var b = this._elem(this._table_div),
        c = b.getElementsByTagName("TABLE")[0].getElementsByTagName("TR");
      b.scrollTop = a.offsetTop - c[this._header_rows].offsetTop;
      this._adjustScroll()
    }
  }
};