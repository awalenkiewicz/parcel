import os, sys, subprocess
sys.path.insert(0,"../../")
sys.path.insert(0,"./")

#import needed libraries
from scipy.io import netcdf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from parcel import parcel

from matplotlib.font_manager import FontProperties
import matplotlib.cm as cm
import numpy as np
from libcloudphxx import common as cm

switch = "pres" #temp
RH=.999999
#r_0=cm.eps*RH*cm.p_vs(T_0)/(p_0-RH*cm.p_vs(T_0))

outbin = '{"radii": {"rght": 0.0001, "moms": [0], "drwt": "wet", "nbin": 26, "lnli": "log", "left": 1e-09}, \
	"radii_aver": {"rght": 1, "moms": [0,1,3], "drwt": "wet", "nbin": 1, "lnli": "log", "left": 1e-6}\
	}'


results = []

if switch == "pres":
    for p_0 in [101300, 102000, 101000, 100000, 99000]: 
        print p_0

        outfile="test_p0_"+str(p_0)+".nc"
        T_0 = 300

        #run parcel model
        parcel(p_0=p_0, T_0=T_0, r_0=cm.eps*RH*cm.p_vs(T_0)/(p_0 - RH*cm.p_vs(T_0)) , outfile=outfile, out_bin=outbin)
        results.append(netcdf.netcdf_file(outfile))


elif switch == "temp":

    for T_0 in [320, 310, 300, 290, 280]: 

        outfile="test_T0_"+str(T_0)+".nc"
        p_0 = 101300

        #run parcel model
        parcel(p_0=p_0, T_0=T_0, r_0=cm.eps*RH*cm.p_vs(T_0)/(p_0 - RH*cm.p_vs(T_0)) , outfile=outfile, out_bin=outbin)
  
        results.append(netcdf.netcdf_file(outfile))

else:
    assert(False)


#plot results
plt.figure(1, figsize=(20,10))
#plot general title

if switch == "pres":
  plt.suptitle("Changes in variables with height \n for p= 1020, 1010, 1000, 990 hPa", fontsize=20)
elif switch == "temp":
   plt.suptitle("Changes in variables with height \n for T= 310, 300, 290, 280 K", fontsize=20)

subplots = []
legend = []

for i in range(6):
	subplots.append(plt.subplot(2,3,i+1))


colors = ["m", "c", "y", "k", "b"]

for i, a in enumerate(results):
	z = a.variables["z"][:]
	subplots[0].plot(a.variables["RH"][:], z, colors[i])
	subplots[1].plot(a.variables["th_d"][:], z, colors[i])
	subplots[2].plot(a.variables["r_v"][:]*1000, z, colors[i])
	subplots[3].plot(a.variables["radii_aver_m0"][:], z, colors[i])	
	subplots[4].plot(a.variables["radii_aver_m1"][:]/a.variables["radii_aver_m0"][:]*1e6, z, colors[i])
	subplots[5].plot(a.variables["radii_aver_m3"][:]/a.variables["radii_aver_m0"][:]*1e6, z, colors[i])

if switch == "pres":
  subplots[0].legend(("p=1020" , "p=1010" , "p=1000" , "p=990"), loc=1, prop=FontProperties(size=10))
elif switch == "temp":
  subplots[0].legend(("T=320", "T=310" , "T=300" , "T=290" , "T=280"), loc=1, prop=FontProperties(size=10))

#choose different names for x axis in each subplots
subplots[0].set_xlabel("RH")
subplots[1].set_xlabel("th_d [K]")
subplots[2].set_xlabel("r_v [g/kg]")
subplots[3].set_xlabel("number of activated droplets \n m0 (>1um) [#/kg]")
subplots[4].set_xlabel("droplet radius \n m1 (>1um) [um]")
subplots[5].set_xlabel("LWC \n m3 (>1um) [um]")

#add some dashed lines, maximum etc
for grid in subplots:
	grid.grid(axis='y', linestyle='--')

#choose the same name for y axis in each subplot
for axis in subplots:
	axis.set_ylabel("z [m]")
	axis.set_yticks(np.arange(0,200,25))
	axis.set_ylim([0,100])

#subplots[0].set_xlim([0.950,1.015])
#subplots[1].set_xlim([0,280])
subplots[3].set_xlim([0*1e7,5*1e7])
#subplots[4].set_xlim([0*1e-9,16*1e-9])
subplots[5].set_xlim([0*1e-9,2*1e-9])


#save figure
if switch == "pres":
  plt.savefig("multiple_plots_of_p.pdf")
elif switch == "temp":
  plt.savefig("multiple_plots_of_T.pdf")

