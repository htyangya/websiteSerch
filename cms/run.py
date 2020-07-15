from app import create_app
from app.lib.cms_lib.str_util import StrUtil

app = create_app()

if __name__ == '__main__':
    app.run(debug=StrUtil.get_safe_config(app, 'DEBUG'))
