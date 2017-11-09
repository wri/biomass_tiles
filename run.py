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
treecover_mask=None
loss=None
loss_mask=None


def get_treecover_mask_for_threshold(threshold):
    return hansen.select(['treecover2000']).gte(threshold)


def get_loss_for_threshold(threshold):
    raw_loss=hansen_thresh_16.select(['loss_'+THRESHOLD]);
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







"""EXPORT HELPERS: biomass_loss 
"""
def export_tiles(name,img,region,top=True):
  if top:
    max_z=START_Z
    min_z=SPLIT_Z
  else:
    max_z=SPLIT_Z-1
    min_z=END_Z

  Export.map.toCloudStorage(
    image=img, 
    description=name, 
    bucket='wri-public', 
    fileFormat='png', 
    # path='biomass/tiles/'+name, 
    path='biomass/tests/'+name, 
    writePublicTiles=True, 
    maxZoom=max_z, 
    minZoom=min_z, 
    region=region, 
    skipEmptyTiles=True)


          
def export_split_asset(name,img,region):
  scale=Z_LEVELS[SPLIT_Z-1]
  img.reproject(scale=scale,
                crs=CRS)
  Export.image.toAsset(
    image=img, 
    description=name, 
    assetId='projects/wri-datalab/biomass_zsplit/'+name, 
    scale=scale, 
    crs=CRS, 
    region=region, 
    maxPixels=1e13)


""" MAIN
"""

def run():
    bm_img=ee.Image([loss_yy,biomass_loss,density]).rename(BANDS).toInt()


def main():
    parser=argparse.ArgumentParser(description='HANSEN COMPOSITE')
    parser.add_argument('-g','--geom_name',default=DEFAULT_GEOM_NAME,help='geometry name (https://fusiontables.google.com/DataSource?docid=13BvM9v1Rzr90Ykf1bzPgbYvbb8kGSvwyqyDwO8NI)')
    parser.add_argument('threshold',help='treecover 2000:\none of {}'.format(THRESHOLDS))
    subparsers=parser.add_subparsers()
    parser_inside=subparsers.add_parser('inside', help='export the zoomed in z-levels')
    parser_inside.add_argument('-max','--max',default=12,help='max level')
    parser_inside.add_argument('-min','--min',default=7,help='min level')
    parser_inside.add_argument('-a','--asset',default='True',help='export min level to asset')
    parser_inside.set_defaults(func=_inside)
    parser_outside=subparsers.add_parser('outside', help='export the zoomed out z-levels')
    parser_outside.add_argument('-max','--max',default=6,help='max level')
    parser_outside.add_argument('-min','--min',default=2,help='min level')
    parser_outside.set_defaults(func=_outside)
    parser_zasset=subparsers.add_parser('zasset', help='export z-level to asset')
    parser_zasset.add_argument('-z','--z_level',default=7,help='max level')
    parser_zasset.set_defaults(func=_zasset)
    args=parser.parse_args()
    if int(args.threshold) in THRESHOLDS: 
        geom_name=args.geom_name
        geom=get_geom(geom_name)
        args.func(args)
    else: 
        print 'INVALID THRESHOLD:',args.threshold,args


if __name__ == "__main__":
    main()



