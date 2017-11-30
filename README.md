### BIOMASS TILES

This script generates the biomass tiles for http://climate.globalforestwatch.org/

Future updates will most likely require changing the following CONFIG params:

- VERSION: this is used in the path for GCS tiles
- END_YY: two digit year for the last year with data
- BINARY_LOSS_ASSET_ID: binary `hansen lossyear.gt(0)` thresholded by treecover
- HANSEN_ASSET_ID: hansen asset with umd-lossyear
- CARBON_ASSET_IDS: list of carbon assets

---
#### USAGE

Tiles must generated in two steps: the zoomed-in (inside) tiles and then the zoomed-out (outside) tiles. Here is an example for treecover threshold of 10.

Start by exporting the split-asset and tiles for zoom levels 12-7:
```bash
python run.py 10 inside
```

Once the split-asset-task has completed you can export the other zoom-levels:
```bash
python run.py 10 outside
```


Here are the docs:

```bash
biomass|master $ python run.py -h
gee.init: USER_ACCOUNT 
usage: run.py [-h] [-p NAME_PREFIX] [-g GEOM_NAME]
              threshold {outside,inside,split_asset} ...

HANSEN COMPOSITE

positional arguments:
  threshold             treecover 2000: one of [10, 15, 20, 25, 30, 50, 75]
  {outside,inside,split_asset}
    outside             export the zoomed out z-levels
    inside              export the zoomed in z-levels
    split_asset         export z-level split asset

optional arguments:
  -h, --help            show this help message and exit
  -p NAME_PREFIX, --name_prefix NAME_PREFIX
                        prefix for asset name and tiles path
  -g GEOM_NAME, --geom_name GEOM_NAME
                        geometry name (https://fusiontables.google.com/DataSou
                        rce?docid=13BvM9v1Rzr90Ykf1bzPgbYvbb8kGSvwyqyDwO8NI)


# the 'inside' run has a parameter that allows you to skip the split-asset export
python run.py 10 inside -h
gee.init: USER_ACCOUNT 
usage: run.py threshold inside [-h] [-a SPLIT_ASSET]

optional arguments:
  -h, --help            show this help message and exit
  -a SPLIT_ASSET, --split_asset SPLIT_ASSET
                        export spit asset
```




---

###### FIRST PASS JS-VERSION
https://code.earthengine.google.com/efd0994b074c8fa121b27fd8e499bbb6

###### ORIGNIAL THAU JS-VERSION
https://code.earthengine.google.com/68e1d4a7e2ee621128fbd9d6bfe0c40a

###### BEN's NOTES
https://github.com/Vizzuality/data_sci_tutorials/blob/master/work/GFW_climate_biomass_tiles.ipynb

###### GFW-CLIMATE CODE BASE
https://github.com/Vizzuality/gfw-climate