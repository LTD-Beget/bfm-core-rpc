from lib.FileManager.workers.baseWorkerCustomer import BaseWorkerCustomer
import traceback
from config.main import DB_FILE
import sqlite3


class OpenTerminal(BaseWorkerCustomer):
    def __init__(self, login, password, session, *args, **kwargs):
        super(OpenTerminal, self).__init__(login, password, *args, **kwargs)

        self.session = session

    def run(self):
        db = sqlite3.connect(DB_FILE)
        db.execute("PRAGMA journal_mode=MEMORY")
        print("Database created and opened successfully file = %s" % DB_FILE)
        cursor = db.cursor()
        try:
            self.preload()
            self.logger.debug("session=%s" % self.session)
            login = self.login
            if self.session["type"] == "home":
                server = self.session["host"]

            else:
                table_name = ""
                if self.session["type"] == "ftp":
                    table_name = "ftp_servers"
                elif self.session["type"] == "sftp":
                    table_name = "sftp_servers"
                elif self.session["type"] == "webdav":
                    table_name = "webdav_servers"

                self.logger.debug("table_name=%s, login=%s, server_id=%s" % (table_name, self.login, self.session["server_id"]))

                cursor.execute("SELECT * FROM {} WHERE fm_login = ? AND id = ?".format(table_name), (self.login, self.session["server_id"]))
                server_description = cursor.fetchone()
                server = server_description[2]

            self.logger.debug("server=%s" % server)

            result = {
                "data": {
                    "account": {
                        "login": login,
                        "server": server
                    },
                },
                "error": False,
                "message": None,
                "traceback": None
            }
            self.logger.debug("result=%s" % result)
            self.on_success(result)

        except Exception as e:
            result = {
                "error": True,
                "message": str(e),
                "traceback": traceback.format_exc()
            }

            self.on_error(result)
        finally:
            db.close()
