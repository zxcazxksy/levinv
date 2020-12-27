import os

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *

f = open("files/condition_stock.txt", "a", encoding="utf8")
a = "94360"
b = "칩스앤미디어"
c = "9610"
f.write("%s\t%s\t%s\n" % (str("094360"), str("칩스앤미디어"), str("9610")))
f.close()
