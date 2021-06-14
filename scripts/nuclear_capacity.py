import pandas as pd
import shapely.geometry
import geopandas as gpd


def regionalise_nuclear_capacity(
    path_to_power_plant_database, path_to_nuclear_capacity,
    path_to_shapes, nuclear_capacity_year, path_to_result
):
    power_plants = pd.read_csv(path_to_power_plant_database)
    units = gpd.read_file(path_to_shapes)

    capacity_current = power_plants[power_plants.type_g == 'Nuclear']
    capacity_current_points = [
        shapely.geometry.Point(xy)
        for xy in zip(capacity_current.lon, capacity_current.lat)
    ]
    capacity_current_gdf = gpd.GeoDataFrame(
        capacity_current, geometry=capacity_current_points, crs='epsg:4326'
    )
    capacity_current_per_region = (
        gpd.overlay(capacity_current_gdf, units)
        .groupby(['id', 'country_code']).sum()
        .capacity_g
    )
    if nuclear_capacity_year == "current":
        capacity_per_region = pd.concat(
            [capacity_current_per_region, capacity_current_per_region],
            keys=['installed_capacity_nuclear_min_MW', 'installed_capacity_nuclear_max_MW'],
            axis=1
        )

    elif nuclear_capacity_year == "2050":
        capacity_2050 = pd.read_csv(path_to_nuclear_capacity, index_col=0)
        nuclear_proportion = capacity_current_per_region.div(
            capacity_current_per_region.sum(level='country_code')
        )

        capacity_per_region = (
            capacity_2050[['installed_capacity_nuclear_min_MW', 'installed_capacity_nuclear_max_MW']]
            .mul(nuclear_proportion, level='country_code', axis=0)
        )
    capacity_per_region.dropna().droplevel("country_code").to_csv(path_to_result)


if __name__ == "__main__":
    regionalise_nuclear_capacity(
        path_to_power_plant_database=snakemake.input.power_plant_database,
        path_to_nuclear_capacity=snakemake.input.nuclear_capacity,
        path_to_shapes=snakemake.input.shapes,
        nuclear_capacity_year=snakemake.params.nuclear_capacity_year,
        path_to_result=snakemake.output[0]
    )
