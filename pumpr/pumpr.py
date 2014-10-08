__version__ = "0.1.0"

from Phidgets.Devices.InterfaceKit import InterfaceKit
from .cli import parseCommandLineArgs
import telnetlib
import time
import threading

def newPumpConnection(IPaddr, port=100):
    return telnetlib.Telnet(IPaddr, port)

class withdrawFully(threading.Thread):
    def __init__(
            self,
            setup_name,
            interfaceKit,
            telnetconn,
            isFullSensor_AnalogInputNumber_01=1,
            isEmptySensor_AnalogInputNumber_01=2,
            isFullSensor_AnalogInputNumber_02=3,
            isEmptySensor_AnalogInputNumber_02=4,
            pump_channels=["01", "02"]
        ):
        threading.Thread.__init__(self)
        self.setup_name = setup_name
        self.ikit = interfaceKit
        self.pump_conn = telnetconn
        self.channel_01_full_sensor_number = isFullSensor_AnalogInputNumber_01
        self.channel_02_full_sensor_number = isFullSensor_AnalogInputNumber_02
        self.pump_channels = pump_channels

    def run(self):
        time.sleep(0.2) #give everything time to get connected
        if self.ikit.isAttachedToServer():
            #set both pumps to withdraw volume 13.0mL at 3 mL/min
            for ch in self.pump_channels:
                self.pump_conn.write(ch + " VOL 13.0\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " RAT 5.0 MM\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " DIR WDR\r\n")
                self.pump_conn.read_until(ch, timeout=5)
            #now start withdrawing the syringes
            for ch in self.pump_channels:
                self.pump_conn.write(ch + " RUN\r\n")
                self.pump_conn.read_until(ch + "W", timeout=5)

            #monitor "full" sensors to stop the pumps when syringes are full
            pump01_stopped = False
            pump02_stopped = False
            while True:
                sensor01 = self.ikit.getSensorValue(self.channel_01_full_sensor_number)
                sensor02 = self.ikit.getSensorValue(self.channel_02_full_sensor_number)
                if sensor01 < 500 and pump01_stopped == False:
                    self.pump_conn.write("01 STP\r\n")
                    self.pump_conn.read_until("01", timeout=5)
                    pump01_stopped = True
                if sensor02 < 500 and pump02_stopped == False:
                    self.pump_conn.write("02 STP\r\n")
                    self.pump_conn.read_until("02", timeout=5)
                    pump02_stopped = True
                if pump01_stopped and pump02_stopped:
                    break
        else:
            print self.setup_name, "failed to withdraw. self.ikit.isAttachedToServer() == False"

class infuseFully(threading.Thread):
    def __init__(
            self,
            setup_name,
            interfaceKit,
            telnetconn,
            isFullSensor_AnalogInputNumber_01=1,
            isEmptySensor_AnalogInputNumber_01=2,
            isFullSensor_AnalogInputNumber_02=3,
            isEmptySensor_AnalogInputNumber_02=4,
            pump_channels=["01", "02"]
        ):
        threading.Thread.__init__(self)
        self.setup_name = setup_name
        self.ikit = interfaceKit
        self.pump_conn = telnetconn
        self.channel_01_empty_sensor_number = isEmptySensor_AnalogInputNumber_01
        self.channel_02_empty_sensor_number = isEmptySensor_AnalogInputNumber_02
        self.pump_channels = pump_channels

    def run(self):
        time.sleep(0.2) #give everything time to get connected
        if self.ikit.isAttachedToServer():
            #set both pumps to withdraw volume 13.0mL at 3 mL/min
            for ch in self.pump_channels:
                self.pump_conn.write(ch + " VOL 13.0\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " RAT 5.0 MM\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " DIR INF\r\n")
                self.pump_conn.read_until(ch, timeout=5)
            #now start infusing
            for ch in self.pump_channels:
                self.pump_conn.write(ch + " RUN\r\n")
                self.pump_conn.read_until(ch + "I", timeout=5)

            #monitor "empty" sensors to stop the pumps when syringes are empty
            pump01_stopped = False
            pump02_stopped = False
            while True:
                sensor01 = self.ikit.getSensorValue(self.channel_01_empty_sensor_number)
                sensor02 = self.ikit.getSensorValue(self.channel_02_empty_sensor_number)
                if sensor01 < 500 and pump01_stopped == False:
                    self.pump_conn.write("01 STP\r\n")
                    self.pump_conn.read_until("01", timeout=5)
                    pump01_stopped = True
                if sensor02 < 500 and pump02_stopped == False:
                    self.pump_conn.write("02 STP\r\n")
                    self.pump_conn.read_until("02", timeout=5)
                    pump02_stopped = True
                if pump01_stopped and pump02_stopped:
                    break
        else:
            print self.setup_name, "failed to infuse. self.ikit.isAttachedToServer() == False"

class primeForBehaviorSession(threading.Thread):
    '''
    Infuses 1 mL to get water flowing again for a behavior session (used after a full withdrawal).
    '''
    def __init__(
            self,
            setup_name,
            interfaceKit,
            telnetconn,
            isFullSensor_AnalogInputNumber_01=1,
            isEmptySensor_AnalogInputNumber_01=2,
            isFullSensor_AnalogInputNumber_02=3,
            isEmptySensor_AnalogInputNumber_02=4,
            pump_channels=["01", "02"]
        ):
        threading.Thread.__init__(self)
        self.setup_name = setup_name
        self.ikit = interfaceKit
        self.pump_conn = telnetconn
        self.channel_01_full_sensor_number = isFullSensor_AnalogInputNumber_01
        self.channel_02_full_sensor_number = isFullSensor_AnalogInputNumber_02
        self.pump_channels = pump_channels

    def run(self):
        time.sleep(0.2) #give everything time to get connected
        if self.ikit.isAttachedToServer():
            #verify that syringe pumps are fully withdrawn (i.e. in "full" sensor range)
            if not self.ikit.getSensorValue(self.channel_01_full_sensor_number) < 500:
                w = withdrawFully(self.setup_name, self.ikit, self.pump_conn, pump_channels=["01"])
                w.start()
                w.join()
            if not self.ikit.getSensorValue(self.channel_02_full_sensor_number) < 500:
                w = withdrawFully(self.setup_name, self.ikit, self.pump_conn, pump_channels=["02"])
                w.start()
                w.join()
            #everything should be withdrawn...let's prime 'em
            for ch in self.pump_channels:
                self.pump_conn.write(ch + " VOL 1.0\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " RAT 3.0 MM\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " DIR INF\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " RUN\r\n")
                self.pump_conn.read_until(ch + "I", timeout=5)
        else:
            print self.setup_name, "failed to prime for the behavior session. self.ikit.isAttachedToServer() == False"

def cycleForever(behavior_setup_name, interfaceKitIPAddress, pumpIPAddress, interfaceKitPort=5001, pumpPort=100):
    controller = InterfaceKit()
    controller.openRemoteIP(interfaceKitIPAddress, interfaceKitPort)
    pumpsConn = newPumpConnection(pumpIPAddress, pumpPort)
    print "Withdraw/Infuse cycling forever...happy cleaning. :-)"
    print "Protip: ctrl+c will exit the program after finishing the current cycle"

    while True:
        try:
            infuse = infuseFully(behavior_setup_name, controller, pumpsConn)
            infuse.start()
            infuse.join()
            withdraw = withdrawFully(behavior_setup_name, controller, pumpsConn)
            withdraw.start()
            withdraw.join()
        except KeyboardInterrupt:
            print "Exiting..."
            pumpsConn.write("01 STP\r\n")
            pumpsConn.read_until("01", timeout=5)
            pumpsConn.write("02 STP\r\n")
            pumpsConn.read_until("02", timeout=5)
            pumpsConn.close()
            break

def cycleFor(numCycles, behavior_setup_name, interfaceKitIPAddress, pumpIPAddress, interfaceKitPort=5001, primeForBehavior=True, pumpPort=100):
    controller = InterfaceKit()
    controller.openRemoteIP(interfaceKitIPAddress, interfaceKitPort)
    pumpsConn = newPumpConnection(pumpIPAddress, pumpPort)

    #infuse fully then withdraw fully for numCycles
    for i in xrange(numCycles):
        infuse = infuseFully(behavior_setup_name, controller, pumpsConn)
        infuse.start()
        infuse.join()
        withdraw = withdrawFully(behavior_setup_name, controller, pumpsConn)
        withdraw.start()
        withdraw.join()
    if primeForBehavior:
        prime = primeForBehaviorSession(behavior_setup_name, controller, pumpsConn)
        prime.start()
        prime.join()
    pumpsConn.close()

def main():
    command_line_args = parseCommandLineArgs()
    ikit = InterfaceKit()
    print command_line_args
#if __name__ == "__main__":
    #cycleFor(2, "travis", "10.251.103.12", "10.0.254.254")