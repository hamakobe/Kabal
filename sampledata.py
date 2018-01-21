from qpython import *

q = qconnection.QConnection(host = '35.229.70.14', port = 5432, username = 'admin', password = 'It\'s a vibe', timeout = 3.0)
try:
    q.open()
    lap=0;
    speed=0;
    q.query(qconnection.MessageType.SYNC,'`samplesession insert (.z.P;{l};{s})'.format(l=lap,s=speed))
    q.query(qconnection.MessageType.SYNC,'`:q/samplesession/ set samplesession')
    print(q.receive(data_only = False, raw = False))
finally:
    q.close()