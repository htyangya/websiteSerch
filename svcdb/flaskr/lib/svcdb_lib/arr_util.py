class ArrUtil:

    def search_array(arr_ref, search_data):
        if search_data not in arr_ref:
            return -1

        return arr_ref.index(search_data)
