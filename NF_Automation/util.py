import json
class SuccessStatus:
    DEFAULT = 'true'
    HTTP = 200
    SUCCESS = 'success'

class SuccessMessage:
    CREATE_MESSAGE = 'Successfully Created'

class Success:
    status = None
    message = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_status(self, status):
        self.status = status

    def set_message(self, message):
        self.message = message



class Error:
    code = None
    description = None
    errorcode=None
    def __init__(self):
        pass

    def set_code(self, code):
        self.code = code

    def errorcode(self, errorcode):
        self.errorcode = errorcode

    def set_description(self, description):
        self.description = description

    def get_code(self):
        return self.code

    def get_description(self):
        return self.description

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)


import json
import decimal
import datetime
from django.template.defaultfilters import length


class VysfinList:
    data = []
    pagination = None
    count=None
    glcount = None
    creditcount=0
    debitcount=0
    totalcount=0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_unsorted(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=False, indent=4)

    def get_cus(self):
        def custom_serializer(o):
            if isinstance(o, decimal.Decimal):
                return float(o)
            if isinstance(o, (datetime.date, datetime.datetime)):
                return o.isoformat()
            if hasattr(o, '__dict__'):
                return o.__dict__
            return str(o)  # fallback

        return json.dumps(self, default=custom_serializer, sort_keys=True, indent=4)

    def __init__(self):
        self.data = []

    def set_list(self, list):
        self.data = list

    def get_list(self):
        return self.data

    def append(self, obj):
        self.data.append(obj)

    def list_extend(self, obj):
        self.data.extend(obj)

    def set_listcount(self, count):
        self.count = count

    def set_glcount(self, glcount):
        self.glcount = glcount

    def set_totalcount(self, totalcount):
        self.totalcount = totalcount
    def get_listcount(self):
        return self.count


    def set_pagination(self, pagination):
        self.pagination = pagination
        if length(self.data) > pagination.limit:
            self.data.pop()



    def get_pagination(self):
        return self.pagination



