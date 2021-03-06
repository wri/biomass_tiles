from __future__ import print_function
import ee, gee
import argparse
gee.init()




""" CONFIG
"""
VERSION='v4_1_7'
END_YY=19
BINARY_LOSS_ASSET_ID='projects/wri-datalab/umd/HANSEN_BINARY_LOSS_19'
HANSEN_ASSET_ID='UMD/hansen/global_forest_change_2019_v1_7'
#CARBON_ASSET_IC_ID='projects/wri-datalab/WHRC_CARBON'
CARBON_ASSET_IC_ID='projects/wri-datalab/WHRC/global/carbon'


MAX_PIXS=65500
CRS="EPSG:4326"
SCALE=27.829872698318393
START_Z=12
SPLIT_Z=6
END_Z=2
YEARS=ee.List.sequence(1,END_YY)
Z_LEVELS=[156000,78000,39000,20000,10000,4900,2400,1200,611,305,152,76,38]
THRESHOLDS=[10,15,20,25,30,50,75]
# DEFAULT_GEOM_NAME='tropics'
DEFAULT_GEOM_NAME='hansen_world'
GEE_ROOT='projects/wri-datalab'
GEE_SPLIT_FOLDER=f'biomass_loss_2019-global_zsplit-{VERSION}'
GCS_TILES_ROOT="v4.1.7"
GCS_BUCKET='whrc_aboveground_biomass_loss__mg_per_ha'
BANDS=['year', 'total_biomass_loss', 'density']



"""PARAMS
"""
threshold=None
name_prefix=None
geom=None
geom_name=None



""""ASSETS
"""
hansen_binary_loss=ee.Image(BINARY_LOSS_ASSET_ID)
hansen=ee.Image(HANSEN_ASSET_ID)
whrc_carbon=ee.ImageCollection(CARBON_ASSET_IC_ID).max().rename(['carbon'])
hansen_lossyear=hansen.select(['lossyear'])
treecover=hansen.select(['treecover2000'])



"""GEOMETRY
"""
geoms_ft=ee.FeatureCollection('ft:13BvM9v1Rzr90Ykf1bzPgbYvbb8kGSvwyqyDwO8NI')
def get_geom():
    return ee.Geometry.MultiPolygon([[[[180.0, -50.0], [180.0, -60.0], [170.0, -60.0], [160.0, -60.0], [150.0, -60.0],
                                       [150.0, -50.0], [140.0, -50.0], [140.0, -40.0], [130.0, -40.0], [120.0, -40.0],
                                       [110.0, -40.0], [110.0, -30.0], [110.0, -20.0], [100.0, -20.0], [90.0, -20.0],
                                       [90.0, -10.0], [90.0, 0.0], [80.0, 0.0], [80.0, -10.0], [70.0, -10.0],
                                       [70.0, -20.0], [60.0, -20.0], [60.0, -30.0], [50.0, -30.0], [40.0, -30.0],
                                       [40.0, -40.0], [30.0, -40.0], [20.0, -40.0], [10.0, -40.0], [10.0, -30.0],
                                       [10.0, -20.0], [10.0, -10.0], [0.0, -10.0], [0.0, 0.0], [-10.0, 0.0],
                                       [-10.0, -10.0], [-20.0, -10.0], [-20.0, 0.0], [-20.0, 10.0], [-30.0, 10.0],
                                       [-30.0, 20.0], [-20.0, 20.0], [-20.0, 30.0], [-30.0, 30.0], [-40.0, 30.0],
                                       [-40.0, 40.0], [-30.0, 40.0], [-20.0, 40.0], [-10.0, 40.0], [-10.0, 50.0],
                                       [-20.0, 50.0], [-20.0, 60.0], [-30.0, 60.0], [-40.0, 60.0], [-40.0, 50.0],
                                       [-50.0, 50.0], [-50.0, 40.0], [-60.0, 40.0], [-60.0, 30.0], [-70.0, 30.0],
                                       [-70.0, 20.0], [-60.0, 20.0], [-50.0, 20.0], [-50.0, 10.0], [-40.0, 10.0],
                                       [-40.0, 0.0], [-30.0, 0.0], [-30.0, -10.0], [-30.0, -20.0], [-40.0, -20.0],
                                       [-40.0, -30.0], [-50.0, -30.0], [-50.0, -40.0], [-60.0, -40.0], [-60.0, -50.0],
                                       [-50.0, -50.0], [-40.0, -50.0], [-30.0, -50.0], [-20.0, -50.0], [-20.0, -60.0],
                                       [-30.0, -60.0], [-40.0, -60.0], [-50.0, -60.0], [-60.0, -60.0], [-70.0, -60.0],
                                       [-80.0, -60.0], [-80.0, -50.0], [-80.0, -40.0], [-90.0, -40.0], [-90.0, -30.0],
                                       [-90.0, -20.0], [-80.0, -20.0], [-80.0, -10.0], [-90.0, -10.0], [-100.0, -10.0],
                                       [-100.0, 0.0], [-100.0, 10.0], [-110.0, 10.0], [-120.0, 10.0], [-120.0, 20.0],
                                       [-120.0, 30.0], [-130.0, 30.0], [-130.0, 40.0], [-130.0, 50.0], [-140.0, 50.0],
                                       [-150.0, 50.0], [-160.0, 50.0], [-170.0, 50.0], [-180.0, 50.0], [-180.0, 60.0],
                                       [-180.0, 70.0], [-180.0, 80.0], [-170.0, 80.0], [-160.0, 80.0], [-150.0, 80.0],
                                       [-140.0, 80.0], [-130.0, 80.0], [-120.0, 80.0], [-110.0, 80.0], [-100.0, 80.0],
                                       [-90.0, 80.0], [-80.0, 80.0], [-70.0, 80.0], [-60.0, 80.0], [-50.0, 80.0],
                                       [-40.0, 80.0], [-30.0, 80.0], [-20.0, 80.0], [-10.0, 80.0], [0.0, 80.0],
                                       [0.0, 70.0], [10.0, 70.0], [10.0, 80.0], [20.0, 80.0], [30.0, 80.0],
                                       [40.0, 80.0], [50.0, 80.0], [60.0, 80.0], [70.0, 80.0], [80.0, 80.0],
                                       [90.0, 80.0], [100.0, 80.0], [110.0, 80.0], [120.0, 80.0], [130.0, 80.0],
                                       [140.0, 80.0], [150.0, 80.0], [160.0, 80.0], [170.0, 80.0], [180.0, 80.0],
                                       [180.0, 70.0], [180.0, 60.0], [180.0, 50.0], [170.0, 50.0], [160.0, 50.0],
                                       [160.0, 40.0], [150.0, 40.0], [150.0, 30.0], [160.0, 30.0], [160.0, 20.0],
                                       [170.0, 20.0], [180.0, 20.0], [180.0, 10.0], [180.0, 0.0], [180.0, -10.0],
                                       [180.0, -20.0], [180.0, -30.0], [180.0, -40.0], [180.0, -50.0]],
                                      [[150.0, -50.0], [160.0, -50.0], [160.0, -40.0], [150.0, -40.0], [150.0, -50.0]],
                                      [[160.0, -40.0], [170.0, -40.0], [170.0, -30.0], [160.0, -30.0], [160.0, -40.0]],
                                      [[70.0, -10.0], [70.0, 0.0], [70.0, 10.0], [70.0, 20.0], [60.0, 20.0],
                                       [60.0, 10.0], [60.0, 0.0], [60.0, -10.0], [70.0, -10.0]],
                                      [[160.0, 20.0], [150.0, 20.0], [150.0, 10.0], [160.0, 10.0], [160.0, 20.0]]],
                                     [[[0.0, -50.0], [10.0, -50.0], [10.0, -60.0], [0.0, -60.0], [0.0, -50.0]]], [
                                         [[80.0, -40.0], [80.0, -50.0], [80.0, -60.0], [70.0, -60.0], [60.0, -60.0],
                                          [60.0, -50.0], [50.0, -50.0], [50.0, -40.0], [60.0, -40.0], [70.0, -40.0],
                                          [70.0, -30.0], [80.0, -30.0], [80.0, -40.0]]], [
                                         [[-10.0, -40.0], [0.0, -40.0], [0.0, -50.0], [-10.0, -50.0], [-20.0, -50.0],
                                          [-20.0, -40.0], [-20.0, -30.0], [-10.0, -30.0], [-10.0, -40.0]]], [
                                         [[-110.0, -20.0], [-100.0, -20.0], [-100.0, -30.0], [-110.0, -30.0],
                                          [-110.0, -20.0]]],
                                     [[[-30.0, -20.0], [-20.0, -20.0], [-20.0, -30.0], [-30.0, -30.0], [-30.0, -20.0]]],
                                     [[[-10.0, -10.0], [0.0, -10.0], [0.0, -20.0], [-10.0, -20.0], [-10.0, -10.0]]], [
                                         [[-170.0, -40.0], [-170.0, -50.0], [-180.0, -50.0], [-180.0, -40.0],
                                          [-180.0, -30.0], [-180.0, -20.0], [-180.0, -10.0], [-180.0, 0.0],
                                          [-180.0, 10.0], [-170.0, 10.0], [-170.0, 20.0], [-180.0, 20.0],
                                          [-180.0, 30.0], [-170.0, 30.0], [-160.0, 30.0], [-150.0, 30.0],
                                          [-150.0, 20.0], [-150.0, 10.0], [-150.0, 0.0], [-140.0, 0.0], [-130.0, 0.0],
                                          [-130.0, -10.0], [-130.0, -20.0], [-120.0, -20.0], [-120.0, -30.0],
                                          [-130.0, -30.0], [-140.0, -30.0], [-150.0, -30.0], [-160.0, -30.0],
                                          [-160.0, -20.0], [-170.0, -20.0], [-170.0, -30.0], [-170.0, -40.0]]]], None,
                                    False)






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
        region=geom.bounds(),
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
        region=geom.bounds(),
        maxPixels=1e13)
    run_task(task)


def run_task(task):
    task.start()
    print(task.status())






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
    threshold=int(args.threshold)
    loss=hansen_binary_loss.select(['loss_{}'.format(threshold)])
    carbon=whrc_carbon.updateMask(treecover.gte(threshold)).unmask(0)
    for z in range(SPLIT_Z+1,START_Z+1):
        bmz=BIOMASS(loss,hansen_lossyear,carbon,z)
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
    parser_split_asset=subparsers.add_parser('split_asset', help='true/false - export z-level split asset. defaults to true.')
    parser_split_asset.set_defaults(func=_split_asset)
    args=parser.parse_args()
    if int(args.threshold) in THRESHOLDS: 
        name_prefix=args.name_prefix
        threshold=args.threshold
        geom_name=args.geom_name
        geom=get_geom()
        if not geom:
            print('ERROR: {} is not a valid geometry'.format(geom_name))
        else:
            print("THRESHOLD: {}".format(threshold))
            print("GEOMETRY: {}".format(geom_name))
            args.func(args)
    else: 
        print('INVALID THRESHOLD {}: choose from {}'.format(args.threshold,THRESHOLDS))


if __name__ == "__main__":
    main()



