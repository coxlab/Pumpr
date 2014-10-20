![awesome logo](https://github.com/coxlab/Pumpr/raw/master/pumpr-logo.png)

Pumpr is a command line interface that fills syringes with water for operant conditioning experiments so you can do more interesting things with your time.
##Installation
Easy! Just open Terminal.app and type:
```bash
pip install pumpr
```

##Usage
###Adding a setup for automatic pumping
First make sure [Phidget WebService](http://www.phidgets.com/docs/Phidget_WebService) is on for the behavior setup you want to add. There's more info on setting up behavior boxes in the [wiki](https://github.com/coxlab/Pumpr/wiki/Setting-up-a-new-visual-operant-conditioning-chamber).
```bash
pumpr add setup10 192.168.0.22 192.168.0.23
```
Here we added a new setup called setup10 (name is arbitrary: it could have been "10" or "awesomesetup" with no spaces) to pumpr. You might want to just call it 10 in real life so you don't have to type so much (you'll see why later). The 3rd argument to pumpr (192.168.0.22) is the IP address for the computer we're calling setup10. The last argument (192.168.0.23) is the IP address for the Startech (IP to serial) adaptor the pumps are connected to. That's all pumpr needs to get started! Pumpr will save all this boring config stuff so all you have to do from now on is type the setup name when you want to do something with it. If you're an ultra pro, you can check out the optional arguments (e.g. changing the Startech listening port) by asking pumpr for help:
```bash
pumpr -h
```
or
```bash
pumpr --help
```
FYI, you can **remove** a setupName if you don't want it anymore by issuing the rm command to pumpr:
```bash
pumpr rm setupName
```
Just keep typing setup names to remove multiple ones in one command:
```bash
pumpr rm coolSetupName anotherSetup thirdSetup
```

###Withdraw syringes
Just tell pumpr to withdraw (wdr) the name of the setup you added in the previous section.
```bash
pumpr wdr setup10
```
You can also tell it to withdraw multiple setups in one command. Let's say you ```pumpr add```ed another setup called "11". To withdraw setup10 and 11, just type this in your Terminal.
```bash
pumpr wdr setup10 11
```
If I ```pumpr add``` setups with the names "10", "11", "12", and "13" (e.g. every training box on one tower) I would type this to withdraw all their syringes:
```bash
pumpr wdr 10 11 12 13
```
###Infuse syringes
To fully infuse syringes (e.g. for when no experiments are happening and water isn't needed in syringes), issue the inf command instead.
```bash
pumpr inf setup10
```
You can also list multiple setup names if you've added them to pumpr:
```bash
pumpr inf setup10 10 11 12 13 anotherAwesomeSetupName
```
###Infuse and withdraw forever
If you want to infuse/withdraw forever (e.g. to clean the tubing system), use the run command:
```bash
pumpr run forever setupName anotherSetup thirdSetupName
```
where "setupName" "anotherSetup" etc are the setup names you added with ```pumpr add```
Be careful though! All the water in the tubing system will slowly spray out, so you have to put something in the operant boxes to catch it (e.g. a waste bin or gauze pads if there isn't much water left in the tubing system).

###Infuse and withdraw for a few cycles
By default, the run argument "cycle" will infuse and withdraw for 3 cycles.
```bash
pumpr run cycle setupName anotherSetup
```
You can customize the number of infuse/withdraw cycles by issuing the -n option. For example, to infuse and withdraw for just 1 cycle, do this:
```bash
pumpr run cycle setupName anotherSetup -n=1
```

###Infuse 1 mL to prime setups for an experiment
Sometimes you have to infuse a little to get water running smoothly before an animal goes into its operant box for a session. You can prime the setups for a session like this:
```bash
pumpr prime setupName setupTwo setupThree etc
```

###Change the number of pump channels on a setup
If one of your setups only has 1 pump channel (e.g. for a go-no-go task where there is only one lick port), tell pumpr its name. For example, if I only have 1 pump channel called "01" on a setup called "coolSetup", I'd do this:
```bash
pumpr config coolSetup channels 01
```