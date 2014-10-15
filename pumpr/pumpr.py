__version__ = "0.1.0"

from Phidgets.Devices.InterfaceKit import InterfaceKit
from .cli import parseCommandLineArgs
from .config import saveNewSetup, deleteSetup, updateSetupField, getSetupInfoFromConfig
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
            #set both pumps to withdraw volume 13.0mL at 5 mL/min
            for ch in self.pump_channels:
                ch = str(ch) #config file strs are unicode, Telnet needs str
                self.pump_conn.write(ch + " VOL 13.0\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " RAT 5.0 MM\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " DIR WDR\r\n")
                self.pump_conn.read_until(ch, timeout=5)
            #now start withdrawing the syringes
            for ch in self.pump_channels:
                ch = str(ch) #config file strs are unicode, Telnet needs str
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
            #set both pumps to withdraw volume 13.0mL at 5 mL/min
            for ch in self.pump_channels:
                ch = str(ch) #config file strs are unicode, Telnet needs str
                self.pump_conn.write(ch + " VOL 13.0\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " RAT 5.0 MM\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " DIR INF\r\n")
                self.pump_conn.read_until(ch, timeout=5)
            #now start infusing
            for ch in self.pump_channels:
                ch = str(ch) #config file strs are unicode, Telnet needs str
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
                ch = str(ch) #config file strs are unicode, Telnet needs str
                self.pump_conn.write(ch + " VOL 1.0\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " RAT 3.0 MM\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " DIR INF\r\n")
                self.pump_conn.read_until(ch, timeout=5)
                self.pump_conn.write(ch + " RUN\r\n")
                self.pump_conn.read_until(ch + "I", timeout=5)
            time.sleep(19) #keep the connection around on the main thread for cancellation
        else:
            print self.setup_name, "failed to prime for the behavior session. self.ikit.isAttachedToServer() == False"

class cycleForever(threading.Thread):
    def __init__(
        self,
        behavior_setup_name,
        interfaceKitIPAddress,
        pumpIPAddress,
        interfaceKitPort=5001,
        pumpPort=100,
        pump_channels=["01", "02"]
        ):
        threading.Thread.__init__(self)
        self.setup_name = behavior_setup_name
        self.interfaceKitIPAddress = interfaceKitIPAddress
        self.interfaceKitPort = interfaceKitPort
        self.controller = InterfaceKit()
        self.controller.openRemoteIP(self.interfaceKitIPAddress, self.interfaceKitPort)
        self.pumpIPAddress = pumpIPAddress
        self.pumpPort = pumpPort
        self.pumpsConn = newPumpConnection(self.pumpIPAddress, self.pumpPort)
        self.pump_channels = pump_channels

    def run(self):
        while True:
            infuse = infuseFully(self.setup_name, self.controller, self.pumpsConn, pump_channels=self.pump_channels)
            infuse.start()
            infuse.join()
            withdraw = withdrawFully(self.setup_name, self.controller, self.pumpsConn, pump_channels=self.pump_channels)
            withdraw.start()
            withdraw.join()

class cycleFor(threading.Thread):
    def __init__(
        self,
        numCycles,
        behavior_setup_name,
        interfaceKitIPAddress,
        pumpIPAddress,
        interfaceKitPort=5001,
        primeForBehavior=True,
        pumpPort=100,
        pump_channels=["01", "02"]
        ):
        threading.Thread.__init__(self)
        self.controller = InterfaceKit()
        self.controller.openRemoteIP(interfaceKitIPAddress, interfaceKitPort)
        self.pumpsConn = newPumpConnection(pumpIPAddress, pumpPort)
        self.numCycles = numCycles
        self.behavior_setup_name = behavior_setup_name
        self.interfaceKitIPAddress = interfaceKitIPAddress
        self.pumpIPAddress = pumpIPAddress
        self.interfaceKitPort = interfaceKitPort
        self.primeForBehavior = primeForBehavior
        self.pumpPort = pumpPort
        self.pump_channels = pump_channels
    def run(self):
        #infuse fully then withdraw fully for numCycles
        for i in xrange(self.numCycles):
            infuse = infuseFully(self.behavior_setup_name, self.controller, self.pumpsConn, pump_channels=self.pump_channels)
            infuse.start()
            infuse.join()
            withdraw = withdrawFully(self.behavior_setup_name, self.controller, self.pumpsConn, pump_channels=self.pump_channels)
            withdraw.start()
            withdraw.join()
        if self.primeForBehavior:
            prime = primeForBehaviorSession(self.behavior_setup_name, self.controller, self.pumpsConn, pump_channels=self.pump_channels)
            prime.start()
            prime.join()
        self.pumpsConn.close()

def main():
    args = parseCommandLineArgs()
    config = getSetupInfoFromConfig()
    if args["add"]:
        saveNewSetup(
            args["<setupName>"][0],
            args["<phidgetWebServiceIPaddress>"],
            args["<StartechAdaptorIPaddress>"],
            phidget_webservice_listen_port=int(args["--phidgetPort"]),
            pump_telnet_listen_port=int(args["--startechPort"]),
        )

    elif args["rm"]:
        for setup in args["<setupName>"]:
            deleteSetup(setup)

    elif args["config"] and args["channels"]:
        updateSetupField(args["<setupName>"][0], "pump_channels", [chan for chan in args["<chans>"]])

    elif args["run"]:
        if args["cycle"]:
            threads = []
            for setup in args["<setupName>"]:
                #run pump routine for each setup in its own thread
                pump_routine = cycleFor(
                    int(args["-n"]),
                    setup,
                    config["setups"][setup]["setupIPaddr"],
                    config["setups"][setup]["pumpIPaddr"],
                    interfaceKitPort=config["setups"][setup]["phidget_webservice_listen_port"],
                    primeForBehavior=args["--primePumps"],
                    pumpPort=config["setups"][setup]["pump_telnet_listen_port"],
                    pump_channels=config["setups"][setup]["pump_channels"]
                )
                pump_routine.setDaemon(True)
                pump_routine.start()
                threads.append(pump_routine)
            print "Starting infuse/withdraw for", args["-n"], "cycles. Ctrl+c to stop pumping..."
            try:
                while threading.activeCount() > 1: #keep main thread running so it can raise KeyboardInterrupt
                    time.sleep(1)
            except KeyboardInterrupt:
                for pump_routine in threads: #TODO make this thread safe with threading.Lock in case main thread tries to access pumpConns concurrently
                    if pump_routine.isAlive():
                        for ch in pump_routine.pump_channels:
                            ch = str(ch)
                            pump_routine.pumpsConn.write(ch + " STP\r\n")
                            pump_routine.pumpsConn.read_until(ch, timeout=5)
                        pump_routine.pumpsConn.close()

        if args["forever"]:
            threads = []
            for setup in args["<setupName>"]:
                pump_routine = cycleForever(
                    setup,
                    config["setups"][setup]["setupIPaddr"],
                    config["setups"][setup]["pumpIPaddr"],
                    interfaceKitPort=config["setups"][setup]["phidget_webservice_listen_port"],
                    pumpPort=config["setups"][setup]["pump_telnet_listen_port"],
                    pump_channels=config["setups"][setup]["pump_channels"]
                )
                pump_routine.setDaemon(True)
                pump_routine.start()
                threads.append(pump_routine)
            print "Withdraw/Infuse cycling forever...happy cleaning. :-)"
            print "Protip: ctrl+c will exit the program after finishing the current cycle"
            try:
                while threading.activeCount() > 1:
                    time.sleep(1)
            except KeyboardInterrupt:
                for pump_routine in threads:
                    if pump_routine.isAlive():
                        for ch in pump_routine.pump_channels:
                            ch = str(ch)
                            pump_routine.pumpsConn.write(ch + " STP\r\n")
                            pump_routine.pumpsConn.read_until(ch, timeout=5)
                        pump_routine.pumpsConn.close()
    elif args["inf"]:
        threads = []
        for setup in args["<setupName>"]:
            controller = InterfaceKit()
            controller.openRemoteIP(config["setups"][setup]["setupIPaddr"], config["setups"][setup]["phidget_webservice_listen_port"])
            pumpsConn = newPumpConnection(config["setups"][setup]["pumpIPaddr"], port=config["setups"][setup]["pump_telnet_listen_port"])
            time.sleep(0.2) #give time to establish connections; multiple threads need extra time
            pump_routine = infuseFully(
                setup,
                controller,
                pumpsConn,
                pump_channels=config["setups"][setup]["pump_channels"]
            )
            pump_routine.setDaemon(True)
            pump_routine.start()
            threads.append(pump_routine)
        print "Infusing...press ctrl+c to cancel."
        try:
            while threading.activeCount() > 1:
                time.sleep(1)
        except KeyboardInterrupt:
            for pump_routine in threads:
                    if pump_routine.isAlive():
                        for ch in pump_routine.pump_channels:
                            ch = str(ch)
                            pump_routine.pump_conn.write(ch + " STP\r\n")
                            pump_routine.pump_conn.read_until(ch, timeout=5)
                        pump_routine.pump_conn.close()
    elif args["wdr"]:
        threads = []
        for setup in args["<setupName>"]:
            controller = InterfaceKit()
            controller.openRemoteIP(config["setups"][setup]["setupIPaddr"], config["setups"][setup]["phidget_webservice_listen_port"])
            pumpsConn = newPumpConnection(config["setups"][setup]["pumpIPaddr"], port=config["setups"][setup]["pump_telnet_listen_port"])
            time.sleep(0.2) #give time to establish connections; multiple threads need extra time
            pump_routine = withdrawFully(
                setup,
                controller,
                pumpsConn,
                pump_channels=config["setups"][setup]["pump_channels"]
            )
            pump_routine.setDaemon(True)
            pump_routine.start()
            threads.append(pump_routine)
        print "Withdrawing...press ctrl+c to cancel."
        try:
            while threading.activeCount() > 1:
                time.sleep(1)
        except KeyboardInterrupt:
            for pump_routine in threads:
                    if pump_routine.isAlive():
                        for ch in pump_routine.pump_channels:
                            ch = str(ch)
                            pump_routine.pump_conn.write(ch + " STP\r\n")
                            pump_routine.pump_conn.read_until(ch, timeout=5)
                        pump_routine.pump_conn.close()

    elif args["prime"]:
        threads = []
        for setup in args["<setupName>"]:
            controller = InterfaceKit()
            controller.openRemoteIP(config["setups"][setup]["setupIPaddr"], config["setups"][setup]["phidget_webservice_listen_port"])
            pumpsConn = newPumpConnection(config["setups"][setup]["pumpIPaddr"], port=config["setups"][setup]["pump_telnet_listen_port"])
            time.sleep(0.2) #give time to establish connections; multiple threads need extra time
            pump_routine = primeForBehaviorSession(
                setup,
                controller,
                pumpsConn,
                pump_channels=config["setups"][setup]["pump_channels"]
            )
            pump_routine.setDaemon(True)
            pump_routine.start()
            threads.append(pump_routine)
        print "Infusing 1 mL to get water flowing for a behavior session...press ctrl+c to cancel."
        try:
            while threading.activeCount() > 1:
                time.sleep(1)
        except KeyboardInterrupt:
            for pump_routine in threads:
                    if pump_routine.isAlive():
                        for ch in pump_routine.pump_channels:
                            ch = str(ch)
                            pump_routine.pump_conn.write(ch + " STP\r\n")
                            pump_routine.pump_conn.read_until(ch, timeout=5)
                        pump_routine.pump_conn.close()
    else:
        pass

