import os,sys
from math import exp

def get_options():
    import os, os.path
    from optparse import OptionParser
    parser = OptionParser()    
    parser.add_option("-n", "--nriders", dest="nriders", help="number of riders", type="int", default=None)
    parser.add_option("-v", "--vmodel", dest="vmodel",  type="string", default="exp", help="velocity update model")
    parser.add_option("-i", "--rider_gaps_file", dest="rider_gaps_file",  type="string", default="rider_gaps.in", help="file containing initial gaps")
    parser.add_option("-o", "--race_file", dest="race_file",  type="string", default="race.out", help="output file for plotting")
    (options, args) = parser.parse_args()
    return options, args
    

class Rider(object):
    def __init__(self,x,v,gap,rider_num):
        self.x = x
        self.v = v
        self.gap = gap
        self.rider_num = rider_num
        self.riderchain_len = 0

def get_pos(rider):
    return rider.x


def minsec2hrs(s):
    """ string s e.g. "2.33" or "2:33".  convert to 2 minutes, 33 seconds = 2/60 + 33 / 3600 hours """
    import re
    s = re.split(':|\.', s)
    h = float(s[0])/60.0
    if len(s)>1:
        h += float(s[1])/3600.0
    return h

class BikeRace(object):
    def __init__(self):
        self.riders = None
        self.dt = 0.001   # hours
        self.dtout = 0.005  # hours
        self.t = 0
        self.last_print_time = -1;
        self.race_length = 25 # miles
        self.max_riderchain_gap_feet = 10 # feet
        self.max_riderchain_gap = self.max_riderchain_gap_feet / 5280. # miles
        self.vmax = 30  # mph
        self.vmin = 20
        self.vdecay = 3  # units: group size
        self.v0 = 15.0
        self.v1 = 1

    def vfun(self,glen):
        if (self.options.vmodel == "exp"):
            v = self.vmax - (self.vmax-self.vmin)*exp(-(glen-1)/self.vdecay)
        else:
            v = self.v0 + self.v1 * (glen-1)
        return v

    def setup(self, options):
        self.options = options

        if (options.nriders != None):
            print "random start list of n riders: unimplemented"
            sys.exit()

        ## initial gaps are _time_ gaps, in minutes.seconds, convert t hours
        gaps = [minsec2hrs(x) for x in file(options.rider_gaps_file).readlines()]
        self.riders = [Rider(0,0,gaps[i],i) for i in range(len(gaps))]
        self.update_speeds()

        self.fout = file(options.race_file, "w")
        self.fout.write("# nrider: %d\n"  % (len(self.riders)))
        self.fout.write("#time pos vel gap0 glen place0\n")


    def run(self, options):
        self.dump_riders()
        while self.riders[-1].x < self.race_length:
            self.advance_time()
            self.sort_riders()
            self.dump_riders()
            self.update_speeds()

    def dump_riders(self):
        print "riders at time = %f" % self.t
        print "pos    speed   initial_gap   chain_len   rider_num"  
        for i in range(len(self.riders)):
            r = self.riders[i]
            print r.x, r.v, r.gap, r.riderchain_len, r.rider_num
        if (self.t - self.last_print_time > self.dtout):
            self.last_print_time = self.t
            for i in range(len(self.riders)):
                r = self.riders[i]            
                self.fout.write("%f  %f  %f  %f  %d  %d\n" % (self.t, r.x, r.v, r.gap, r.riderchain_len, r.rider_num))
            
    def advance_time(self):
        eps = 1e-6
        for i in range(len(self.riders)):
            if (self.t + eps >= self.riders[i].gap):
                self.riders[i].x += self.riders[i].v * self.dt
        self.t += self.dt

    def sort_riders(self):
        self.riders = sorted(self.riders, key=get_pos, reverse=True)
    
    def update_speeds(self):
        # assuming riders.x is sorted, we are counting how many riders make a "chain", then
        # assigning speed based on that.        
        i = 0
        eps = 1e-6
        while i < len(self.riders):
            if (self.t + eps < self.riders[i].gap):
                return # only update riders who are riding!
            j = 1
            ii = i
            while (ii < len(self.riders)-1 and self.riders[ii].x - self.riders[ii+1].x < self.max_riderchain_gap
                   and self.t + eps >= self.riders[ii].gap and self.t + eps >= self.riders[ii+1].gap):
                j += 1
                ii += 1
            for k in range(j):
                self.riders[i+k].v = self.vfun(j)
                self.riders[i+k].riderchain_len = j
            i += j

if __name__=="__main__":
    options, args = get_options()
    race = BikeRace()
    race.setup(options)
    race.run(options)
    race.fout.close()
