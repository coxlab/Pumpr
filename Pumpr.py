import telnetlib
import threading
import time
#config must be in the same directory as Pumpr.py
import config

class BehaviorRoom(object):
    def __init__(self, hosts=False):
        '''
        Represents a behavior room full of SkinnerBox instances. It gets 
        hosts/channels from config and/or command line interface
        and stores a list of SkinnerBox instances to iterate through.

        e.g. for skinnerbox in BehaviorRoom():
                skinnerbox.withdraw_pumps()

        Alternatively, you can manually overwrite the default config 
        like this:
            for skinnerbox in BehaviorRoom(hosts={'localhost': ["01"],
                                                   '10.0.0.1': ["01"]}):
                skinnerbox.withdraw_pumps()

        :param hosts: a dict with keys as IP addr strings and values
            as a list of pump channels
        '''
        if hosts:
            self.skinner_boxes = hosts
        else:
            self.skinner_boxes = self.get_boxes_from_config()

    def get_boxes_from_config(self):

        '''Returns a list of SkinnerBox instances'''

        hosts_and_channels_dict = self.get_hosts_and_channels()

        return [SkinnerBox(k, v) for k, v in hosts_and_channels_dict.iteritems()]


    def get_hosts_and_channels(self):

        '''Returns a dict with hosts as keys and channel lists as values, e.g.
        {'192.168.0.20': ["01", "02"], 'setup2pump': ["01"]}

        Currently gets config from a dict in the config.py module,
        TODO: add command line options to specify hosts/channels
        '''

        result = config.config
        print "hosts and channels: %s" % result
        return result

    def __iter__(self):
        '''Access each SkinnerBox instance via a for loop for pretty code!'''
        for skinnerbox in self.skinner_boxes:
            yield skinnerbox


class SkinnerBox(object):
    def __init__(self, host, pumps, port=100):
        '''
        A behavior box object that runs Telnet commands to its pumps via the 
        Startech RS232 over IP adaptor. All Telnet connections/commands runs
        in a threading.Thread object.

        :param host: a str of the StarTech adaptor's IP addr or nickname in 
            /etc/hosts (e.g. "192.168.0.24" or "setup6")

        :param pumps: list of strings with the pump channel numbers
            for the behavior box. This is useful because some behavior boxes
            will have 1 or 2 pumps, e.g. ["01"] or  ["01", "02"]

        :param port: should always be 100, the StarTech port for Telnet

        :param pump_volume: str of the volume in mL to withdraw or infuse

        :param rate: str of rate in mL/minute to withdraw or infuse

        '''

        self.host = host
        self.pumps = pumps
        self.port = port

    def withdraw_pumps(self, volume="8.0", pump_rate="2.0"):
        '''Starts connection/pumping in a thread b/c non-blocking I/O is hard'''
        try:
            thread = threading.Thread(target=self._connect_and_withdraw_pumps(volume, pump_rate))
            thread.start()
        except Exception as e:
            print "Couldn't pump host %s due to exception: %s" % (self.host, e)

    def _connect_and_withdraw_pumps(self, volume, pump_rate):
        '''helper function for self.withdraw_pumps; this runs in a thread'''
        try:
            self.tn = telnetlib.Telnet(self.host, self.port)
            time.sleep(1)
        except Exception as e:
            print "Could not connect to host %s due to error %s" % (self.host, e)
        else:
            print "Starting pumps on host: %s" % self.host
            for channel in self.pumps:
                print "Pumping channel: " + channel
                #meaning of these commands outlined in syringepump.com NE-500 manual
                self.write_to_telnet(channel + " FUN RAT", channel + "S")
                self.write_to_telnet(channel + " RAT " + pump_rate + " MM", channel + "S")
                self.write_to_telnet(channel + " VOL " + volume, channel + "S")
                self.write_to_telnet(channel + " DIR " + "WDR", channel + "S")
                self.write_to_telnet(channel + " RUN", channel + "W")
            self.tn.close()

    def write_to_telnet(self, command, expected_response):
        '''wrapper around Telnet's write function so I can handle exceptions 
        in one method instead of chaining if conditionals for multiple
        commands/exception handling

        This talks to the StarTech RS-232 over IP adaptor, which is 
        plugged into the pumps and accessible via Telnet port 100.
        '''
        self.tn.write(command + "\r\n")
        resp = self.tn.read_until(expected_response, timeout=15)
        if expected_response not in resp:
            raise IOError("Pump didn't respond with expected value")


if __name__ == "__main__":
    room = BehaviorRoom()
    for skinnerbox in room:
        skinnerbox.withdraw_pumps()