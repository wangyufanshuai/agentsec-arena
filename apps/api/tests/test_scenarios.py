from agentsec_arena.scenarios import ScenarioCatalog


def test_catalog_loads_required_scenarios():
    catalog = ScenarioCatalog()
    scenario_ids = {scenario.id for scenario in catalog.list()}
    assert "dvwa" in scenario_ids
    assert "juice-shop" in scenario_ids
    assert "vulhub-cve-2021-41773-apache" in scenario_ids

