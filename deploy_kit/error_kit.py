# ProductionMode Exception and Traceback Handler.
# (C) 2023 Dierk-Bent Piening <d.b.piening@mailbox.org>
# (C) 2023 NeonLogic GmbH
# This is free software, you can modify it under the terms of the general public license (GPL v2).
# Python code is peotry
import sys
import os
import typing
import json
import platform
from datetime import datetime
from concurrent import futures
from pathlib import Path

class ProductionErrorKit:
    def __init__(self, appname: str, logfile_path: str):
        self._appname: str = appname
        self._logfile_path = logfile_path
        self._exception_header: str = (
            f"\n{datetime.now()} An unexspected Error Occured!\n"
        )
        self._debug_mode = False

    @property
    def exception_header(self) -> str:
        return self.exception_header

    @exception_header.setter
    def exception_header(self, custom_header: str) -> None:
        self._exception_header = custom_header

    @property
    def debug_mode(self) -> bool:
        return self.__debug_mode

    @debug_mode.setter
    def debug_mode(self, debugmode) -> None:
        self.debug_mode = debugmode

    def __handle_exception(type, value: str, traceback: Exception) -> None:
        def execute(type, value: str, traceback: Exception):
            _error_filename: str = (
                f"error_stacktrace_{datetime.now().strftime('%m-%d-%Y')}.json"
            )
            _error_file_object = os.path.exists(_error_filename)
            _error_message: str = f"Developer Informations got secured and saved!"
            _proccess_pid: int = int(os.getpid())
            _error_message_response: dict = {
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
                                            "__loader__": str(traceback.tb_frame.f_locals['__loader__']),
                                            },
                        "host_details": {
                                "node_name": platform.node(),
                                "platform": platform.platform(),
                                "architecture": platform.processor(),
                            },
                        "Python_Details:" {},
                        "value": str(value),
                        "type": f"{type}",
                    },
                ]
            }
            if os.environ.get('PYTHONPRODDEBUG_CLI') == "enabled":
                print(json.dumps(_error_message_response, indent=4))
            if _error_file_object == True:
                try:
                    with open(_error_filename) as file:
                         _existing_error_file = file.read()
                except FileNotFound:
                    print(f"Fatal error occured in ProductionErrorModul!\n  Could not read stacktrace file:_object\n    Filename: {_error_filename}")
                try:
                    _current_error_file_state = json.loads(_existing_error_file)
                except json.decoder.JSONDecodeError as ex:
                        print(f"Fatal error occured in ProductionErrorModul!\n  Could not decode json error object\n    Message: {ex.msg}\n    Line: {ex.lineno}\n    Pos: {ex.pos}\n    Column: {ex.colno}")
                        sys.stdout.flush()
                        sys.exit("Fatal Error")
                _current_error_file_state["Exceptions"].append(
                        _error_message_response["Exceptions"])
                try:
                    with open(_error_filename, "w") as file:
                        file.write(json.dumps(_current_error_file_state))
                except FileNotFound:
                    print(f'Fatal Error at handling existing error file!')
            else:
                try:
                    with open(_error_filename, "a+") as file:
                        file.write(json.dumps(_error_message_response))
                except Exception as ex:
                    print(f"Could not write StacktraceFile\n{str(ex)}")

        with futures.ThreadPoolExecutor(max_workers=20) as traceback_handle_proccess:
            traceback_handle_proccess.submit(execute, type, value, traceback)

    @classmethod
    def enable_production_exception_mode(self) -> None:
        try:
            sys.excepthook = self.__handle_exception
        except Exception as ex:
            print("Fatal Error, could not activate production_exception_mode")
