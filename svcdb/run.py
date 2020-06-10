from flask_login import current_user

from flaskr import create_app
from flaskr.lib.conf.config import Config
from flaskr.lib.conf.const import Const
from flaskr.lib.svcdb_lib.str_util import StrUtil

app = create_app()


@app.context_processor
def svcdb_processor():
    resp_dict = {
        "system_name": Const.SYSTEM_NAME,
        "current_user": current_user,
        "user_name": current_user.get_user_name() if current_user.is_active else "",
        "appVer": Config.APP_VER
    }
    return resp_dict


if __name__ == '__main__':
    app.run(debug=StrUtil.get_safe_config(app, 'DEBUG'))
