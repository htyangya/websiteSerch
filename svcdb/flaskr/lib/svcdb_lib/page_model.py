from flaskr.lib.conf.config import Config


class PageModel:
    # プロジェクト全体に画面page数のデフォルトを設定
    display_page_count = 10

    # 初期化のとき、pageは必須です、item_countと一緒にセットしてはいい、後でset_item_countを利用してもいい
    def __init__(self, page, item_count=None, page_size=Config.MAX_PAGE_SIZE, display_page_count=None):
        self.page = max(page, 1)
        self.item_count = item_count
        self.page_size = page_size
        self.begin_item = None
        self.end_item = None
        self.page_count = None
        self.result_list = []
        self.current_pages = []
        if display_page_count:
            self.display_page_count = display_page_count
        if item_count:
            self.set_item_count(item_count)

    def set_item_count(self, item_count):
        self.item_count = item_count
        self.page_count = (item_count + self.page_size - 1) // self.page_size
        self.page = min(self.page, self.page_count)
        self._set_search_param()
        self._set_current_pages()

    def _set_search_param(self):
        self.begin_item = (self.page - 1) * self.page_size + 1
        self.end_item = self.page * self.page_size

    def _set_current_pages(self):
        if self.page_count < self.display_page_count:
            self.current_pages = list(range(1, self.page_count + 1))
        else:
            page_start = max(self.page - (self.display_page_count - 1) // 2, 1)
            page_end = min((page_start + self.display_page_count - 1), self.page_count)
            if page_end == self.page_count:
                page_start = min(page_start, self.page_count - self.display_page_count + 1)
            self.current_pages = list(range(page_start, page_end + 1))
