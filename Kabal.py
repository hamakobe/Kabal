import sys
import ac
import acsys
import os
import os.path
import platform
import math
import datetime

#Picking between 64bit or 32bit libraries for the physics modules (fuel etc.)
if platform.architecture()[0] == "64bit":
    sysdir=os.path.dirname(__file__)+'/shared_memory/stdlib64'
    sysdirq=os.path.dirname(__file__)+'/qpython'
    dlls=os.path.dirname(__file__)+'/DLLs'
else:
    sysdir=os.path.dirname(__file__)+'/shared_memory/stdlib'
    dlls=os.path.dirname(__file__)+'/32DLLs'
sys.path.insert(0, sysdir)
os.environ['PATH'] = os.environ['PATH'] + ";."
sys.path.insert(0, sysdirq)
os.environ['PATH'] = os.environ['PATH'] + ";."
sys.path.insert(0, dlls)
os.environ['PATH'] = os.environ['PATH'] + ";."

#Importing the info module, which includes fuel info 
from shared_memory.sim_info import *
try:
    from qpython import *
    q = qconnection.QConnection(host = '35.229.70.14', port = 5432, username = 'admin', password = 'It\'s a vibe', timeout = 3.0)
except ImportError as e:
   ac.log("imported error: %s" % e)

#Global variables
l_lapcount=0
lapcount=0
l_speed=0
tick=0
laps=0
speed = 0
fuel = 0
clap_top_speed = 0
llap_top_speed = 0
tspeed_session = 0
l_tspeed_session = 0
l_tspeed_llap = 0
l_tspeed_clap = 0
l_q = 0
l_fuel = 0

#Session ID
drivername = ac.getDriverName(0) #info.static.playerName
drivername = drivername.replace(" ","")
trackname = ac.getTrackName(0) #info.static.track
carname = ac.getCarName(0) #info.static.carModel
currenttime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
sessionid = "{a}_{b}_{c}_{d}".format(a=drivername,b=currenttime,c=trackname,d=carname)

#Output file name and directory definition
try:
    sessionstarttime = datetime.datetime.now().strftime(' %b, %d, %Y %H %M %S')
    targetdir = os.path.dirname(__file__)+'/TESTS/'
    targetname = "{d}Session from {t}.txt".format(d=targetdir,t=sessionstarttime)
    #targetfile = open(targetname,"w") #use this file to run tests on outputs
except Exception as e:
    ac.log("File creation error was: {}".format(e))

#Main Assetto Corsa function, builds the App Window and the labels associated with it
def acMain(ac_version):
    global l_lapcount, l_speed, appWindow, l_tspeed_session, l_tspeed_llap, l_tspeed_clap, tick, q, l_q, sessionid, l_fuel
    

    tick=ticker() #set the global variable to be a ticker, see the class below
    appWindow = ac.newApp("Kabal")
    q.open() #opens connection

    l_lapcount = ac.addLabel(appWindow, "Lap: {}".format(0));
    l_speed = ac.addLabel(appWindow, "Speed: {}".format(0));
    l_tspeed_session = ac.addLabel(appWindow, "Session Top Speed: {}".format(0));
    l_tspeed_llap = ac.addLabel(appWindow, "Last Lap Top Speed: {}".format(0));
    l_tspeed_clap = ac.addLabel(appWindow, "Current Lap Top Speed: {}".format(0));
    l_fuel = ac.addLabel(appWindow, "Fuel Level: {} L".format(0));
    l_q = ac.addLabel(appWindow, "Q-test, 1+1? {}".format(q('1+1'))); #visual test of connection
    q.query(qconnection.MessageType.SYNC,'{}:([] time:();lap:();speedMPH:();fuelL:();psiFL:();psiFR:();psiRL:();psiRR:())'.format(sessionid)) #creates a table
    
    ac.setSize(appWindow, 250, 200)
    ac.setPosition(l_lapcount, 3, 30)
    ac.setPosition(l_speed, 3, 60)
    ac.setPosition(l_tspeed_session, 3, 80)
    ac.setPosition(l_tspeed_llap, 3, 100)
    ac.setPosition(l_tspeed_clap, 3, 120)
    ac.setPosition(l_fuel, 3, 140)
    ac.setPosition(l_q, 3, 160)

    return "Kabal"
    
#Main update function for Assetto Corsa, it runs the enclosed code every DeltaT - I think DeltaT = 1/60 of a second
def acUpdate(deltaT):
    global l_lapcount, l_speed, lapcount, targetfile, tick, speed, clap_top_speed, llap_top_speed, tspeed_session, q, sessionid, fuel

    if tick.tack(deltaT):  #does not bother CPU with unnecessary updates, basically exits the update function call if time is less than value specified in ticker()
        return
    
    fuel = round(info.physics.fuel,3)
    psiFL,psiFR,psiRL,psiRR = ac.getCarState(0,acsys.CS.DynamicPressure)
    laps = ac.getCarState(0, acsys.CS.LapCount)+1
    speed = round(ac.getCarState(0, acsys.CS.SpeedMPH),2)
    ac.setText(l_speed,"Speed: {} MPH".format(speed))
    ac.setText(l_fuel,"Fuel Level: {} L".format(fuel))
    q.query(qconnection.MessageType.SYNC,'`{t} insert (.z.P;{l};{s};{f};{pFL};{pFR};{pRL};{pRR})'.format(t=sessionid,l=laps,s=speed,f=fuel,pFL=psiFL,pFR=psiFR,pRL=psiRL,pRR=psiRR))

    if speed > clap_top_speed:
        clap_top_speed = speed
        ac.setText(l_tspeed_clap,"Current Lap Top Speed: {} MPH".format(clap_top_speed))

    if speed > tspeed_session:
        tspeed_session = speed
        ac.setText(l_tspeed_session,"Session Top Speed: {} MPH".format(tspeed_session))

    if laps > lapcount:
        lapcount = laps
        llap_top_speed = clap_top_speed
        clap_top_speed = 0
        ac.setText(l_lapcount, "Lap: {}".format(lapcount)) #updates the label in the App Window defined on acMain
        ac.setText(l_tspeed_llap, "Last Lap Top Speed: {} MPH".format(llap_top_speed));
        
def acShutdown():
    global sessionid, q
    q.query(qconnection.MessageType.SYNC,'`:Sessions/{a}/ set {b}'.format(a=sessionid,b=sessionid))
    q.close()
#-----------------------
# ticker function, to determine update rate
#--------------------
class ticker:
    def __init__(self):
        self.ticktimer = 0.0
        self.ticktime = 0.0
        self.tickrate = 0.1 #update rate in seconds
   
    def tack(self,deltaT):
        self.ticktime += deltaT
        self.ticktimer += deltaT
        if self.ticktime >= self.tickrate:
            self.ticktime = self.ticktime % self.tickrate
            return False
        else:
            return True
   
    def debuginfo(self):
        return "ticktimer: %s ticktime: %s tickrate: %s" % (self.ticktimer, self.ticktime, self.tickrate)
