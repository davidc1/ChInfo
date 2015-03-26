# ChannelInfo

## Dependencies
   * numpy

## Load tool
```
ipython
import getChInfo
chinfo = getChInfo.ChanInfo()
lchan = chinfo.getlarch(5,6,2)
lchan.getlength()
lchan.getnoise(0,0)
chinfo.getlength(5,6,2)
chinfo.getnoise(5,6,2,0,0)
chinfo.getnoise(5,6,2,0,0,5)
```

## Get LArSoft Channel
Use getlarch(crate,slot,femch) function to get a "larchan" object
a "larchan" object contains:
- larch
- crate
- femch
- larwire
- plane
- length [cm]
+ noise, amplitude gain and area gain arrays.
+ each array has 4 elements (one per gain setting)
+ each element is itself a 2-element array:
+ for 1 and 3 usec Shaping times.
- noise [ [[gain=4.7 mV/fC,shaping=1 usec], [4.7,3]], [[7.8,1], [7.8,3]], [[14,1], [14,3]], [[25,1], [25,3]] ]
- ampgain (same)
- areagain (same)
- gainfact (fraction of charge the channel sees from the pulser. 1 or 8/7)
```
lchan = chinfo.getlarch(5,5,31)
lchan.getlength()
lchan.getnoise(0,0)
lchan.getampgain(1,1)
```

## Get Channel Information
The "larchan" object does not need to be called directly:
```
chinfo.getlength(5,5,31)
chinfo.getampgain(5,5,31,0,0)
```

## Cable Mapping Backwards Compatibility
Getter functions for ChanInfo can take an optional 'run number'
as the last argument. This will be used to map to the correct
LArSoft channel according to how cables were mapped during
that run.
If no run number is specified the current (3/24/2015) cable
positions will be used.
Example:
```
chinfo.getlength(5,5,31)
chinfo.getlength(5,5,31,25)
lchan = chinfo.getlarch(5,5,31)
lchan = chinfo.getlarch(5,5,31,25)
```

## Bad Channel List
Jeremy wrote a script that produces lists of "bad channels" (high & low RMS noise)
I have implemented a few functions that returns whether a channel was bad or not,
and if so at which runs.
For example:
If a channel is bad "isBad" prints out text showing at what runs the channel was 
bad and the RMS noise values measured.
The "plotBad" function brings up a plot showing the RMS value for runs in which
the channel was found to be bad. (like this: http://www.nevis.columbia.edu/~dcaratelli/showandtell/BadInfo.png)
```
chinfo.isBad(4,5,1)
chinfo.plotBad(4,5,1)
```
