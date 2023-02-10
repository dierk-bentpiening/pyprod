# ProductionMode Exception and Traceback Handler.
# (C) 2023 Dierk-Bent Piening <d.b.piening@mailbox.org>
# (C) 2023 NeonLogic GmbH
# This is free software, you can modify it under the terms of the general public license (GPL v2).
# Python code is peotry
import sys
import os
import json
import platform
import logging
import psutil
from datetime import datetime
from concurrent import futures
from pathlib import Path

class ProductionErrorKit:
    def __init__(self, appname, logfile_path, debug_mode=False):
        self.logger = logging.getLogger(__name__)
        self._appname = appname
        self._logfile_path = logfile_path
        self.debug_mode = debug_mode

    @property
    def debug_mode(self):
        return self.__debug_mode

    @debug_mode.setter
    def debug_mode(self, debugmode):
        self.debug_mode = debugmode

    def __handle_exception(self, type, value, traceback):
        def execute(self, type, value, traceback):
            _error_filename = "error_stacktrace_"+ datetime.now().strftime('%m-%d-%Y') + ".json"

            _error_file_object = os.path.exists(_error_filename)
            _error_message = "Developer Informations got secured and saved!"
            _proccess_pid = int(os.getpid())
            self.logger.debug("Successfully loaded base information..")
            _error_message_response = {
                "Exceptions": [
                    {
                        "message": _error_message,
                        "datetime": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "app_pid": os.getpid(),
                        "traceback_sourcename": traceback.tb_frame.f_code.co_filename,
                        "traceback_lineno": traceback.tb_lineno,
                        "traceback_locals":{
                                            "__name__": traceback.tb_frame.f_locals['__name__'],
                                            "__doc__": traceback.tb_frame.f_locals['__doc__'],
                                            "__package__": traceback.tb_frame.f_locals['__package__'],

                                            },
                        "host_details": {
                                "node_name": platform.node(),
                                "platform": platform.platform(),
                                "architecture": platform.processor(),
                                "os": platform.system(),
                                "os_release": platform.release(),
                                "os_version": platform.version(),
                                "memory_total": int(round(psutil.virtual_memory().total / (1024. **3))),
                                "memory_used": round(psutil.virtual_memory()[3]/ (1024 **3), 2)
                        },
                        "python_details:": {
                                "python_version": platform.python_version(),
                                "python_scm_revision": platform.python_revision(),
                                "python_scm_branch": platform.python_branch(),
                                "python_build": platform.python_build(),
                                "python_implementation": platform.python_implementation(),
                                "python_compiler": platform.python_compiler(),
                            },
                        "value": str(value),
                        "type": str(type),
                    },
                ]
            }
            self.logger.info("Successfully generated stacktrace file...")
            if self.debug_mode == True:
                self.logger.info(json.dumps(_error_message_response, indent=4))
            if _error_file_object == True:
                try:
                    with open(_error_filename) as file:
                         _existing_error_file = file.read()
                except FileNotFound:
                    print("Fatal error occured in ProductionErrorModul!\n  Could not read stacktrace file:_object\n    Filename: " + _error_filename)
                try:
                    _current_error_file_state = json.loads(_existing_error_file)
                except json.decoder.JSONDecodeError as ex:
                        sys.stdout.flush()
                        sys.exit("Fatal Error")
                _current_error_file_state["Exceptions"].append(
                        _error_message_response["Exceptions"])
                try:
                    with open(_error_filename, "w") as file:
                        file.write(json.dumps(_current_error_file_state))
                except FileNotFound:
                    self.logger.error('Error Occured! Stacktrace has been saved in Traceback-File' + _error_filename)
            else:
                try:
                    with open(_error_filename, "a+") as file:
                        file.write(json.dumps(_error_message_response))
                except Exception as ex:
                    print("Could not write StacktraceFile\n" + str(ex))
        execute(self, type, value, traceback)
        """
        with futures.ThreadPoolExecutor(max_workers=20) as traceback_handle_proccess:
            traceback_handle_proccess.submit(execute, type, value, traceback)"""

    def enable_production_exception_mode(self):
        try:
            sys.excepthook = self.__handle_exception
        except Exception as ex:
            print("Fatal Error, could not activate production_exception_mode %s" % str(ex))

