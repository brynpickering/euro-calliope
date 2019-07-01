from pathlib import Path

import pytest
import calliope

MONETARY_SCALING_FACTOR = 30
POWER_SCALING_FACTOR = 2
AREA_SCALING_FACTOR = 0.1
PATH_TO_SIMPLE_CONTINENTAL_MODEL = Path(__file__).parent / ".." / "build" / "output" / "continental-model.nc"
PATH_TO_SIMPLE_CONTINENTAL_MODEL_SCALED = Path(__file__).parent / ".." / "build" / "output" / "continental-model-scaled.nc"


@pytest.fixture(scope="module")
def scaled_results():
    return calliope.read_netcdf(PATH_TO_SIMPLE_CONTINENTAL_MODEL_SCALED.as_posix())


@pytest.fixture(scope="module")
def unscaled_results():
    return calliope.read_netcdf(PATH_TO_SIMPLE_CONTINENTAL_MODEL.as_posix())


@pytest.fixture(
    params=[
        "battery",
        "hydrogen",
        ["open_field_pv", "roof_mounted_pv"],
        "biofuel",
        ["wind_onshore_competing", "wind_onshore_monopoly"],
        "hydro_run_of_river",
        "hydro_reservoir",
        "pumped_hydro"
    ])
def tech(request):
    return request.param


@pytest.fixture(
    params=[
        "battery",
        "hydrogen",
        ["open_field_pv", "roof_mounted_pv"],
        "biofuel",
        ["wind_onshore_competing", "wind_onshore_monopoly"],
        "pumped_hydro"
    ])
def tech_with_cost(request):
    return request.param


@pytest.fixture(
    params=[
        "open_field_pv",
        "wind_onshore_competing",
    ])
def tech_with_area(request):
    return request.param


@pytest.mark.scaling
def test_same_total_costs(unscaled_results, scaled_results):
    scaled = scaled_results.get_formatted_array("cost").squeeze(["costs", "locs"]).sum().item()
    unscaled = unscaled_results.get_formatted_array("cost").squeeze(["costs", "locs"]).sum().item()
    assert scaled / MONETARY_SCALING_FACTOR == pytest.approx(unscaled)


@pytest.mark.scaling
def test_same_costs(unscaled_results, scaled_results, tech_with_cost):
    scaled = scaled_results.get_formatted_array("cost").squeeze(["costs", "locs"]).sel(techs=tech_with_cost).sum().item()
    unscaled = unscaled_results.get_formatted_array("cost").squeeze(["costs", "locs"]).sel(techs=tech_with_cost).sum().item()
    assert scaled / MONETARY_SCALING_FACTOR == pytest.approx(unscaled)


@pytest.mark.scaling
def test_same_energy_cap(unscaled_results, scaled_results, tech):
    scaled = scaled_results.get_formatted_array("energy_cap").squeeze(["locs"]).sel(techs=tech).sum().item()
    unscaled = unscaled_results.get_formatted_array("energy_cap").squeeze(["locs"]).sel(techs=tech).sum().item()
    assert scaled / POWER_SCALING_FACTOR == pytest.approx(unscaled)


@pytest.mark.scaling
def test_same_total_generation(unscaled_results, scaled_results, tech):
    scaled = scaled_results.get_formatted_array("carrier_prod").squeeze(["locs", "carriers"]).sel(techs=tech).sum().item()
    unscaled = unscaled_results.get_formatted_array("carrier_prod").squeeze(["locs", "carriers"]).sel(techs=tech).sum().item()
    assert scaled / POWER_SCALING_FACTOR == pytest.approx(unscaled)


@pytest.mark.xfail(reason="Optimiser can always choose PV/wind without footprint. It's a valid choice.")
@pytest.mark.scaling
def test_same_area(unscaled_results, scaled_results, tech_with_area):
    scaled = scaled_results.get_formatted_array("resource_area").squeeze(["locs"]).sel(techs=tech_with_area).sum().item()
    unscaled = unscaled_results.get_formatted_array("resource_area").squeeze(["locs"]).sel(techs=tech_with_area).sum().item()
    assert scaled / AREA_SCALING_FACTOR == pytest.approx(unscaled)
