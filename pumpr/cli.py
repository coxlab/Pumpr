"""Pumpr.

Usage:
    pumpr add <setupName> <phidgetWebServiceIPaddress> <StartechAdaptorIPaddress> [--phidgetPort=<portNum>] [--startechPort=<portNum>]
    pumpr rm <setupName>...
    pumpr run forever <setupName>...
    pumpr run cycle <setupName>... [-n=<numCycles>] [--primePumps=<boolean>]
    pumpr inf <setupName>...
    pumpr wdr <setupName>...
    pumpr prime <setupName>...
    pumpr config <setupName> channels <chans>...

Options:
    -h --help                   Show this screen.
    --version                   Show version.
    --phidgetPort=<portNum>     Phidget WebService listening port number [default: 5001].
    --startechPort=<portNum2>   Telnet listening port for Startech IP (syringe pump) adapter [default: 100].
    -n=<numCycles>              Number of times syringe pumps will infuse and withdraw to prep for session and/or wash [default: 3].
    --primePumps=<boolean>      Set to False and pumps will not infuse 1 mL to get water flowing for a session [default: True].
"""
from docopt import docopt

def parseCommandLineArgs():
    args = docopt(__doc__, version="pumpr-0.1.0")
    return args
