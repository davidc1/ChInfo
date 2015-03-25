import numpy as np
import os,sys
import warnings


# A function that deterimnes the mapping version to use accoridng to run number
# version "oldest"  (3rd dictionary in list) -> Run <= 57
# version "old"     (2nd dictionary in list) -> Run <= 92
# version "current" (1st dictionary in list) -> All other runs
def getDictionaryVersion(r):
    v = 0
    if (r < 0):
        raise ValueError("Run Number less than 0. Error!")
    if (r <= 57):
        v = 2
    elif (r <= 92):
        v = 1
    else:
        v = 0
    return v

# Defining class for LArTF Production [Crate, Slot, Femch]
# Channel labeling
class lartfpos:
    def __init__(self,crate,slot,femch):
        self.crate = crate
        self.slot = slot
        self.femch = femch
    def __str__(self):
        return "Crate %d. Slot %d. Femch %d"%(self.crate,self.slot,self.femch)
    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
    def __hash__(self):
        return hash((self.crate,self.slot,self.femch))

# Defining a class for the info on a LArTF Channel itself
class larchan:
    def __init__(self,larch,crate,slot,femch,larwire,plane):
        self.larch  = larch
        self.crate = crate
        self.slot = slot
        self.femch = femch
        self.larwire = larwire
        self.plane = plane
        self.length = 0
        self.noise = []
        self.ampgain = []
        self.areagain = []
        self.gainfact = 0
    # Setters
    def setlength(self,length):
        self.length = length
    def setampgain(self,gain):
        self.ampgain = gain
    def setareagain(self,gain):
        self.areagain = gain
    def setnoise(self,noise):
        self.noise = noise
    def setgainfact(self,fact):
        self.gainfact = fact
    # Getters
    def getlarch(self):
        return self.larch
    def getcrate(self):
        return self.crate
    def getslot(self):
        return self.slot
    def getfemch(self):
        return self.femch
    def getCSF(self):
        return [self.crate,self.slot,self.femch]
    def getwire(self):
        return sef.larwire
    def getplane(self):
        return self.plane
    def getlength(self):
        return self.length
    def getampgain(self,gain,shaping):
        if ( (gain > 3) or (shaping > 1) or (gain < 0) or (shaping < 0) ):
            print "Gains: [0 = 4.7, 1 = 7.8, 2 = 14, 3 = 25]. Shapings: [0 = 1, 1 = 3]"
            return
        return self.ampgain[gain][shaping]
    def getareagain(self,gain,shaping):
        if ( (gain > 3) or (shaping > 1) or (gain < 0) or (shaping < 0) ):
            print "Gains: [0 = 4.7, 1 = 7.8, 2 = 14, 3 = 25]. Shapings: [0 = 1, 1 = 3]"
            return
        return self.areagain[gain][shaping]
    def getgain(self,area,gain,shaping):
        if ( (gain > 3) or (shaping > 1) or (gain < 0) or (shaping < 0) ):
            print "Gains: [0 = 4.7, 1 = 7.8, 2 = 14, 3 = 25]. Shapings: [0 = 1, 1 = 3]"
            return
        if (area):
            return self.areagain[gain][shaping]
        return self.ampgain[gain][shaping]
    def getnoise(self,gain,shaping):
        if ( (gain > 3) or (shaping > 1) or (gain < 0) or (shaping < 0) ):
            print "Gains: [0 = 4.7, 1 = 7.8, 2 = 14, 3 = 25]. Shapings: [0 = 1, 1 = 3]"
            return
        return self.noise[gain][shaping]
    def getgainfact(self):
        return self.gainfact

class ChanInfo():
    def __init__(self):
        # Load default text files if they can be found
        self.fname = ['','','']
        success = 0
        if ((os.path.isfile('fnal_map.txt'))==True):
            self.fname[0] = 'fnal_map.txt'
            success +=1 
        if ((os.path.isfile('fnal_map_old.txt'))==True):
            self.fname[1] = 'fnal_map_old.txt'
            success += 1
        if ((os.path.isfile('fnal_map_oldest.txt'))==True):
            self.fname[2] = 'fnal_map_oldest.txt'
            success += 1
        # dictionary mapping [crate,slot,femch] -> LArSoft Channel
        self.lardict = [{},{},{}]
        # dictionary mapping LArSoft Channel num to larsoft wire object
        self.chandict = {}
        if (success == 3):
            self.makeDictionary()


    def makeDictionary(self):
        # make sure input file has been specified
        if ( (self.fname[0] == "") or (self.fname[1] == "") or (self.fname[2] == "") ):
            print "File name not yet specified. Cannot create dictionary"
            return
        if ( ((os.path.isfile(self.fname[0]))==False) or ((os.path.isfile(self.fname[1]))==False) or ((os.path.isfile(self.fname[2]))==False)):
            print "Path to file not found."
            return
        # open file
        for n in xrange(len(self.fname)):
            infile = open(self.fname[n],'r')
            # load file contents to numpy array
            ch = np.loadtxt(infile,delimiter=' ',
                            dtype={'names':('crate','slot','femch','larch','larwire','plane','length',
                                            'rms01','rms03','rms11','rms13','rms21','rms23','rms31','rms33',
                                            'amp01','amp03','amp11','amp13','amp21','amp23','amp31','amp33',
                                            'area01','area03','area11','area13','area21','area23','area31','area33',
                                            'gainnorm'),
                                   'formats':('u1','u1','u2','u2','u2','u1','f3',
                                              'f2','f2','f2','f2','f2','f2','f2','f2',
                                              'f2','f2','f2','f2','f2','f2','f2','f2',
                                              'f2','f2','f2','f2','f2','f2','f2','f2',
                                              'f2')})
            # loop over all entry and populate the dictionaries
            for i in xrange(len(ch)):
                # Set [crate,slot,femch] position for dictonary
                thischan = lartfpos(ch['crate'][i],ch['slot'][i],ch['femch'][i])
                # now create larsoft wire object
                thislar = larchan(ch['larch'][i],ch['crate'][i],ch['slot'][i],ch['femch'][i],ch['larwire'][i],ch['plane'][i])
                thislar.setlength(ch['length'][i])
                thisnoise = [ [ch['rms01'][i],ch['rms03'][i]], [ch['rms11'][i],ch['rms13'][i]], [ch['rms21'][i],ch['rms23'][i]], [ch['rms31'][i],ch['rms33'][i]] ]
                thisamp   = [ [ch['amp01'][i],ch['amp03'][i]], [ch['amp11'][i],ch['amp13'][i]], [ch['amp21'][i],ch['amp23'][i]], [ch['amp31'][i],ch['amp33'][i]] ]
                thisarea  = [ [ch['area01'][i],ch['area03'][i]], [ch['area11'][i],ch['area13'][i]], [ch['area21'][i],ch['area23'][i]], [ch['area31'][i],ch['area33'][i]] ]
                thislar.setnoise(thisnoise)
                thislar.setampgain(thisamp)
                thislar.setareagain(thisarea)
                thislar.setgainfact(ch['gainnorm'][i])
                # Add to dictionary
                self.lardict[n][thischan] = thislar
                self.chandict[thislar.larch] = thislar
            del ch
            infile.close()
        print "done filling dictionary!"


    def isinputvalid(self,crate,slot,femch,r):
        # First check that the run number exists
        v = 0
        try:
            v = getDictionaryVersion(r)
        except ValueError as detail:
            raise ValueError(detail)
        # now check that this [crate,slot,femch] maps to a larchannel
        x = lartfpos(crate,slot,femch)
        if ( (x in self.lardict[v]) == False):
            raise ValueError("[Crate,Slot,Femch] Not found in Dictionary")
        # If all is good, return the larch object
        return x,v
        

    def getlarch(self,crate,slot,femch,r=100):
        try:
            x,v = self.isinputvalid(crate,slot,femch,r)
            return self.lardict[v][x]
        except ValueError as detail:
            print "Error: ",detail

    def getlarchnum(self,crate,slot,femch,r=100):
        try:
            x,v = self.isinputvalid(crate,slot,femch,r)
            return self.lardict[v][x].getlarch()
        except ValueError as detail:
            print "Error: ",detail

    def getwirenum(self,crate,slot,femch,r=100):
        try:
            x,v = self.isinputvalid(crate,slot,femch,r)
            return self.lardict[v][x].getwire()
        except ValueError as detail:
            print "Error: ",detail

    def getplane(self,crate,slot,femch,r=100):
        try:
            x,v = self.isinputvalid(crate,slot,femch,r)
            return self.lardict[v][x].getplane()
        except ValueError as detail:
            print "Error: ",detail

    def getlength(self,crate,slot,femch,r=100):
        try:
            x,v = self.isinputvalid(crate,slot,femch,r)
            return self.lardict[v][x].getlength()
        except ValueError as detail:
            print "Error: ",detail

    def getnoise(self,crate,slot,femch,gain,shaping,r=100):
        try:
            x,v = self.isinputvalid(crate,slot,femch,r)
            return self.lardict[v][x].getnoise(gain,shaping)
        except ValueError as detail:
            print "Error: ",detail

    def getampgain(self,crate,slot,femch,gain,shaping,r=100):
        try:
            x,v = self.isinputvalid(crate,slot,femch,r)
            return self.lardict[v][x].getampgain(gain,shaping)
        except ValueError as detail:
            print "Error: ",detail

    def getareagain(self,crate,slot,femch,gain,shaping,r=100):
        try:
            x,v = self.isinputvalid(crate,slot,femch,r)
            return self.lardict[v][x].getareagain(gain,shaping)
        except ValueError as detail:
            print "Error: ",detail

    def getgainfact(self,crate,slot,femch,r=100):
        try:
            x,v = self.isinputvalid(crate,slot,femch,r)
            return self.lardict[v][x].getgainfact()
        except ValueError as detail:
            print "Error: ",detail

    def getCSF(self,larch):
        if (larch in self.chandict):
            chch = self.chandict[larch]
            return [chch.crate,chch.slot,chch.femch]
        else:
            print "Channel not found!"
    
