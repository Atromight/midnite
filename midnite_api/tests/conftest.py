from typing import Any


def pytest_generate_tests(metafunc: Any) -> None:
    """Custom parametrization scheme"""
    function_name = metafunc.function.__name__
    function_scenarios = getattr(metafunc.cls, f"{function_name}_scenarios")
    function_params = [key for key in function_scenarios[0] if key != "description"]
    function_values = [
        [scenario[param] for param in function_params]
        for scenario in function_scenarios
    ]
    ids_list = [
        scenario.get("description", f"scenario_{i}")
        for i, scenario in enumerate(function_scenarios)
    ]
    metafunc.parametrize(function_params, function_values, ids=ids_list, scope="class")
