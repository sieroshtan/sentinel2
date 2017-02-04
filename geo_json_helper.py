from osgeo import ogr


def createGeoJson(bin, tilepath):
    """
    Create geojson file with a farm polygon
    :param bin:
    :param tilepath:
    :return:
    """
    poly = ogr.CreateGeometryFromWkb(bytes(bin))

    # Create the output Driver
    outDriver = ogr.GetDriverByName('GeoJSON')

    # Create the output GeoJSON
    outDataSource = outDriver.CreateDataSource(tilepath)
    outLayer = outDataSource.CreateLayer(tilepath, geom_type=ogr.wkbPolygon)

    # Get the output Layer's Feature Definition
    featureDefn = outLayer.GetLayerDefn()

    # create a new feature
    outFeature = ogr.Feature(featureDefn)

    # Set new geometry
    outFeature.SetGeometry(poly)

    # Add new feature to output Layer
    outLayer.CreateFeature(outFeature)

    # destroy the feature
    outFeature.Destroy()

    # Close DataSources
    outDataSource.Destroy()
