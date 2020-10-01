(function ($) {
    $.fn.input_selectize = function (url) {
        var input = this.filter(".form-group>input[type='text']:first");
        if (input.nextAll('#_' + input.attr("id")).length) {
            return input
        }
        var select_str = "<select class='form-control input_selectize' id=" + ('_' + input.attr("id")) + " name='" + input.attr("name") + "'>" +
            // "<option value='" + input.val() + "'>" + input.val() +
            // "</option>" +
            " </select>";
        var select = $(select_str).appendTo(input.parent());
        if (url) {
            load_ajax(url,input.val());
        }
        input.addClass("input_selectize").prop("disabled", true).hide();


        function show_input() {
            input.val("");
            select.prop("disabled", true).hide();
            input.prop("disabled", false).show();
            return input
        }

        function show_select() {
            input.prop("disabled", true).hide();
            select.prop("disabled", false).show();
            return input
        }

        function add_item(item) {
            var key, val;
            if (Array.isArray(item)) {
                key = item[0];
                val = item[1];
            } else {
                key = item.toString();
                val = item.toString();
            }
            select.append("<option value='" + key + "'>" + val + "</option>");
            return input
        }

        function add_items(item_list) {
            item_list.forEach(function (item) {
                add_item(item);
            });
            return input
        }

        function clean_and_add(item_list) {
            select.empty();
            add_item(["None", "---"]);
            add_items(item_list);
            return input
        }

        function load_ajax(url,be_set_item) {
            var p = $.get(url).then(function (data) {
                clean_and_add(data);
                show_select();
            });
            if (be_set_item) {
                p.then(function () {
                    set_item(be_set_item);
                })
            }
            return input;
        }

        function set_item(item) {
            select.val(item);
        }

        input.extend({
            show_input: show_input,
            show_select: show_select,
            add_item: add_item,
            add_items: add_items,
            clean_and_add: clean_and_add,
            load_ajax: load_ajax,
            set_item: set_item,
        });
        return input;
    };
})(jQuery);