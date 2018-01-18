from qpython import *

q = qconnection.QConnection(host = '35.229.70.14', port = 5432, username = 'admin', password = 'It\'s a vibe', timeout = 3.0)
try:
    q.open()
    print(q('1+1'));
finally:
    q.close()