import ee, gee
import argparse
gee.init()




""" CONFIG
"""
VERSION='v3'
MAX_PIXS=65500
CRS="EPSG:4326"
SCALE=27.829872698318393
START_Z=12
SPLIT_Z=6
END_Z=2
END_YY=16
YEARS=ee.List.sequence(1,END_YY)
Z_LEVELS=[156000,78000,39000,20000,10000,4900,2400,1200,611,305,152,76,38]
THRESHOLDS=[10,15,20,25,30,50,75]
DEFAULT_GEOM_NAME='tropics'
GEE_ROOT='projects/wri-datalab'
GEE_SPLIT_FOLDER='biomass_zsplit'
GCS_TILES_ROOT='biomass/{}'.format(VERSION)
GCS_BUCKET='wri-public'
BANDS=['year', 'total_biomass_loss', 'density']
CARBON_ASSET_IDS=[
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Neotropic',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Africa',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Australia',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Tropical_Asia',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Palearctic',
      'users/mfarina/Biomass_Data_MapV3/WHRC_Biomass_30m_Nearctic'
    ]

    


"""PARAMS
"""
threshold=None
name_prefix=None
geom=None
geom_name=None




""""ASSETS
"""
hansen_thresh_16=ee.Image('projects/wri-datalab/HansenComposite_16')
hansen_binary_loss_16=ee.Image('projects/wri-datalab/HANSEN_BINARY_LOSS_16')
hansen=ee.Image('UMD/hansen/global_forest_change_2016_v1_4')
whrc_carbon=ee.ImageCollection(CARBON_ASSET_IDS).max().rename(['carbon'])
hansen_lossyear=hansen.select(['lossyear'])




"""GEOMETRY
"""
geoms_ft=ee.FeatureCollection('ft:13BvM9v1Rzr90Ykf1bzPgbYvbb8kGSvwyqyDwO8NI')
def get_geom(name):
    f=geoms_ft.filter(ee.Filter.eq('name',name)).first()
    if f.getInfo():
        return ee.Feature(f).geometry()






"""BIOMASS CLASS
"""
class BIOMASS(object):


    ############################################    
    # 
    #
    #   STATIC METHODS
    #
    #
    ############################################

    
    @staticmethod
    def _zmean(img,z,init_scale=SCALE):
        reducer=ee.Reducer.mean()
        return BIOMASS._reduce(img,z,init_scale,reducer)


    @staticmethod
    def _zmode(img,z,init_scale=SCALE):
        img=img.updateMask(img.gt(0))
        reducer=ee.Reducer.mode()
        return BIOMASS._reduce(img,z,init_scale,reducer)


    @staticmethod
    def _reduce(img,z,init_scale,reducer):
        if (z==START_Z):
            return img
        else:
            return img.reproject(
                        scale=init_scale,
                        crs=CRS
                ).reduceResolution(
                        reducer=reducer,
                        maxPixels=MAX_PIXS
                ).reproject(
                        scale=Z_LEVELS[z],
                        crs=CRS
                )


    ############################################    
    # 
    #
    #   PUBLIC METHODS
    #
    #
    ############################################


    """constructor

        ARGS:
            assets:
                * for each of the assets below we use the raw data or,
                  for lower zoom levels, the "split_data" output asset.

                - loss (binary hansen loss image: 'projects/wri-datalab/HANSEN_BINARY_LOSS_16' or latest)
                - lossyear (hansen lossyear band)
                - carbon (carbon data)

            config:
                - target_z: the z_level of the final image.
                - data_z: the z_level of the input assets described above

    """
    def __init__(self,loss,lossyear,carbon,target_z,data_z=START_Z):
        self._image=None
        self._init_assets(loss,lossyear,carbon,target_z,Z_LEVELS[data_z])
        

    """image

        returns ee.image  
            - bands: ['year', 'total_biomass_loss', 'density']
            - nominalScale: Z_LEVELS[z]
            - export to tiles at zoom level z
    
    """
    def image(self):
        if not self._image:
            loss_mask=self.loss.gt(0)
            loss_yy=self._get_loss_yy().updateMask(loss_mask)
            density=self._get_density()
            biomass_loss=self._get_biomass_loss(density).updateMask(loss_mask)
            self._image=ee.Image([loss_yy,biomass_loss,density]).unmask()
            self._image=self._image.rename(BANDS).toInt()
        return self._image
    

    """split_data

        returns ee.image  
            - bands: [loss,lossyear,carbon] 
            - nominalScale: Z_LEVELS[z]
            - save as asset to get around "too many input per out pixels" error

    """
    def split_data(self):
        return self.loss.addBands([self.lossyear,self.carbon])


    ############################################    
    # 
    #
    #   INTERNAL METHODS
    #
    #
    ############################################


    """initialize assets: reduce loss/lossyear/carbon data to target z_level
    """
    def _init_assets(self,loss,lossyear,carbon,z,init_scale):
        self.loss=loss.reproject(crs=CRS,scale=Z_LEVELS[z]).rename(['loss'])
        self.lossyear=self._zmode(lossyear,z,init_scale).rename(['lossyear'])
        self.carbon=self._zmean(carbon,z,init_scale).rename(['carbon'])
        self.lossyear_mask=self.lossyear.gt(0)


    """BAND 1 (loss_yy): two-digit loss year (corresponding to the most carbon loss)
    """
    def _get_loss_yy(self):

        def _yy_loss_image(yy):
            yy=ee.Number(yy).toInt()
            lby=self.lossyear.eq(yy).multiply(255).toInt()
            loss_image = lby.multiply(self.carbon);
            yy_loss_img=ee.Image(yy).addBands(loss_image).rename(['year','loss'])
            return yy_loss_img.updateMask(self.lossyear_mask).toFloat()
        
        year_and_loss_images=ee.ImageCollection.fromImages(YEARS.map(_yy_loss_image))
        return year_and_loss_images.qualityMosaic('loss').select(['year']).unmask()


    """BAND 2: biomass_loss 
    """
    def _get_biomass_loss(self,density):
        return self.loss.divide(255.0).multiply(density)
        

    """ BAND 3: density
    """
    def _get_density(self):
        return self.carbon.unitScale(0, 450).multiply(255).toInt()






"""EXPORT HELPERS: 
"""
def split_asset_name():
    asset_z=SPLIT_Z+1
    if geom_name==DEFAULT_GEOM_NAME:
        name='{}_tc{}_z{}'.format(VERSION,threshold,asset_z)
    else:
        name='{}_{}_tc{}_z{}'.format(geom_name,VERSION,threshold,asset_z)
    return '{}{}'.format(name_prefix,name)


def split_asset_id():
    return '{}/{}/{}'.format(GEE_ROOT,GEE_SPLIT_FOLDER,split_asset_name())


def tiles_path():
    if geom_name==DEFAULT_GEOM_NAME:
        path='{}/{}'.format(GCS_TILES_ROOT,threshold)
    else:
        path='{}/{}/{}'.format(GCS_TILES_ROOT,geom_name,threshold)
    return '{}{}'.format(name_prefix,path)


def tiles_description(path,z,min_z=None):
    dpath=path.replace('/','__')
    if (z!=min_z):
        return '{}__{}_{}'.format(dpath,z,min_z)
    else:
        return '{}__{}'.format(dpath,z)


def export_tiles(img,max_z,min_z):
    path=tiles_path()
    task=ee.batch.Export.map.toCloudStorage(
        image=img, 
        description=tiles_description(path,max_z,min_z), 
        bucket=GCS_BUCKET, 
        fileFormat='png', 
        path=path, 
        writePublicTiles=False, 
        maxZoom=max_z, 
        minZoom=min_z, 
        region=geom.coordinates().getInfo(), 
        skipEmptyTiles=True)
    run_task(task)


def export_split_asset(img):
    scale=Z_LEVELS[SPLIT_Z+1]
    task=ee.batch.Export.image.toAsset(
        image=img, 
        description=split_asset_name(), 
        assetId=split_asset_id(), 
        scale=scale, 
        crs=CRS, 
        region=geom.coordinates().getInfo(), 
        maxPixels=1e13)
    run_task(task)


def run_task(task):
    task.start()
    print task.status()






""" MAIN
"""
def _outside(args):
    split_data=ee.Image(split_asset_id())
    loss=split_data.select(['loss'])
    lossyear=split_data.select(['lossyear'])
    carbon=split_data.select(['carbon'])
    for z in range(END_Z,SPLIT_Z+1):
        bmz=BIOMASS(loss,lossyear,carbon,z,SPLIT_Z+1)
        export_tiles(bmz.image(),z,z)


def _inside(args):
    loss=hansen_binary_loss_16.select(['loss_{}'.format(int(args.threshold))])
    for z in range(SPLIT_Z+1,START_Z+1):
        bmz=BIOMASS(loss,hansen_lossyear,whrc_carbon,z)
        if (z==(SPLIT_Z+1)) and (SPLIT_Z>END_Z):
            if (args.split_asset is True) or (args.split_asset.lower()=='true'):
                export_split_asset(bmz.split_data())
        export_tiles(bmz.image(),z,z)


def _split_asset(args):
    bm=BIOMASS(int(args.threshold))
    export_split_asset(bm.image())


def main():
    global threshold, geom_name, geom, name_prefix
    parser=argparse.ArgumentParser(description='HANSEN COMPOSITE')
    parser.add_argument(
        '-p','--name_prefix',
        default='',
        help='prefix for asset name and tiles path')
    parser.add_argument(
        '-g','--geom_name',
        default=DEFAULT_GEOM_NAME,
        help='geometry name (https://fusiontables.google.com/DataSource?docid=13BvM9v1Rzr90Ykf1bzPgbYvbb8kGSvwyqyDwO8NI)')
    parser.add_argument('threshold',help='treecover 2000:\none of {}'.format(THRESHOLDS))
    subparsers=parser.add_subparsers()
    parser_outside=subparsers.add_parser('outside', help='export the zoomed out z-levels')
    parser_outside.set_defaults(func=_outside)
    parser_inside=subparsers.add_parser('inside', help='export the zoomed in z-levels')
    parser_inside.add_argument('-a','--split_asset',default=True,help='export spit asset')
    parser_inside.set_defaults(func=_inside)
    parser_split_asset=subparsers.add_parser('split_asset', help='export z-level split asset')
    parser_split_asset.set_defaults(func=_split_asset)
    args=parser.parse_args()
    if int(args.threshold) in THRESHOLDS: 
        name_prefix=args.name_prefix
        threshold=args.threshold
        geom_name=args.geom_name
        geom=get_geom(geom_name)
        if not geom:
            print 'ERROR: {} is not a valid geometry'.format(geom_name)
        else:
            print "THRESHOLD: {}".format(threshold)
            print "GEOMETRY: {}".format(geom_name)
            args.func(args)
    else: 
        print 'INVALID THRESHOLD {}: choose from {}'.format(args.threshold,THRESHOLDS)


if __name__ == "__main__":
    main()



