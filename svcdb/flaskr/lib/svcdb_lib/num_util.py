import re


class NumUtil:

    def is_number_data(data):
        if not data:
            data = ''

        data = data.strip()
        if not re.search('[0-9]', data):
            return 0

        if re.search('^[+\-]?[0-9,]*(\.?)[0-9]*$', data):
            return 1

        return 0

    def is_integer_data(data):
        if not data:
            data = ''

        data = data.strip()
        if not re.search('[0-9]', data):
            return 0

        if re.search('^[+\-]?[0-9,]*$', data):
            return 1

        return 0

    def _trim_number(data):
        if not data:
            data = ''

        data = re.sub(r'[\s,]', r'', data)

        return data

    def split_number(data, num_prop):
        if not data:
            data = ''

        data = NumUtil._trim_number(data)

        search_rst = re.search('^([+\-]?)([\d,]*)(?:.?)(\d*)$', data)
        if search_rst:
            num_prop['sign_ref'] = search_rst.group(1)
            num_prop['i_ref'] = re.sub(r',', r'', search_rst.group(2))
            num_prop['f_ref'] = search_rst.group(3)
