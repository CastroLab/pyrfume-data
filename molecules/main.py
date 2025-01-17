# ---
# jupyter:
#   jupytext:
#     formats: py:light,ipynb
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

import pandas as pd
import pyrfume
from pyrfume.odorants import from_cids

# Get list of all archives
archives = pyrfume.list_archives()
print(f'{len(archives)} archives in Pyrfume-Data')

# +
# Exclude archives that are not for sole datasources
exclude = ['mordred', 'morgan', 'molecules', 'embedding', 'prediction_targets', 'tools']

# Exclude Qian 2022 since not currently formatted properly; FlavorDB for tractability (has ~25k molecules)
exclude += ['qian_2022', 'flavordb']

# Exclude archives with no behavior data or molecules.csv file
for arc in archives:
    if arc not in exclude:
        processed = pyrfume.load_manifest(arc)['processed']
        
        if ('molecules.csv' not in processed) or ('behavior' not in ' '.join(processed.keys())):
            exclude.append(arc)
            
print(f'{len(exclude)} archives to be excluded:')
print('\n'.join(exclude))
# -

# Cut those to exclude from archive list
archives = [arc for arc in archives if arc not in exclude]
print(f'{len(archives)} archives contributing to the master molecule list')

# Get molecules
all_molecules = {}
for archive in archives:
    df = pyrfume.load_data(f'{archive}/molecules.csv')   
    all_molecules[archive] = df

# +
# Covnert to dataframe
molecules = pd.concat(all_molecules, axis=0).reset_index().rename(columns={'level_0': 'Archive'})
molecules = molecules.set_index('CID').sort_index()
molecules = molecules[['MolecularWeight', 'IsomericSMILES', 'IUPACName', 'name']]
 
# Drop duplicates (~80 CIDs appear in duplicate because of differences in common name)
molecules = molecules[~molecules.index.duplicated()]

print(f'{molecules.shape[0]} unique molecules')
molecules.head()

# +
# Usage
usage = pd.DataFrame(index=molecules.index)
for archive in archives:
    archive_mols = all_molecules[archive]
    usage[archive] = usage.index.isin(archive_mols.index).astype(int)

print(usage.shape)
usage.head()
# -

# Write to disk
molecules.to_csv('molecules.csv')
usage.to_csv('usage.csv')
