BUFFER_SIZE = 1024
HEARTBEAT = 5
EXPIRIES = HEARTBEAT * 3
RAND_MIN = 45000
RAND_MAX = 49000


def getIp(s):
    return (s.split(":")[0], int(s.split(":")[1]))


def getStr(ip):
    return ip[0]+":"+str(ip[1])
