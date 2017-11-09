import ee, gee
import argparse
gee.init()

""" CONFIG """
MAX_PIXS=65500
CRS="EPSG:4326"
SCALE=27.829872698318393
START_Z=12
SPLIT_Z=7
END_Z=2
END_YY=16
Z_LEVELS=[156000,78000,39000,20000,10000,4900,2400,1200,611,305,152,76,38]
THRESHOLDS=[10,15,20,25,30,50,75]
GEE_ROOT='projects/wri-datalab'
GEE_SPLIT_FOLDER='biomass_zsplit'
GCS_TILES_ROOT='biomass/thresholds'
GCS_BUCKET='wri-public'
YEARS=ee.List.sequence(1,END_YY)
BANDS=['year', 'total_biomass_loss', 'density']
CARBON_ASSET_IDS=[
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Neotropic',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Africa',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Australia',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Tropical_Asia',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Palearctic',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Nearctic'
    ]



""""ASSETS
"""
carbon=ee.ImageCollection(CARBON_ASSET_IDS).max().rename(['carbon'])
lossyear=hansen.select(['lossyear'])
threshold=None
treecover_mask=None
loss=None
loss_mask=None


def get_treecover_mask_for_threshold():
    return hansen.select(['treecover2000']).gte(threshold)


def get_loss_for_threshold():
    raw_loss=hansen_thresh_16.select(['loss_'+threshold]);
    return raw_loss.unmask()
                .gt(0)
                .multiply(255)
                .reproject(
                    scale=SCALE,
                    crs=CRS
                ).reduceResolution(
                    reducer=ee.Reducer.mean(),
                    maxPixels=MAX_PIXS
                )


def get_loss_mask():
    return loss.neq(0);



"""GEOMETRY
"""
geom=None
geom_name=None
geoms_ft=ee.FeatureCollection('ft:13BvM9v1Rzr90Ykf1bzPgbYvbb8kGSvwyqyDwO8NI')
def get_geom(name):
    return ee.Feature(geoms_ft.filter(ee.Filter.eq('name',name)).first()).geometry()



"""BAND 1 (loss_yy): two-digit loss year (corresponding to the most carbon lossed)
"""
def loss_by_year(yy):
  return lossyear.eq(yy).updateMask(treecover_mask).multiply(255).toInt().rename(['loss'])


def yy_image(yy):
  yy=ee.Number(yy).toInt()
  return ee.Image(yy).set({'year': yy}).rename(['year'])


def yy_loss_image(yy_img):
      yy_img=ee.Image(yy_img)
      yy=ee.Number(yy_img.get('year')).toInt()
      lby=loss_by_year(yy)
      loss_image = lby.updateMask(lby).multiply(carbon);
      return yy_img.addBands(loss_image).toFloat();


def get_loss_yy():
    year_images=YEARS.map(yy_image)
    year_and_loss_images=ee.ImageCollection.fromImages(year_images.map(yy_loss_image))
    return year_and_loss_images.qualityMosaic('loss')
                            .select('year')
                            .updateMask(loss_mask)
                            .unmask()


"""BAND 2: biomass_loss 
"""
def get_biomass_loss(density):
    return loss.divide(255).multiply(density).updateMask(loss_mask)
    

""" BAND 3: density
"""
def get_density():
    return carbon.unitScale(0, 450).multiply(255).toInt()


""" BIOMASS_IMAGE
"""
def get_biomass_image():
    treecover_mask=get_treecover_mask_for_threshold()
    loss=get_loss_for_threshold()
    loss_mask=get_loss_mask()
    loss_yy=get_loss_yy()
    density=get_density()
    biomass_loss=get_biomass_loss(density)
    return ee.Image([loss_yy,biomass_loss,density]).rename(BANDS).toInt()


"""EXPORT HELPERS: biomass_loss 
"""
def split_asset_name():
    asset_z=SPLIT_Z-1
    if geom_name==DEFAULT_GEOM_NAME:
        name='z{}'.format(asset_z)
    else:
        name='{}_z{}'.format(geom_name,asset_z)
    return name


def split_asset_id():
    return '{}/{}/{}'.format(GEE_ROOT,GEE_SPLIT_FOLDER,split_asset_name())


def tiles_path():
    if geom_name==DEFAULT_GEOM_NAME:
        path='{}/{}'.format(GCS_TILES_ROOT,threshold)
    else:
        path='{}/{}/{}'.format(GCS_TILES_ROOT,geom_name,threshold)
    return path


def tiles_description(path,max_z,min_z):
    return '{}__{}_{}'.format(path.replace('/','__'),max_z,min_z)


def export_tiles(img,max_z,min_z):
    path=tiles_path()
    Export.map.toCloudStorage(
        image=img, 
        description=tiles_description(path,max_z,min_z), 
        bucket=GCS_BUCKET, 
        fileFormat='png', 
        path=path, 
        writePublicTiles=True, 
        maxZoom=max_z, 
        minZoom=min_z, 
        region=geom, 
        skipEmptyTiles=True)


def export_split_asset(img):
    img=img.reproject(scale=Z_LEVELS[SPLIT_Z-1],crs=CRS)
    Export.image.toAsset(
        image=img, 
        description=split_asset_name(), 
        assetId=split_asset_id(), 
        scale=scale, 
        crs=CRS, 
        region=geom, 
        maxPixels=1e13)


""" MAIN
"""
def _inside(args):
    bm_img=ee.Image(split_asset_id())
    export_tiles(name,bm_img,SPLIT_Z-1,END_Z)


def _outside(args):
    bm_img=get_biomass_image()
    export_tiles(name,bm_img,START_Z,SPLIT_Z)
    if (args.split_asset is True) or (args.split_asset.lower()=='true'):
        export_split_asset(bm_img)


def _split_asset(args):
    bm_img=get_biomass_image()
    export_split_asset(bm_img)


def run_tiles(loss_yy,biomass_loss,density):


def main():
    parser=argparse.ArgumentParser(description='HANSEN COMPOSITE')
    parser.add_argument('-g','--geom_name',default=DEFAULT_GEOM_NAME,help='geometry name (https://fusiontables.google.com/DataSource?docid=13BvM9v1Rzr90Ykf1bzPgbYvbb8kGSvwyqyDwO8NI)')
    parser.add_argument('threshold',help='treecover 2000:\none of {}'.format(THRESHOLDS))
    subparsers=parser.add_subparsers()
    parser_inside=subparsers.add_parser('inside', help='export the zoomed in z-levels')
    parser_zasset.add_argument('-a','--split_asset',default=True,help='export spit asset')
    parser_inside.set_defaults(func=_inside)
    parser_outside=subparsers.add_parser('outside', help='export the zoomed out z-levels')
    parser_outside.set_defaults(func=_outside)
    parser_zasset=subparsers.add_parser('zasset', help='export z-level to asset')
    parser_zasset.add_argument('-z','--z_level',default=7,help='max level')
    parser_zasset.set_defaults(func=_zasset)
    args=parser.parse_args()
    if int(args.threshold) in THRESHOLDS: 
        geom_name=args.geom_name
        geom=get_geom(geom_name)
        threshold=None
        args.func(args)
    else: 
        print 'INVALID THRESHOLD:',args.threshold,args


if __name__ == "__main__":
    main()



