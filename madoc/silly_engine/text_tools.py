#! /usr/bin/env python3

"""
color parameters: style;background (30 is none);foreground
example:
c = Color
print(f"{c.info}This is an info message{c.end}")
"""


class Color:
    end = "\x1b[0m"
    cyan    =    info       = "\x1b[0;30;36m"
    red     =    danger     = "\x1b[0;30;31m"
    green   =    success    = "\x1b[0;30;32m"
    yellow  =    warning    = "\x1b[0;30;33m"
    blue = "\x1b[0;30;34m"
    violet = "\x1b[0;30;35m"

    fg_red = "\x1b[5;30;41m"
    fg_green = "\x1b[5;30;42m"
    fg_yellow = "\x1b[5;30;43m"
    fg_blue = "\x1b[5;30;44m"
    fg_cyan = "\x1b[5;30;46m"
    fg_violet = "\x1b[5;30;45m"
    fg_white = "\x1b[5;30;47m"

    bg_red = "\x1b[2;30;41m"
    bg_green = "\x1b[2;30;42m"
    bg_yellow = "\x1b[2;30;43m"
    bg_blue = "\x1b[2;30;44m"
    bg_cyan = "\x1b[2;30;46m"
    bg_violet = "\x1b[2;30;45m"
    bg_white = "\x1b[2;30;47m"

    def demo(self):
        """print all available colors"""
        no_display = ["end", "demo"]
        for attr in dir(self):
            if not attr.startswith("__") and attr not in no_display:
                print(f"{getattr(self, attr)}{attr}{self.end}")

c = Color()
