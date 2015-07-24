# This Python file uses the following encoding: utf-8
import sys
sys.path.insert(0, "../")
sys.path.insert(0, "./")
sys.path.insert(0, "plots/one_simulat/")
from scipy.io import netcdf
import numpy as np
import pytest
import subprocess

from parcel import parcel
from spectrum_plot import plot_spectrum

import pdb

@pytest.fixture(scope="module")
def data(request):
    """
    Run parcel simulation and return opened netdcf file
    """
    outfile = "test_spectrum.nc"

    # running parcel model for open / closed chem system  ...
    parcel(dt = .5, sd_conc = 1024, outfreq = 40,  outfile=outfile,\
           out_bin = '{"linwradii": {"rght": 0.0001, "moms": [0, 1, 3], "drwt": "wet", "nbin": 26, "lnli": "lin", "left": 1e-09}, "lindradii": {"rght": 1e-06, "moms": [0, 1, 3], "drwt": "dry", "nbin": 26, "lnli": "lin", "left": 1e-09}, "wradii": {"rght": 0.0001, "moms": [0, 1, 3], "drwt": "wet", "nbin": 26, "lnli": "log", "left": 1e-09}, "dradii": {"rght": 1e-06, "moms": [0, 1, 3], "drwt": "dry", "nbin": 26, "lnli": "log", "left": 1e-09}}')

    data = netcdf.netcdf_file(outfile, "r")

    # removing all netcdf files after all tests
    def removing_files():
        subprocess.call(["rm", outfile])

    request.addfinalizer(removing_files)
    return data


@pytest.mark.parametrize("name_spect", ["wradii_r_wet", "dradii_r_dry", #log bins
                                        "linwradii_r_wet", "lindradii_r_dry"]) # lin bins
def test_bin_checker(data, name_spect, eps_d=1.e-14):
    """
    Check if bin sizes stored in the netcdf file are equal to the difference between bin edges 
    (done for all but last bin because in output files we store bin left edges)             
    """
    r_nc  = data.variables[name_spect][:]
    dr_nc = data.variables[name_spect.replace("_r_", "_dr_" )][:]
    dr = np.empty(r_nc.shape[0] - 1)
    dr[:] = (r_nc[1:] - r_nc[0:-1]) 
    
    # TODO
    # why this works ...
    #dj -  now it doesn't ;-) don't know why it did work, but there are some small diff.
   # for it in range(dr.shape[0]):
   #     assert  dr[it] == dr_nc[it]
     # .... while this doesn't?
     #assert (dr[:] == dr_nc[:-1]).all()
    assert np.isclose(dr, dr_nc[:-1], atol=0, rtol=eps_d).all()


@pytest.mark.parametrize("var", ["wradii_r_wet", "wradii_dr_wet", "dradii_r_dry", 
                                 "dradii_dr_dry","linwradii_r_wet", "linwradii_dr_wet", 
                                 "lindradii_r_dry", "lindradii_dr_dry"])
def test_spectrum_diff(data, var, eps_d = 1e-15):
    """
    Compare the results with the referential simulation
    (stored in refdata folder)                                             
    """
    # the referential simulation against which we compare ...
    f_ref  = netcdf.netcdf_file("unit_test/refdata/test_spectrum.nc", "r")

    assert np.isclose(f_ref.variables[var][:], data.variables[var][:],atol=0, rtol=eps_d).all()


# ... and 0th, 1st, 3rd moment of wet and dry radius size distribution             
# TODO - are those epsilons reasonable??   dj - NO!!                                 
@pytest.mark.parametrize("mom, eps", [("wradii_m0", 1.e-15), ("dradii_m0", 1e-15), 
                                      ("lindradii_m0", 1e-15), ("linwradii_m0", 1e-15),
                                      ("wradii_m1", 4e-5), ("dradii_m1", 5e-15), 
                                      ("lindradii_m1", 4e-15), ("linwradii_m1", 2e-6),
                                      ("wradii_m3", 2e-4), ("dradii_m3", 2e-14), 
                                      ("lindradii_m3", 2e-14), ("linwradii_m3", 5e-6)])

def test_mom_checker(data, mom, eps):
    f_ref  = netcdf.netcdf_file("unit_test/refdata/test_spectrum.nc", "r")
    refdata = f_ref.variables[mom][:]
    cmpdata = data.variables[mom][:]
    refdata = np.reshape(refdata, np.product(refdata.shape))
    cmpdata = np.reshape(cmpdata, np.product(cmpdata.shape))

    assert np.isclose(cmpdata, refdata, atol=0, rtol=eps).all(),\
        "differs e.g. " + str(mom) + "; max(ref diff) = " +\
        str(np.where(refdata != 0.,abs((cmpdata - refdata) / refdata), abs(cmpdata - refdata)).max())


def test_spectrum_plot(data):
    """
    plot dry and wet radius size distribution
    """
    plot_spectrum(data, outfolder = "plots/outputs/")
