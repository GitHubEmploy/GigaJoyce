from typing import Any, List, Tuple, Union, Dict

# Type alias for recursive mappings
RecursiveMap = Dict[str, Union[Any, "RecursiveMap"]]


def parse_to_database(map_obj: RecursiveMap) -> List[Tuple[str, Any]]:
    """
    Convert a nested dictionary (RecursiveMap) to a list of key-value pairs suitable for database storage.

    Args:
        map_obj (RecursiveMap): The nested dictionary to convert.

    Returns:
        List[Tuple[str, Any]]: A list of key-value pairs.
    """
    built = []
    for key, value in map_obj.items():
        if isinstance(value, dict):
            built.append((key, parse_to_database(value)))
        else:
            built.append((key, value))
    return built


def parse_from_database(array: List[Tuple[str, Any]]) -> RecursiveMap:
    """
    Convert a list of key-value pairs from a database back to a nested dictionary (RecursiveMap).

    Args:
        array (List[Tuple[str, Any]]): The list of key-value pairs.

    Returns:
        RecursiveMap: A nested dictionary.
    """
    built = {}
    for key, value in array:
        if isinstance(value, list):
            built[key] = parse_from_database(value)
        else:
            built[key] = value
    return built
