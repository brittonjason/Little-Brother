import sys
import sched, time

# check for appropriate command line arguments
if (len(sys.argv) != 9 and len(sys.argv) != 7):
	print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
	sys.exit(2)
elif sys.argv[1] != "-b":
	print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
	sys.exit(2)
elif sys.argv[3] != "[-p" and sys.argv[3] != "[-c":
	print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
	sys.exit(2)
elif sys.argv[3] == "[-p":
	if sys.argv[4][len(sys.argv[4])-1] != "]":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)
	elif sys.argv[5] != "[-c" or sys.argv[6][len(sys.argv[6])-1] != "]":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)
	elif sys.argv[7] != "-k":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)
elif sys.argv[3] == "[-c":
	if sys.argv[3] != "[-c" or sys.argv[4][len(sys.argv[4])-1] != "]":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)
	elif sys.argv[5] != "-k":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)

# gather information from command line
message_broker = sys.argv[2]
if len(sys.argv) == 9:
	virtual_host = sys.argv[4]
	virtual_host = virtual_host[:len(virtual_host)-1]
else:
	virtual_host = "/"
if len(sys.argv) == 9:
	loginpassword = sys.argv[6]
else:
	loginpassword = sys.argv[4]
loginpassword = loginpassword[:len(loginpassword)-1]
loginpassword = loginpassword.split(":")
if len(loginpassword) != 2:
	print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
	sys.exit(2)
login = loginpassword[0]
password = loginpassword[1]
if len(sys.argv) == 9:
	routing_key = sys.argv[8]
else:
	routing_key = sys.argv[6]

# for timing interface
s = sched.scheduler(time.time, time.sleep)

# function to run every second
def getTimes(sc, last_idle, last_total, oldwlanRec, oldwlanTran, oldloRec, oldloTran, oldethRec, oldethTran, time):
	with open('/proc/stat') as f:
		fields = [float(column) for column in f.readline().strip().split()[1:]]
	with open('/proc/net/dev') as f:
		readNet = f.readlines()
	# increment time
	time += 1
	print('\n\nat time: ' + str(time))
	# gather all new readings
	idle, total = fields[3], sum(fields)
	idle_delta, total_delta = idle - last_idle, total - last_total
	utilisation = (1.0 - idle_delta / total_delta) # CPU in JSON message
	print('util: ' + str(utilisation))
	
	wlan = readNet[2]
	wlan = wlan.split(' ')
	while '' in wlan:
		wlan.remove('')
	newwlanRec = wlan[2]
	newwlanTran = wlan[9]
	wlan0rx = float(newwlanRec) - float(oldwlanRec) #wlan0:rx on JSON
	wlan0tx = float(newwlanTran) - float(oldwlanTran) #wlan0:tx on JSON
	
	lo = readNet[3]
	lo = lo.split(' ')
	while '' in lo:
		lo.remove('')
	newloRec = lo[2] 
	newloTran = lo[9]
	lorx = float(newloRec) - float(oldloRec) #lo:rx on JSON
	lotx = float(newloTran) - float(oldloTran) #lo:tx on JSON
	
	eth = readNet[4]
	eth = eth.split(' ')
	while '' in eth:
		eth.remove('')
	newethRec = eth[2] 
	newethTran = eth[9]
	eth0rx = float(newethRec) - float(oldethRec) #eth0:rx on JSON
	eth0tx = float(newethTran) - float(oldethTran) #eth0:tx on JSON
	
	# print relevant information and send JSON message only
	# after initial values have been taken
	
	if time != 1:
		print('wlan0:\n\trx: ' + str(wlan0rx))
		print('\ttx: ' + str(wlan0tx))
		print('lo:\n\trx: ' + str(lorx))
		print('\ttx: ' + str(lotx))
		print('eth0:\n\trx: ' + str(eth0rx))
		print('\ttx: ' + str(eth0tx))

	s.enter(1, 1, getTimes, (sc,idle,total,newwlanRec, newwlanTran, newloRec, newloTran, newethRec, newethTran,time,))
	
# runs function every second
s.enter(1, 1, getTimes, (s,0,0,0,0,0,0,0,0,0,))
s.run()
