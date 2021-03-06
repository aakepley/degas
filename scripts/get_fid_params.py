# Purpose: put together a data table with the fiducial parameters for
# the DEGAS sample. 

# Base material:
#       -- z0mgs data table from Leroy et al.  2019 (2019 ApJS 244 24)
#       -- gal_base from Adam Leroy (private communication)
#       -- gal_base_local from Adam Leroy (private communication)

# Notes:
#       -- I don't know how gal_base and gal_base_local differ from one another.
#       -- I also don't know how the z0mgs and gal_base tables differ
#       -- IC0342, NGC0337, and NGC2903 aren't in z0mgs sample, but 
#               appear to be in gal_base sample. But I can find them in the 
#               z0mgs database if I search by PGC. I checked the z0mgs PGC 
#               distance against the distance listed for the sources above and they
#               match. The tags in gal_base also have them in both z0mgs and degas
#       -- IC0342 and NGC4038 have no posang in gal_base. IC342 is more or 
#          less face on and NGC4038 is the antennae (so weird).
#       

# Desired Output Columns:
#       -- PGC number
#       -- Name
#       -- Center (RA, Dec)
#       -- Distance (Mpc) including error and source
#       -- Position angle (PA) including error and source
#       -- Inclination (Inc) including error and source
#       -- SFR
#       -- stellar mass
#       -- distance
#       -- R25 (include error and reference)
#       -- MORPH? (including reference)
#       -- BAR??

#       From degas:
#               -- observed RA
#               -- observed DEC
#               -- observed velocity
#               -- PGC number

#       From z0mgs:
#               -- logM*, e_logM* should be used. The values are NaN in gal_base
#               -- logSFR,e_logSFR,r_logSFR  should be used. The values are NaN in gal_base
#               I will hae to figure out what to do with NGC2903, IC0342, and 
#                       NGC0337 since they aren't in z0mgs.

#       From gal base:
#               -- RA_DEG, DEC_DEG, REF_POS
#               -- DIST_MPC, E_DIST_DEX, DIST_CODE
#               -- R25_DEG, E_R25, REF_R25
#               -- INCL_DEG, E_INCL, REF_INCL -- all galaxies have this
#               -- POSANG_DEG, E_POSANG -- couple of galaxies missing this -- need to figure out which ones
#               -- MORPH, BAR, REF_MORPH

# Output format should be fits binary table (because Erik R. said so).

# Questions:
#       -- Do I just want to copy all the gal_base data to the DEGAS list?
#           -- Advantages is that I have it.
#           -- Disadvantages is that there 's a lot of information that 
#                       I haven't vetted.



from astropy.io import ascii
from astropy.io import fits
from astropy import units as u
import numpy as np
from astropy.table import Table
import os
import math

databaseDir = os.path.join(os.environ['ANALYSISDIR'],'database')
scriptDir = os.environ['SCRIPTDIR']

degas = ascii.read(os.path.join(databaseDir,'dense_survey.cat'))
z0mgs = ascii.read(os.path.join(databaseDir,'apjsab3925t4_mrt.txt'),format='cds')
gal_base = Table.read(os.path.join(databaseDir,'gal_base.fits'),format='fits')

degas_cols = ['NAME','RA','DEC','CATVEL','PGC','DR1']
gal_base_cols = ['RA_DEG','DEC_DEG','REF_POS', 
                 'DIST_MPC','E_DIST_DEX','DIST_CODE','REF_DIST',
                 'R25_DEG','E_R25','REF_R25',
                 'INCL_DEG','E_INCL','REF_INCL',
                 'POSANG_DEG','E_POSANG','REF_POSANG',
                 'MORPH','BAR','REF_MORPH']
z0mgs_cols = ['logM*','e_logM*','logSFR','e_logSFR','r_logSFR']

data = []
galaxy = {}

for line in degas:
    
    # get info from DEGAS file
    galaxy['NAME'] = line['NAME']
    galaxy['PGC'] = line['PGC']
    galaxy['RA_OBS'] = line['RA']
    galaxy['DEC_OBS'] = line['DEC']
    galaxy['VHEL_OBS'] = line['CATVEL']
    galaxy['DR1'] = line['DR1']

    # get info from gal_base
    idx = gal_base['PGC'] == galaxy['PGC'] 
    if np.any(idx):
        for col in gal_base_cols:
            galaxy[col] = gal_base[idx][col].data[0]

    # fix up missing position angle and inclination information
    if math.isnan(galaxy['INCL_DEG']):
        galaxy['INCL_DEG'] = 0.0

    if math.isnan(galaxy['E_INCL']):
        galaxy['E_INCL'] = 10.0

    if math.isnan(galaxy['POSANG_DEG']):
        galaxy['POSANG_DEG'] = 0.0

    if math.isnan(galaxy['E_POSANG']):
        galaxy['E_POSANG'] = 10.0

    # get info from z0mgs
    idx = z0mgs['PGC'] == galaxy['PGC']
    if np.any(idx):
        galaxy['LOGMSTAR'] = z0mgs[idx]['logM*']
        galaxy['E_LOGMSTAR'] = z0mgs[idx]['e_logM*']
        galaxy['LOGSFR'] = z0mgs[idx]['logSFR']
        galaxy['E_LOGSFR'] = z0mgs[idx]['e_logSFR']
        galaxy['REF_LOGSFR'] = z0mgs[idx]['r_logSFR']
    
    # append on galaxy list
    data.append(galaxy)
    
    # clear information for next source    
    galaxy = {}
    
       
t = Table(rows=data)

t.write(os.path.join(scriptDir,'degas_base.fits'),format='fits',overwrite=True)


