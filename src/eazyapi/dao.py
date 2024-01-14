"""Generic DAO classes for CRUD operations."""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator
from tortoise import Model, Tortoise, connections
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.expressions import Q

from eazyapi.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    InvalidQueryError,
    RecordNotFoundError,
)


class DatabaseConfig(BaseModel):
    """
    Pydantic model for the database configuration.

    Args:
        uri (str): A string indicating the database URI.
        database (str): A string indicating the database name.
        models (List[str]): List of modules containing models.
    """

    uri: str = Field(..., description="A string indicating the database URI.")
    database: str = Field(..., description="A string indicating the database name.")
    models: List[str] = Field(..., description="List of modules containing models.")


class BaseDAO(BaseModel, ABC):
    """
    Abstract base class for CRUD operations in an asynchronous environment.

    Defines the expected methods for Create, Read, Update, and Delete operations.
    These methods are all asynchronous and therefore should be used in an
    asynchronous context. Specific implementations are expected to subclass this
    and provide concrete implementations for all methods.

    Attributes:
        config: Database configuration.
    """

    model_config = ConfigDict(extra="ignore")

    config: DatabaseConfig

    @abstractmethod
    async def init(self) -> None:
        """
        Initialize the connection with the database.

        Raises:
            DatabaseConnectionError: If there are issues connecting to the database.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Closes the connections to the database.

        Raises:
            DatabaseConnectionError: If there are issues closing the connection to the database.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, model_name: str, _id: int) -> Any:
        """
        Fetches a record by its ID from a model.

        Args:
            model_name: Name of the model.
            _id: ID of the record.

        Returns:
            The record if found, else None

        Raises:
            RecordNotFoundError: If the record is not found in the database.
            DatabaseOperationError: If the operation fails due to database issues.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_field(self, model_name: str, field: str, value: Any) -> Any:
        """
        Fetches a record by a specific field's value.

        Args:
            model_name: Name of the model.
            field: Name of the field.
            value: Value of the field.

        Returns:
            The record if found, else None

        Raises:
            RecordNotFoundError: If the record is not found in the database.
            DatabaseOperationError: If the operation fails due to database issues.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_many(
        self,
        model_name: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[Union[str, Dict[str, int], List[Tuple[str, int]]]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[Any]:
        """
        Fetches all records of a model based on filters, sort orders, and pagination.

        Args:
            model_name: Name of the model.
            filters: Dictionary of filters to apply.
            sort: Sorting order.
            page: Page number.
            page_size: Number of records per page.

        Returns:
            List of records of the model.

        Raises:
            DatabaseOperationError: If the operation fails due to database issues.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, model_name: str, record: Dict[str, Any]) -> Any:
        """
        Creates a new record in a model.

        Args:
            model_name: Name of the model.
            record: Dictionary with fields and their values for the new record.

        Returns:
            The created record.

        Raises:
            DatabaseOperationError: If the operation fails due to database issues.
            ValidationError: If the provided data doesn't match the expected format.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, model_name: str, _id: int, update: Dict[str, Any]) -> Any:
        """
        Updates a record in a model with new values.

        Args:
            model_name: Name of the model.
            _id: ID of the record.
            update: Dictionary with Fields and their new values for update record.

        Returns:
            The updated record.

        Raises:
            RecordNotFoundError: If the record is not found in the database.
            DatabaseOperationError: If the operation fails due to database issues.
            ValidationError: If the provided data doesn't match the expected format.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_or_create(
        self, model_name: str, defaults: Dict[str, Any], update: Dict[str, Any]
    ) -> Any:
        """
        Updates a record if it exists, else creates it.

        Args:
            model_name: Name of the model.
            defaults: Fields and their values for the new record (if creation happens).
            update: Fields and their new values (if update happens).

        Returns:
            The updated or created record.

        Raises:
            DatabaseOperationError: If the operation fails due to database issues.
            ValidationError: If the provided data doesn't match the expected format.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, model_name: str, _id: int) -> None:
        """
        Deletes a record from a model.

        Args:
            model_name: Name of the model.
            _id: ID of the record.

        Raises:
            RecordNotFoundError: If the record is not found in the database.
            DatabaseOperationError: If the operation fails due to database issues.
            InvalidQueryError: If the query (model_name) is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def bulk_create(self, model_name: str, records: List[Dict[str, Any]]) -> None:
        """
        Creates multiple new records in a model.

        Args:
            model_name: Name of the model.
            records: List of dictionaries.
                     Each dictionary has fields and their values for a new record.

        Raises:
            DatabaseOperationError: If the operation fails due to database issues.
            ValidationError: If the provided data doesn't match the expected format.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def bulk_update(
        self, model_name: str, filters: Dict[str, Any], update: Dict[str, Any]
    ) -> None:
        """
        Updates multiple records in a model with new values.

        NOTE: Same update is applied to all matching records.

        Args:
            model_name: Name of the model.
            filters: Fields and their values to filter records.
            update: Dictionary with fields and their new values.
                    Will be applied to all matched records.

        Raises:
            DatabaseOperationError: If the operation fails due to database issues.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def bulk_delete(self, model_name: str, filters: Dict[str, Any]) -> None:
        """
        Deletes multiple records from a model.

        Args:
            model_name: Name of the model.
            filters: Fields and their values to filter records.

        Raises:
            DatabaseOperationError: If the operation fails due to database issues.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self, model_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Counts the number of records in a model based on filters.

        Args:
            model_name: Name of the model.
            filters: Dictionary of filters to apply.

        Returns:
            Count of records.

        Raises:
            DatabaseOperationError: If the operation fails due to database issues.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @abstractmethod
    async def exists(self, model_name: str, filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Checks if a record exists in a model.

        Args:
            model_name: Name of the model.
            filters: Dictionary of filters to apply.

        Returns:
            True if exists, else False.

        Raises:
            DatabaseOperationError: If the operation fails due to database issues.
            InvalidQueryError: If the query is not formed correctly.
        """
        raise NotImplementedError

    @staticmethod
    def validate_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the provided filters dictionary.

        Args:
            filters: Dictionary of filters to validate.

        Returns:
            The same filter dictionary if validation passed.

        Raises:
            InvalidQueryError: If filter key is not a valid column name,
                        or filter value is not of a valid type
                        (int, float, str, bool, None),
                        or filter value for valid operators is not a list.
        """
        # TODO: Improve filter validation to prevent SQL Injection
        # The validation could involve checking the keys and values in the dictionary,
        # and raising an error if they contain unexpected characters.
        # This could be as simple as a regex check, or as complex as a full SQL parser.
        valid_operators = [
            "$eq",
            "$ne",
            "$gt",
            "$gte",
            "$lt",
            "$lte",
            "$in",
            "$nin",
            "$and",
            "$or",
        ]
        for key, value in filters.items():
            if key in valid_operators:
                if key in ["$in", "$nin"] and not isinstance(value, list):
                    raise InvalidQueryError(f"Value for {key} should be of type list")
                elif key in ["$and", "$or"]:
                    if not isinstance(value, list):
                        raise InvalidQueryError(f"Value for {key} should be of type list")
                    for v in value:
                        BaseDAO.validate_filters(v)
            else:
                if not re.match(
                    r"^[a-zA-Z_][a-zA-Z0-9_]*$", key
                ):  # Check key for valid column name
                    raise InvalidQueryError(f"Invalid key {key} in filter")
                if isinstance(value, dict):  # For nested filters
                    BaseDAO.validate_filters(value)
                else:
                    if not isinstance(
                        value, (int, float, str, bool, type(None))
                    ):  # Check value for valid types
                        raise InvalidQueryError(f"Invalid value {value} in filter")

        return filters

    @staticmethod
    def validate_sort(
        sort: Union[str, Dict[str, int], List[Tuple[str, int]]]
    ) -> Union[str, Dict[str, int], List[Tuple[str, int]]]:
        """
        Validates the provided sort parameter.

        Args:
            sort: The sort parameter to validate. Can be a string, dictionary or list of tuples.

        Returns:
            The same sort parameter if validation passed.

        Raises:
            InvalidQueryError: If sort key is not a valid column name,
                        or sort value is not -1 or 1,
                        or sort item is not a tuple of size 2,
                        or sort is not of a valid type (str, dict, list).
        """

        def is_valid_column_name(name: str) -> bool:
            return bool(re.match(r"^-?[a-zA-Z_][a-zA-Z0-9_]*$", name))

        if isinstance(sort, str):
            sort_fields = sort.split(",")
            for field in sort_fields:
                if not is_valid_column_name(field):
                    raise InvalidQueryError(f"Invalid sort field: {field}")
        elif isinstance(sort, dict):
            for key, value in sort.items():
                if not is_valid_column_name(key):
                    raise InvalidQueryError(f"Invalid sort key: {key}")
                if value not in (-1, 1):
                    raise InvalidQueryError(
                        f"Invalid sort value: {value}, allowed values are -1 and 1"
                    )
        elif isinstance(sort, list):
            for item in sort:
                if not isinstance(item, tuple) or len(item) != 2:
                    raise InvalidQueryError(
                        f"Invalid sort item: {item}, it should be a tuple of size 2"
                    )
                if not is_valid_column_name(item[0]):
                    raise InvalidQueryError(f"Invalid sort key: {item[0]}")
                if item[1] not in (-1, 1):
                    raise InvalidQueryError(
                        f"Invalid sort value: {item[1]}, allowed values are -1 and 1"
                    )
        else:
            raise InvalidQueryError(
                f"Invalid sort type: {type(sort).__name__}, allowed types are "
                f"str, dict, and list of tuples"
            )

        return sort


class SQLDAO(BaseDAO):
    """Generic DAO for SQL databases using tortoise-orm.

    Provides methods for Create, Read, Update, and Delete operations.
    These methods are all asynchronous and therefore should be used in an
    asynchronous context.

    Usage:
        ```
        config = DatabaseConfig(uri='sqlite://db.sqlite3', database='test', models=['app.models'])
        crud = SQLDAO(config=config)
        crud.init()
        ```

    Attributes:
        config: Database configuration.
    """

    model_config = ConfigDict(extra="ignore")

    tortoise_config: Dict = None

    @model_validator(mode="before")
    def prepare_tortoise_config(self) -> "SQLDAO":
        """
        Prepares the configuration for Tortoise ORM.

        This function extracts the configuration from the instance (if it exists),
        builds a specific configuration for Tortoise ORM, and stores it back
        into the instance. The configuration includes connections (master and slave),
        apps (with their respective models), and specified routers.

        Note: The function uses the 'model_validator' decorator, which validates the models
        before they are used in the function.

        Returns:
            SQLDAO: Returns the instance of the SQL Data Access Object (DAO) with updated
            tortoise configuration.
        """
        config = self["config"]
        if config and "tortoise_config" not in self:
            tortoise_config = {
                "connections": {"master": config.uri, "slave": config.uri},
                "apps": {
                    config.database: {
                        "models": config.models,
                        "default_connection": "master",
                    }
                },
                "routers": ["eazyapi.dao.TortoiseDefaultRouter"],
            }
            self["tortoise_config"] = tortoise_config
        return self

    @property
    def connections(self) -> Any:
        """Get tortoise connections object.

        Returns:
            Any: connections singleton object
        """
        return connections

    async def init(self) -> None:  # noqa: D102
        try:
            await Tortoise.init(self.tortoise_config)
            await Tortoise.generate_schemas()
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to initialize connection: {str(e)}")

    async def close(self) -> None:  # noqa: D102
        try:
            await connections.close_all()
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to close connection: {str(e)}")

    async def get_by_id(self, model_name: str, _id: int) -> Dict:  # noqa: D102
        # TESTED: ❌
        ModelClass = self._get_model(model_name)
        try:
            obj = await ModelClass.get(_id=_id)
            return obj.to_dict() if obj else None
        except DoesNotExist:
            raise RecordNotFoundError("Record not found")
        except Exception as e:
            raise DatabaseOperationError(f"Failed to fetch record: {str(e)}")

    async def get_by_field(self, model_name: str, field: str, value: Any) -> Dict:  # noqa: D102
        # TESTED: ❌
        ModelClass = self._get_model(model_name)
        try:
            obj = await ModelClass.get(**{field: value})
            return obj.to_dict() if obj else None
        except DoesNotExist:
            raise RecordNotFoundError("Record not found")
        except Exception as e:
            raise DatabaseOperationError(f"Failed to fetch record: {str(e)}")

    async def get_many(  # noqa: D102
        self,
        model_name: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[Union[str, Dict[str, int], List[Tuple[str, int]]]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[Dict]:
        # TESTED: ❌
        ModelClass = self._get_model(model_name)
        query = ModelClass.filter(self._prepare_filters(filters)) if filters else ModelClass.all()

        if sort:
            query = query.order_by(*self._prepare_sorting(sort))

        if page is not None and page_size is not None:
            query = query.offset((page - 1) * page_size).limit(page_size)

        try:
            return [obj.to_dict() for obj in await query]
        except Exception as e:
            raise DatabaseOperationError(f"Failed to fetch records: {str(e)}")

    async def create(self, model_name: str, record: Dict[str, Any]) -> Dict:  # noqa: D102
        # TESTED: ❌
        ModelClass = self._get_model(model_name)
        try:
            obj = await ModelClass.create(**record)
            return obj.to_dict()
        except IntegrityError:
            raise DatabaseOperationError("Failed to create record due to IntegrityError")
        except Exception as e:
            raise DatabaseOperationError(f"Failed to create record: {str(e)}")

    async def update(  # noqa: D102
        self, model_name: str, _id: int, update: Dict[str, Any]
    ) -> Dict:
        # TESTED: ❌
        ModelClass = self._get_model(model_name)
        try:
            obj = await ModelClass.get(_id=_id)
            await obj.update_from_dict(update).save()
            return obj.to_dict()
        except DoesNotExist:
            raise RecordNotFoundError("Record not found")
        except Exception as e:
            raise DatabaseOperationError(f"Failed to update record: {str(e)}")

    async def update_or_create(  # noqa: D102
        self, model_name: str, defaults: Dict[str, Any], update: Dict[str, Any]
    ) -> Dict:
        # TESTED: ❌
        # TODO:
        # [ ] Make interface consistent (here as well as in base class)
        # [ ] Make sure exceptions are being handled with proper type handling (+ base)

        ModelClass = self._get_model(model_name)
        try:
            obj, created = await ModelClass.update_or_create(defaults, update)
            return obj.to_dict()
        except Exception as e:
            raise DatabaseOperationError(f"Failed to update record: {str(e)}")

    async def delete(self, model_name: str, _id: int) -> None:  # noqa: D102
        # TESTED: ❌
        ModelClass = self._get_model(model_name)
        try:
            obj = await ModelClass.get(_id=_id)
            await obj.delete()
        except DoesNotExist:
            raise RecordNotFoundError("Record not found")
        except Exception as e:
            raise DatabaseOperationError(f"Failed to delete record: {str(e)}")

    async def bulk_create(  # noqa: D102
        self, model_name: str, records: List[Dict[str, Any]]
    ) -> None:
        # TESTED: ❌
        ModelClass = self._get_model(model_name)
        try:
            await ModelClass.bulk_create([ModelClass(**obj) for obj in records])
        except Exception as e:
            raise DatabaseOperationError(f"Failed to create records: {str(e)}")

    async def bulk_update(  # noqa: D102
        self, model_name: str, filters: Dict[str, Any], update: Dict[str, Any]
    ) -> None:
        # TESTED: ❌
        try:
            ModelClass = self._get_model(model_name)
            await ModelClass.filter(self._prepare_filters(filters)).update(**update)
        except InvalidQueryError as e:
            raise e
        except Exception as e:
            raise DatabaseOperationError(f"Failed to update records: {str(e)}")

    async def bulk_delete(self, model_name: str, filters: Dict[str, Any]) -> None:  # noqa: D102
        # TESTED: ❌
        try:
            ModelClass = self._get_model(model_name)
            await ModelClass.filter(self._prepare_filters(filters)).delete()
        except InvalidQueryError as e:
            raise e
        except Exception as e:
            raise DatabaseOperationError(f"Failed to delete records: {str(e)}")

    async def count(  # noqa: D102
        self, model_name: str, filters: Optional[Dict[str, Any]] = None
    ) -> int:
        # TESTED: ❌
        try:
            ModelClass = self._get_model(model_name)
            if filters:
                return await ModelClass.filter(self._prepare_filters(filters)).count()
            return await ModelClass.all().count()
        except InvalidQueryError as e:
            raise e
        except Exception as e:
            raise DatabaseOperationError(f"Failed to count records: {str(e)}")

    async def exists(  # noqa: D102
        self, model_name: str, filters: Optional[Dict[str, Any]] = None
    ) -> bool:
        # TESTED: ❌
        try:
            ModelClass = self._get_model(model_name)
            if filters:
                return await ModelClass.filter(self._prepare_filters(filters)).exists()
            return await ModelClass.all().exists()
        except InvalidQueryError as e:
            raise e
        except Exception as e:
            raise DatabaseOperationError(f"Failed to check if record exists: {str(e)}")

    def _get_model(self, model_name: str) -> Type[Model]:
        """
        Gets the model class from its name.

        Args:
            model_name: Name of the model.

        Returns:
            The model class.

        Raises:
            InvalidQueryError: If model_name is not valid.
        """
        if not re.match(
            r"^[a-zA-Z_][a-zA-Z0-9_]*$", model_name
        ):  # Simple validation for SQL Injection
            raise InvalidQueryError(f"Invalid model name: {model_name}")
        # Model = None
        try:
            Model = Tortoise.get_model(self.config.database, model_name)
        except Exception as e:
            raise InvalidQueryError(f"Error getting model {model_name}: {str(e)}")
        return Model

    def _prepare_filters(self, filters: Dict[str, Any], no_validate: bool = False) -> "Q":
        """
        Recursively apply filters to a query.

        Args:
            filters: Dictionary of filters to apply.
            no_validate: If True, skip the validation of filters. Defaults to False.

        Returns:
            Query with applied filters.

        Raises:
            InvalidQueryError: If filters key is not valid.
        """
        try:
            if not no_validate:
                _ = self.validate_filters(filters)
        except InvalidQueryError as e:
            raise e

        conditions = []
        for key, value in filters.items():
            if key == "$and":
                conditions.append(Q(*[self._prepare_filters(v, no_validate=True) for v in value]))
            elif key == "$or":
                conditions.append(
                    Q(*[self._prepare_filters(v, no_validate=True) for v in value], join_type="OR")
                )
            else:
                if isinstance(value, dict):
                    for op, val in value.items():
                        if op == "$eq":
                            conditions.append(Q(**{f"{key}__exact": val}))
                        elif op == "$ne":
                            conditions.append(~Q(**{f"{key}__exact": val}))
                        elif op == "$gt":
                            conditions.append(Q(**{f"{key}__gt": val}))
                        elif op == "$gte":
                            conditions.append(Q(**{f"{key}__gte": val}))
                        elif op == "$lt":
                            conditions.append(Q(**{f"{key}__lt": val}))
                        elif op == "$lte":
                            conditions.append(Q(**{f"{key}__lte": val}))
                        elif op == "$in":
                            conditions.append(Q(**{f"{key}__in": val}))
                        elif op == "$nin":
                            conditions.append(~Q(**{f"{key}__in": val}))
                elif isinstance(value, str):
                    if value.startswith(">="):
                        conditions.append(Q(**{f"{key}__gte": float(value[2:])}))
                    elif value.startswith(">"):
                        conditions.append(Q(**{f"{key}__gt": float(value[1:])}))
                    elif value.startswith("<="):
                        conditions.append(Q(**{f"{key}__lte": float(value[2:])}))
                    elif value.startswith("<"):
                        conditions.append(Q(**{f"{key}__lt": float(value[1:])}))
                    elif value.startswith("!="):
                        conditions.append(~Q(**{f"{key}__exact": float(value[2:])}))
                    elif value.startswith("="):
                        conditions.append(Q(**{f"{key}__exact": float(value[1:])}))
                    else:
                        conditions.append(Q(**{f"{key}__exact": value}))
        return Q(*conditions)

    def _prepare_sorting(
        self, sort: Union[str, Dict[str, int], List[Tuple[str, int]]], no_validate: bool = False
    ) -> List[str]:
        """
        Prepare the sorting for a query.

        Args:
            sort: The sorting order.
            no_validate: If True, skip the validation of filters. Defaults to False.

        Returns:
            Query with applied sorting.

        Raises:
            InvalidQueryError: If sort key is not valid.
        """
        # TODO: Add sort validation to prevent SQL Injection
        try:
            if not no_validate:
                _ = self.validate_sort(sort)
        except InvalidQueryError as e:
            raise e

        if isinstance(sort, str):
            sort_fields = sort.split(",")
            sort = [field.strip() for field in sort_fields]
        elif isinstance(sort, dict):
            sort = [f"-{k}" if v == -1 else k for k, v in sort.items()]
        elif isinstance(sort, list):
            sort = [f"-{field[0]}" if field[1] == -1 else field[0] for field in sort]
        return sort


class TortoiseDefaultRouter:
    """
    Default router for Tortoise ORM.

    This router directs all read operations to the 'slave' database and all write operations
    to the 'master' database.
    """

    def db_for_read(self, model: Type[Model]) -> str:
        """
        Determines the database to use for read operations for a given model.

        Args:
            model (Type[Model]): The model for which the database needs to be determined.

        Returns:
            str: The name of the database to be used for read operations.
                 In this case, it's 'slave'.
        """
        return "slave"

    def db_for_write(self, model: Type[Model]) -> str:
        """
        Determines the database to use for write operations for a given model.

        Args:
            model (Type[Model]): The model for which the database needs to be determined.

        Returns:
            str: The name of the database to be used for write operations.
                 In this case, it's 'master'.
        """
        return "master"
