from qpython import *

q = qconnection.QConnection(host = 'localhost', port = 5000, username = 'tu', password = 'secr3t', timeout = 3.0)
try:
    q.open()
    print(q('1+1'));
finally:
    q.close()