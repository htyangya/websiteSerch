(function(f){function h(b){return"object"==typeof b?b:{top:b,left:b}}var k=f.scrollTo=function(b,g,a){f(window).scrollTo(b,g,a)};k.defaults={axis:"xy",duration:1.3<=parseFloat(f.fn.jquery)?0:1};k.window=function(b){return f(window).scrollable()};f.fn.scrollable=function(){return this.map(function(){if(this.nodeName&&-1==f.inArray(this.nodeName.toLowerCase(),["iframe","#document","html","body"]))return this;var b=(this.contentWindow||this).document||this.ownerDocument||this;return"BackCompat"==b.compatMode?
b.body:b.documentElement})};f.fn.scrollTo=function(b,g,a){"object"==typeof g&&(a=g,g=0);"function"==typeof a&&(a={onAfter:a});"max"==b&&(b=9E9);a=f.extend({},k.defaults,a);g=g||a.speed||a.duration;a.queue=a.queue&&1<a.axis.length;a.queue&&(g/=2);a.offset=h(a.offset);a.over=h(a.over);return this.scrollable().each(function(){function k(d){n.animate(c,g,a.easing,d&&function(){d.call(this,b,a)})}function s(a){var c="scroll"+a;if(!q)return m[c];a="client"+a;var d=m.ownerDocument.documentElement,b=m.ownerDocument.body;
return Math.max(d[c],b[c])-Math.min(d[a],b[a])}var m=this,n=f(m),d=b,p,c={},q=n.is("html,body");switch(typeof d){case "number":case "string":if(/^([+-]=)?\d+(\.\d+)?(px)?$/.test(d)){d=h(d);break}d=f(d,this);case "object":if(d.is||d.style)p=(d=f(d)).offset()}f.each(a.axis.split(""),function(b,f){var g="x"==f?"Left":"Top",l=g.toLowerCase(),e="scroll"+g,h=m[e],r="x"==f?"Width":"Height";p?(c[e]=p[l]+(q?0:h-n.offset()[l]),a.margin&&(c[e]-=parseInt(d.css("margin"+g))||0,c[e]-=parseInt(d.css("border"+g+
"Width"))||0),c[e]+=a.offset[l]||0,a.over[l]&&(c[e]+=d[r.toLowerCase()]()*a.over[l])):c[e]=d[l];/^\d+$/.test(c[e])&&(c[e]=0>=c[e]?0:Math.min(c[e],s(r)));!b&&a.queue&&(h!=c[e]&&k(a.onAfterFirst),delete c[e])});k(a.onAfter)}).end()}})(jQuery);