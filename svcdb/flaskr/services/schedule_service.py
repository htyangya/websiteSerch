import datetime
import json

from flask import render_template, url_for, jsonify
from flask_login import current_user

from flaskr import db
from flaskr.forms.outage_edit_form import OutageEditForm
from flaskr.forms.outage_form import OutageForm
from flaskr.lib.svcdb_lib.db_util import DbUtil
from flaskr.models.svcdb_outage_schedule import OutageSchedule
from flaskr.models.svcdb_turbine_master_table import SvcdbTurbineMasterTable
from flaskr.sql import scheduleSql

# コード対応カラー
COLORMAPPING = {
    "1": "blue",
    "2": "green",
    "3": "red",
    "4": "red",
}


# 各レコードに対応するオブジェクト
class RowObj:

    @staticmethod
    def month_delta(date1, date2):
        return (date2.year - date1.year) * 12 + (date2.month - date1.month)

    # 色をつける処理
    def colour_cells(self, outage_start, outage_end, color_number, teiken_id):
        if color_number != "999" and outage_start and outage_end:
            if outage_start.__class__ == datetime.datetime: outage_start = outage_start.date()
            if outage_end.__class__ == datetime.datetime: outage_end = outage_end.date()
            # print(outage_start, outage_end, color_number)
            cells_start = datetime.date(self.min_year, 1, 1)
            cells_end = datetime.date(self.max_year, 12, 1)
            target_start, target_end = max(outage_start, cells_start), min(outage_end, cells_end)
            index_start, index_end = self.month_delta(cells_start, target_start), self.month_delta(cells_start,
                                                                                                   target_end)
            for index in range(index_start, index_end + 1):
                self.cells[index].color = COLORMAPPING.get(color_number, "gray")
                self.cells[index].teiken_ids.add(teiken_id)

    # セールを初期化
    def set_cells(self):
        for year in range(int(self.min_year), int(self.max_year) + 1):
            for month in range(1, 13):
                self.cells.append(Cell("gray", str(year) + str(month).zfill(2)))

    def __init__(self, plant_cd, plant_name, country_nm, turbine_id, data_type, min_year, max_year, outage_start=None,
                 outage_end=None, color_number=None, teiken_id=None, delete_flg=0, **dict):
        self.plant_cd = plant_cd
        self.plant_name = plant_name
        self.country_nm = country_nm
        self.turbine_id = turbine_id
        self.data_type = data_type
        self.min_year = min_year
        self.max_year = max_year
        self.cells = []
        # セルリストの作成と処理
        self.set_cells()

        if delete_flg == 0:
            self.teiken_id = teiken_id
            self.colour_cells(outage_start, outage_end, color_number, teiken_id)


# 各セールに対応するオブジェクト
class Cell:
    def __init__(self, color, label):
        self.color = color
        self.label = label
        self.teiken_ids = set()

    @property
    def img_src(self):
        return f"static/images/{self.color}.png"

    @property
    def teiken_ids_str(self):
        return json.dumps(list(self.teiken_ids))

    @property
    def length(self):
        return self.teiken_ids.__len__()


# ボータンを押すと
def searching(form, menu_param):
    and_sql = ''
    turbine_id = form.turbine_id.data
    if turbine_id and turbine_id != "None":
        and_sql += f''' AND A.TURBINE_ID = '{turbine_id}' \n'''
    teiken_id = form.teiken_id.data
    if teiken_id and teiken_id != "None":
        and_sql += f''' AND C.TEIKEN_ID = '{teiken_id}' \n'''

    country_cd = form.country.data
    if country_cd and country_cd != "None":
        and_sql += f''' AND TM.MASTER_KIND = 'COUNTRY' \n'''
        and_sql += f''' AND A.COUNTRY_CD = '{country_cd}' \n'''
    plant_cd = form.plant.data
    if plant_cd and plant_cd != "None":
        plant_cd = plant_cd.upper()
        and_sql += f''' AND UPPER(A.KHN_PLANT_CD) LIKE '{plant_cd}%' \n'''
    registered = form.c1.data if hasattr(form, "c1") else None
    if registered and registered != "None":
        date_start = form.date_start.data + "-01-01"
        date_end = form.date_end.data + "-12-31"
        and_sql += f'''AND C.DELETE_FLG = 0 
                AND C.OUTAGE_START <= TO_DATE( '{date_end}', 'yyyy-mm-dd') 
                AND C.OUTAGE_END >= TO_DATE( '{date_start}', 'yyyy-mm-dd')'''

    search_table = "TURBINE_LIST_ESS" if (current_user.corp_cd == 'CNV') else "TURBINE_LIST_EX"
    menu_param["min_year"], menu_param["max_year"] = int(form.date_start.data), int(form.date_end.data)
    menu_param["year_count"] = menu_param["max_year"] - menu_param["min_year"] + 1
    outage_schedule_list = DbUtil.sqlExcuter(scheduleSql.scheduleListSql, search_table=search_table, and_sql=and_sql)
    rows_dict = {}
    for row in outage_schedule_list:
        if row.turbine_id not in rows_dict:
            rows_dict[row.turbine_id] = RowObj(**{k: v for k, v in row.items()},
                                               min_year=menu_param["min_year"],
                                               max_year=menu_param["max_year"])
        elif row.delete_flg == 0:
            rows_dict[row.turbine_id].teiken_id = row.teiken_id
            rows_dict[row.turbine_id].colour_cells(row.outage_start, row.outage_end, row.color_number, row.teiken_id)
    menu_param["outage_schedule_list"] = rows_dict.values()


def show_schedule(request):
    menu_param = {}
    information_message = ""
    template_name = 'outage_schedule.html'
    header_name = 'Outage Schedule'
    form = OutageForm()

    # 初期設定
    # 国
    svcdbTurbineMasterTable = SvcdbTurbineMasterTable()
    rst = svcdbTurbineMasterTable.get_master_list(master_kind='COUNTRY')
    country_dict = [(str(item.code), item.data1) for item in rst]
    form.country.choices = country_dict

    # do search
    if "POST" == request.method and form.validate():
        # do search
        searching(form, menu_param)

    return render_template(
        template_name,
        header_name=header_name,
        title=header_name,
        menu_param=menu_param,
        form=form,
        information_message=information_message,
    )


def open_outage_schedule_jqmodal(request):
    teiken_ids_str = request.form.get("teiken_ids_str")
    teiken_ids = json.loads(teiken_ids_str)
    outageScheduleList = OutageSchedule.query.filter(OutageSchedule.teiken_id.in_(teiken_ids)).all()
    return render_template(
        'outage_schedule_jqmodal.html',
        jqmTitle='予定選択画面',
        outageScheduleList=outageScheduleList)


def open_outage_schedule_detail(request):
    menu_param = {}
    outage = OutageSchedule.query.filter_by(teiken_id=request.args.get("teiken_id")).first()
    form = OutageEditForm(request.args, obj=outage)
    searching(form, menu_param)
    template_name = 'outage_schedule_detail.html'
    header_name = 'Outage Schedule'
    return render_template(
        template_name,
        header_name=header_name,
        title=header_name,
        form=form,
        menu_param=menu_param,
        outage_schedule_info=outage)


def open_outage_schedule_edit(request):
    menu_param = {}
    if request.method == 'POST':
        form = OutageEditForm()
        teiken_id = form.teiken_id.data
        outage = OutageSchedule.query.filter_by(teiken_id=teiken_id).first()
        outage.outage_start = form.outage_start.data or None
        outage.outage_end = form.outage_end.data or None
        outage.outage_type_t = form.outage_type_t.data or None
        outage.outage_type_g = form.outage_type_g.data or None
        outage.execution = form.execution.data or None
        outage.description = form.description.data or None
        outage.outage_duration = form.outage_duration.data or None
        outage.updated_by = current_user.get_id()
        outage.updated_at = datetime.datetime.now()
        db.session.add(outage)
        db.session.commit()
        target_url = url_for("outage_schedule_detail",
                             teiken_id=outage.teiken_id,
                             turbine_id=outage.turbine_id,
                             date_start=form.date_start.data,
                             date_end=form.date_end.data,
                             )
        return jsonify({'url': target_url})
    else:
        teiken_id = request.args.get('teiken_id')
        outage = OutageSchedule.query.filter_by(teiken_id=teiken_id).first()
        form = OutageEditForm(request.args, obj=outage)
        searching(form, menu_param)
    header_name = 'Outage Schedule'
    return render_template(
        'outage_schedule_edit.html',
        header_name=header_name,
        title=header_name,
        form=form,
        menu_param=menu_param)


def open_outage_schedule_add(request):
    menu_param = {}
    if request.method == 'POST':
        form = OutageEditForm()
        outage_model = OutageSchedule(turbine_id=form.turbine_id.data or None,
                                      description=form.description.data or None,
                                      outage_start=form.outage_start.data or None,
                                      outage_end=form.outage_end.data or None,
                                      outage_type_g=form.outage_type_g.data or None,
                                      outage_type_t=form.outage_type_t.data or None,
                                      execution=form.execution.data or None,
                                      outage_duration=form.outage_duration.data or None
                                      )
        db.session.add(outage_model)
        db.session.commit()
        target_url = url_for("outage_schedule_detail",
                             teiken_id=outage_model.teiken_id,
                             turbine_id=outage_model.turbine_id,
                             date_start=form.date_start.data,
                             date_end=form.date_end.data,
                             )
        return jsonify({'url': target_url})

    else:
        form = OutageEditForm(request.args)
        form.outage_type_t.data = 1
        form.outage_type_g.data = 1
        form.execution.data = 100
        turbine_id = request.args.get('turbine_id')
        data_type = menu_param["data_type"] = request.args.get('data_type')
        date_start = request.args.get('date_start')
        date_end = request.args.get('date_end')
        menu_param["min_year"], menu_param["max_year"] = int(date_start), int(date_end)
        menu_param["year_count"] = menu_param["max_year"] - menu_param["min_year"] + 1
        search_table = "TURBINE_LIST_ESS" if (current_user.corp_cd == 'CNV') else "TURBINE_LIST_EX"
        turbine = DbUtil.sqlExcuter(scheduleSql.fetchOneTurbineSql, search_table=search_table, turbine_id=turbine_id,
                                    data_type=data_type).fetchone()
        menu_param['outage_schedule_list'] = [RowObj(**{k: v for k, v in turbine.items()},
                                                     min_year=menu_param["min_year"],
                                                     max_year=menu_param["max_year"])]
    return render_template(
        'outage_schedule_edit.html',
        header_name='Outage Schedule',
        title='Outage Schedule',
        menu_param=menu_param,
        form=form,
    )


def open_outage_schedule_delete(request):
    teiken_id = request.form.get("teiken_id")
    outage = OutageSchedule.query.filter_by(teiken_id=teiken_id).first()
    outage.delete_flg = 1
    outage.deleted_at = datetime.datetime.now()
    outage.deleted_by = current_user.get_id()
    db.session.add(outage)
    db.session.commit()
    msg = None
    return jsonify({"msg": msg})
