from __future__ import annotations
from colorama import Fore
from typing import TypedDict, Union, Literal

Color = Literal["RED", "BLUE", "GREEN", "YELLOW", "WHITE", "BLACK", "MAGENTA", "CYAN"]
ColorTable = {
    "RED": Fore.RED,
    "BLUE": Fore.BLUE,
    "GREEN": Fore.GREEN,
    "YELLOW": Fore.YELLOW,
    "WHITE": Fore.WHITE,
    "BLACK": Fore.BLACK,
    "MAGENTA": Fore.MAGENTA,
    "CYAN": Fore.CYAN,
}
ColorReset = "\033[0m"

class LoggerOptions (TypedDict):

  NAME: Union[str, None]
  SUCCESS_COLOR: Union[Color, None]
  INFO_COLOR: Union[Color, None]
  ERROR_COLOR: Union[Color, None]
  WARN_COLOR: Union[Color, None] 

  @staticmethod
  def DefaultWithName(name : Union[str, None]) -> LoggerOptions:
    return {
      "NAME": name,
      "SUCCESS_COLOR": "GREEN",
      "INFO_COLOR": "BLUE",
      "WARN_COLOR": "YELLOW",
      "ERROR_COLOR": "RED"
    }

  @staticmethod
  def Default() -> LoggerOptions:
    return LoggerOptions.DefaultWithName(None)

class Logger:

  def __init__(self, options : LoggerOptions) -> None:
    self.options = options
  
  def success(self, log : str) -> None:
    print(f"{ColorTable[self.options["SUCCESS_COLOR"]]}{"" if self.options["NAME"] is None else f"[{self.options["NAME"]}] "}{log}{ColorReset}")

  def info(self, log : str) -> None:
    print(f"{ColorTable[self.options["INFO_COLOR"]]}{"" if self.options["NAME"] is None else f"[{self.options["NAME"]}] "}{log}{ColorReset}")

  def warn(self, log : str) -> None:
    print(f"{ColorTable[self.options["WARN_COLOR"]]}{"" if self.options["NAME"] is None else f"[{self.options["NAME"]}] "}{log}{ColorReset}")

  def error(self, log : str) -> None:
    print(f"{ColorTable[self.options["ERROR_COLOR"]]}{"" if self.options["NAME"] is None else f"[{self.options["NAME"]}] "}{log}{ColorReset}")
