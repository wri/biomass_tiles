### BIOMASS TILES

This script generates the biomass tiles for http://climate.globalforestwatch.org/

Future updates will most likely require changing the following CONFIG params:

- VERSION: this is used in the path for GCS tiles
- END_YY: two digit year for the last year with data
- [BINARY_LOSS_ASSET_ID](#hbt): binary `hansen lossyear.gt(0)` thresholded by treecover
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

<a name='hbt'></a>
---
### Hansen Thresholded Binary Asset

The `BINARY_LOSS_ASSET` is created using the code snippet below. [Here](https://code.earthengine.google.com/53c13b75e91f3e68d882c878c70a7360) is the GEE script for the 2017 data.

```python
""" band name for threshold """
var thresholded_bandnames=function(n){
  return ee.String("loss_").cat(ee.String(n))
}

""" iterate method for creating binary-thresholded-image """
var thresholded_hbinary=function(n,im){
  im=ee.Image(im)
  var band=hbinary.updateMask(htc.gte(ee.Number(n))).unmask(0)
  return im.addBands([band])
}

var thresholds=ee.List([10,15,20,25,30,50,75])
var band_names=thresholds.map(thresholded_bandnames)
var binary_thresholed_image=thresholds.iterate(thresholded_hbinary,ee.Image(-1))
binary_thresholed_image=ee.Image(binary_thresholed_image)
binary_thresholed_image=binary_thresholed_image.select(binary_thresholed_image.bandNames().slice(1))
binary_thresholed_image=binary_thresholed_image.rename(band_names)
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


---

#### NOTES

```
# copy from s3 to gcloud storage
gsutil -m cp -R s3://whrc-v4-processed gs://wri-public/tsc_drivers/2018/global
```

--- 

If there are failures:
1. Get missing files
```
# bash
aws s3 ls whrc-v4-processed
gsutil ls gs://wri-public/tsc_drivers/2018/global
# python
...
aws_df[~aws_df.filename.isin(gs_df.filename)].to_csv('/Users/brook/WRI/code/TSC_Drivers/todo_files.csv',index=False)
```

2. Copy missing files
```
FILES=( 00N_010E_biomass.tif 00N_020E_biomass.tif 00N_030E_biomass.tif ... )
FILES=( 50N_080E_biomass.tif 60N_050E_biomass.tif 80N_180W_biomass.tif )

for f in "${FILES[@]}"
do
    echo "S3->GS: "$f
    gsutil cp s3://whrc-v4-processed/${f} gs://wri-public/tsc_drivers/2018/global/${f}
done
```

3. Upload to GEE
``` 
# to gee
IC_ID=projects/wri-datalab/WHRC/global/carbon
GS_BUCKET=wri-public/tsc_drivers/2018/global


cat filenames.txt | while read -r fname ; do
    echo "GS->GEE: "$fname
    earthengine upload image --asset_id $IC_ID/whrc-${fname} gs://$GS_BUCKET/${fname}.tif
done

earthengine ls $IC_ID >  gee_files.txt

MISSING=( 50N_080E_biomass 60N_050E_biomass 80N_180W_biomass )
MISSING=( 50N_080E_biomass )
for fname in "${MISSING[@]}"
do
    echo "GS->GEE: "$fname
    earthengine upload image --asset_id $IC_ID/whrc-${fname} gs://$GS_BUCKET/${fname}.tif
done


```