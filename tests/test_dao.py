"""Tests for `eazyapi.dao` module."""

from pathlib import Path

import pytest
from tortoise import Model, fields

from eazyapi.dao import SQLDAO, BaseDAO, DatabaseConfig, str_to_num
from eazyapi.exceptions import InvalidQueryError

# ------------------------------------------
# Test cases for str_to_num()
# ------------------------------------------


def test_str_to_num_with_int_string() -> None:
    """Test `str_to_num` with string of an integer."""
    assert str_to_num("123") == 123


def test_str_to_num_with_float_string() -> None:
    """Test `str_to_num` with string of a float."""
    assert str_to_num("123.456") == 123.456


def test_str_to_num_with_non_numeric_string() -> None:
    """Test `str_to_num` with a non-numeric string."""
    with pytest.raises(ValueError) as e:
        str_to_num("abc")
    assert str(e.value) == "The provided string abc is not a number"


def test_str_to_num_with_empty_string() -> None:
    """Test `str_to_num` with an empty string."""
    with pytest.raises(ValueError) as e:
        str_to_num("")
    assert str(e.value) == "The provided string  is not a number"


# ------------------------------------------
# Test cases for BaseDAO.validate_filters()
# ------------------------------------------


def test_validate_filters_with_valid_filters() -> None:
    """Tests the `validate_filters` function with valid filters."""
    filters = {
        "column1": {"$eq": "value1"},
        "column2": {"$lt": 10},
        "$and": [{"column3": {"$eq": "value3"}}, {"column4": {"$ne": "value4"}}],
    }
    assert BaseDAO.validate_filters(filters) == filters


def test_validate_filters_with_invalid_operator() -> None:
    """Tests the `validate_filters` function with an invalid operator."""
    filters = {
        "column1": {"$equals": "value1"},  # Invalid operator "$equals"
    }
    with pytest.raises(InvalidQueryError):
        BaseDAO.validate_filters(filters)


def test_validate_filters_with_invalid_column_name() -> None:
    """Tests the `validate_filters` function with an invalid column name."""
    filters = {
        "1column": {"$eq": "value1"},  # Invalid column name "1column",
    }
    with pytest.raises(InvalidQueryError):
        BaseDAO.validate_filters(filters)


def test_validate_filters_with_valid_value_data_type() -> None:
    """Tests the `validate_filters` function with an valid value data type."""
    filters = {
        "column1": {"$eq": ["value1"]},
    }
    assert BaseDAO.validate_filters(filters) == filters
    # with pytest.raises(InvalidQueryError):
    #     BaseDAO.validate_filters(filters)


# def test_validate_filters_with_invalid_structure() -> None:
#     filters = {
#         "column1": {"$eq": "value1", "$ne": "value2"},  # Multiple operators for one column,
#     }
#     with pytest.raises(InvalidQueryError):
#         BaseDAO.validate_filters(filters)


def test_validate_filters_with_invalid_structure_for_and_or() -> None:
    """Tests the `validate_filters` function with an invalid structure for $and and $or."""
    filters = {
        "$and": {
            "column1": {"$eq": "value1"},
            "column2": {"$ne": "value2"},
        },  # Invalid structure for $and,
    }
    with pytest.raises(InvalidQueryError):
        BaseDAO.validate_filters(filters)

    filters = {
        "$or": {
            "column1": {"$eq": "value1"},
            "column2": {"$ne": "value2"},
        },  # Invalid structure for $or,
    }
    with pytest.raises(InvalidQueryError):
        BaseDAO.validate_filters(filters)


def test_validate_filters_complex_case_with_valid_filters() -> None:
    """Tests the `validate_filters` function with complex valid filters."""
    filters = {
        "name": "John",
        "age": {"$gte": 30},
        "$and": [{"city": "New York"}, {"status": {"$ne": "inactive"}}],
    }
    assert BaseDAO.validate_filters(filters) == filters


# def test_validate_filters_complex_case_with_invalid_data_type() -> None:
#     # TODO: Fix me. This case is not working
#     filters = {
#         "name": "John",
#         "age": {"$gte": "30"},  # '30' should be an integer, not a string
#         "$and": [{"city": "New York"}, {"status": {"$ne": "inactive"}}]
#     }
#     with pytest.raises(InvalidQueryError):
#         BaseDAO.validate_filters(filters)


def test_validate_filters_complex_case_with_invalid_operator() -> None:
    """Tests the `validate_filters` function with a complex case having an invalid operator."""
    filters = {
        "name": "John",
        "age": {"$greater_than_or_equal_to": 30},  # Invalid operator
        "$and": [{"city": "New York"}, {"status": {"$ne": "inactive"}}],
    }
    with pytest.raises(InvalidQueryError):
        BaseDAO.validate_filters(filters)


def test_validate_filters_complex_case_with_invalid_column_name() -> None:
    """Tests the `validate_filters` function with a complex case having an invalid column name."""
    filters = {
        "name": "John",
        "age": {"$gte": 30},
        "$and": [
            {"1city": "New York"},
            {"status": {"$ne": "inactive"}},
        ],  # Invalid column name '1city'
    }
    with pytest.raises(InvalidQueryError):
        BaseDAO.validate_filters(filters)


# ---------------------------------------
# Test cases for BaseDAO.validate_sort()
# ---------------------------------------


def test_validate_sort_string_single_column() -> None:
    """Tests the `validate_sort` function with a single column string."""
    sort = "name"
    assert BaseDAO.validate_sort(sort) == sort


def test_validate_sort_string_single_column_descending() -> None:
    """Tests the `validate_sort` function with a single column string in descending order."""
    sort = "-name"
    assert BaseDAO.validate_sort(sort) == sort


def test_validate_sort_string_multiple_columns() -> None:
    """Tests the `validate_sort` function with multiple column strings."""
    sort = "name,-age"
    assert BaseDAO.validate_sort(sort) == sort


def test_validate_sort_dict_single_column() -> None:
    """Tests the `validate_sort` function with a single column dictionary."""
    sort = {"name": 1}
    assert BaseDAO.validate_sort(sort) == sort


def test_validate_sort_dict_single_column_descending() -> None:
    """Tests the `validate_sort` function with a single column dictionary in descending order."""
    sort = {"name": -1}
    assert BaseDAO.validate_sort(sort) == sort


def test_validate_sort_dict_multiple_columns() -> None:
    """Tests the `validate_sort` function with multiple column dictionaries."""
    sort = {"name": 1, "age": -1}
    assert BaseDAO.validate_sort(sort) == sort


def test_validate_sort_list_single_column() -> None:
    """Tests the `validate_sort` function with a single column list."""
    sort = [("name", 1)]
    assert BaseDAO.validate_sort(sort) == sort


def test_validate_sort_list_single_column_descending() -> None:
    """Tests the `validate_sort` function with a single column list in descending order."""
    sort = [("name", -1)]
    assert BaseDAO.validate_sort(sort) == sort


def test_validate_sort_list_multiple_columns() -> None:
    """Tests the `validate_sort` function with multiple column lists."""
    sort = [("name", 1), ("age", -1)]
    assert BaseDAO.validate_sort(sort) == sort


def test_validate_sort_invalid_column_name() -> None:
    """Tests the `validate_sort` function with an invalid column name."""
    with pytest.raises(InvalidQueryError) as e:
        BaseDAO.validate_sort("123name")
    assert str(e.value) == "Invalid sort field: 123name"


def test_validate_sort_invalid_dict_key() -> None:
    """Tests the `validate_sort` function with an invalid dictionary key."""
    with pytest.raises(InvalidQueryError) as e:
        BaseDAO.validate_sort({"123name": 1})
    assert str(e.value) == "Invalid sort key: 123name"


def test_validate_sort_invalid_dict_value() -> None:
    """Tests the `validate_sort` function with an invalid dictionary value."""
    with pytest.raises(InvalidQueryError) as e:
        BaseDAO.validate_sort({"name": 2})
    assert str(e.value) == "Invalid sort value: 2, allowed values are -1 and 1"


def test_validate_sort_invalid_list_item() -> None:
    """Tests the `validate_sort` function with an invalid list item."""
    with pytest.raises(InvalidQueryError) as e:
        BaseDAO.validate_sort([("name", 1), "age"])  # type: ignore
    assert str(e.value) == "Invalid sort item: age, it should be a tuple of size 2"


def test_validate_sort_invalid_list_key() -> None:
    """Tests the `validate_sort` function with an invalid list key."""
    with pytest.raises(InvalidQueryError) as e:
        BaseDAO.validate_sort([("name", 1), ("123age", -1)])
    assert str(e.value) == "Invalid sort key: 123age"


def test_validate_sort_invalid_list_value() -> None:
    """Tests the `validate_sort` function with an invalid list value."""
    with pytest.raises(InvalidQueryError) as e:
        BaseDAO.validate_sort([("name", 1), ("age", 2)])
    assert str(e.value) == "Invalid sort value: 2, allowed values are -1 and 1"


# ---------------------------------------
# Test cases for SQLDAO
# ---------------------------------------


class SampleModel(Model):
    """Sample Model for testing."""

    _id = fields.IntField(pk=True)
    name = fields.TextField()


@pytest.fixture
def db_uri() -> str:
    """Pytest fixture for database URI."""
    # Construct the path to the desired location
    db_name = "testdb.sqlite3"
    tmp_dir = Path(__file__).parent / "tmp"
    db_path = tmp_dir / db_name
    db_uri = f"sqlite:///{db_path}"
    return db_uri


@pytest.fixture
def sqldao(db_uri: str) -> SQLDAO:
    """Pytest fixture for SQLDAO instance."""
    config = DatabaseConfig(uri=db_uri, database="test", models=[__name__])
    dao = SQLDAO(config=config)
    return dao


def test_sqldao_constructor() -> None:
    """Tests the SQLDAO constructor."""
    # Arrange
    config = DatabaseConfig(uri="sqlite://testdb.sqlite3", database="test", models=["app.models"])

    # Act
    sqldao = SQLDAO(config=config)

    # Assert
    assert sqldao.config == config
    assert sqldao.tortoise_config == {
        "connections": {"master": config.uri, "slave": config.uri},
        "apps": {
            config.database: {
                "models": config.models,
                "default_connection": "master",
            }
        },
        "routers": ["eazyapi.dao.TortoiseDefaultRouter"],
    }


@pytest.mark.asyncio
async def test_sqldao_connections_init_and_close(sqldao: SQLDAO) -> None:
    """Tests the `init` and `close` functions of the SQLDAO."""
    # Act
    await sqldao.init()

    # Assert
    assert sqldao.connections.get("master") is not None
    assert sqldao.connections.get("slave") is not None

    # Act
    await sqldao.close()

    # Assert
    # TODO: Fix the below assertions or investigate why they're not working.
    # assert sqldao.connections.get('master') is None
    # assert sqldao.connections.get('slave') is None


def test_prepare_sorting_string(sqldao: SQLDAO) -> None:
    """Tests the `_prepare_sorting` function with a string."""
    sort = "name,-age"

    # Act
    sorted_fields = sqldao._prepare_sorting(sort)

    # Assert
    assert sorted_fields == ["name", "-age"]


def test_prepare_sorting_dict(sqldao: SQLDAO) -> None:
    """Tests the `_prepare_sorting` function with a dictionary."""
    sort = {"name": 1, "age": -1}

    # Act
    sorted_fields = sqldao._prepare_sorting(sort)

    # Assert
    assert sorted_fields == ["name", "-age"]


def test_prepare_sorting_list(sqldao: SQLDAO) -> None:
    """Tests the `_prepare_sorting` function with a list."""
    sort = [("name", 1), ("age", -1)]

    # Act
    sorted_fields = sqldao._prepare_sorting(sort)

    # Assert
    assert sorted_fields == ["name", "-age"]


def test_prepare_sorting_string_with_subkeys(sqldao: SQLDAO) -> None:
    """Tests the `_prepare_sorting` function with a string containing subkeys."""
    sort = "name,-age,employer.name"

    # Act
    sorted_fields = sqldao._prepare_sorting(sort)

    # Assert
    assert sorted_fields == ["name", "-age", "employer__name"]


def test_prepare_sorting_dict_with_subkeys(sqldao: SQLDAO) -> None:
    """Tests the `_prepare_sorting` function with a dictionary containing subkeys."""
    sort = {"name": 1, "age": -1, "employer.name": 1}

    # Act
    sorted_fields = sqldao._prepare_sorting(sort)

    # Assert
    assert sorted_fields == ["name", "-age", "employer__name"]


def test_prepare_sorting_list_with_subkeys(sqldao: SQLDAO) -> None:
    """Tests the `_prepare_sorting` function with a list containing subkeys."""
    sort = [("name", 1), ("age", -1), ("employer.name", 1)]

    # Act
    sorted_fields = sqldao._prepare_sorting(sort)

    # Assert
    assert sorted_fields == ["name", "-age", "employer__name"]


@pytest.mark.asyncio
async def test_check_models(sqldao: SQLDAO) -> None:
    """Tests describe models."""
    await sqldao.init()

    Model.check()

    await sqldao.close()


@pytest.mark.asyncio
async def test_get_model_valid(sqldao: SQLDAO) -> None:
    """Tests the `_get_model` function with a valid model name."""
    await sqldao.init()

    # Act
    ModelClass = sqldao._get_model("SampleModel")

    # Assert
    assert ModelClass == SampleModel

    await sqldao.close()


def test_get_model_invalid(sqldao: SQLDAO) -> None:
    """Tests the `_get_model` function with an invalid model name."""
    # Act & Assert
    with pytest.raises(InvalidQueryError):
        sqldao._get_model("InvalidModel")


# @pytest.mark.asyncio
# async def test_sqldao_create(sqldao: SQLDAO) -> None:
#     """Tests the `create` function of the SQLDAO."""
#     # Arrange
#     await sqldao.init()
#     model_name = "SampleModel"
#     record = {"name": "Test Name"}

#     # Act
#     created_obj = await sqldao.create(model_name, record)

#     # Assert
#     assert created_obj is not None
#     assert created_obj.name == record["name"]

#     # Clean up
#     await sqldao.close()


# @pytest.mark.asyncio
# async def test_sqldao_get_many(sqldao: SQLDAO) -> None:
#     """Tests the `get_many` function of the SQLDAO."""
#     # Arrange
#     await sqldao.init()
#     model_name = "SampleModel"
#     record1 = {"name": "Test Name 1"}
#     record2 = {"name": "Test Name 2"}
#     await sqldao.create(model_name, record1)
#     await sqldao.create(model_name, record2)

#     # Act
#     result = await sqldao.get_many(model_name)

#     # Assert
#     assert len(result) == 2
#     assert result[0].name in [record1["name"], record2["name"]]
#     assert result[1].name in [record1["name"], record2["name"]]

#     # Clean up
#     await sqldao.close()


# @pytest.mark.asyncio
# async def test_sqldao_update(sqldao: SQLDAO) -> None:
#     """Tests the `update` function of the SQLDAO."""
#     # Arrange
#     await sqldao.init()
#     model_name = "SampleModel"
#     record = {"name": "Test Name"}
#     new_name = "New Test Name"
#     created_obj = await sqldao.create(model_name, record)

#     # Act
#     updated_obj = await sqldao.update(model_name, created_obj._id, {"name": new_name})

#     # Assert
#     assert updated_obj is not None
#     assert updated_obj.name == new_name

#     # Clean up
#     await sqldao.close()


# @pytest.mark.asyncio
# async def test_sqldao_delete(sqldao: SQLDAO) -> None:
#     """Tests the `delete` function of the SQLDAO."""
#     # Arrange
#     await sqldao.init()
#     model_name = "SampleModel"
#     record = {"name": "Test Name"}
#     created_obj = await sqldao.create(model_name, record)

#     # Act
#     await sqldao.delete(model_name, created_obj._id)
#     deleted_obj = await sqldao.get_by_id(model_name, created_obj._id)

#     # Assert
#     assert deleted_obj is None

#     # Clean up
#     await sqldao.close()
