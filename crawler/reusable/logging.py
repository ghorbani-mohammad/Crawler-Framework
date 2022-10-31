from logging import Handler

from agency.models import DBLogEntry


class DBHandler(Handler, object):
    def __init__(self):
        super(DBHandler, self).__init__()

    def emit(self, record):
        try:
            log_entry = DBLogEntry(level=record.levelname, message=self.format(record))
            log_entry.save()
        except:
            pass
