from pydantic import BaseModel
from typing import ClassVar, Any, Optional
from ..adaptor.interface import RedisAdaptor
from ..exceptions import (
    model_repeat_set_check,
    RepeatedSetAdaptorError,
    RepeatedSetModelMetadataError,
    RepeatedSetKeyBuilderError,
    RepeatedSetSerializerError,
)
from .metadata import ModelMetadata
from ..d_type import SelfInstance, RedisDataType
from ..core.key_builder import KeyBuilderProtocol
from ..core.serializer import SerializerProtocol


class BaseRedisModel(BaseModel):
    __redis_type__: ClassVar[RedisDataType]
    __key_pattern__: ClassVar[str]
    __schema__: ClassVar[Optional[str]] = None

    # the app will set value for them, can't repeat set it
    __redis_adaptor__: ClassVar[Optional[RedisAdaptor]] = None
    __model_meta__: ClassVar[Optional[ModelMetadata]] = None
    __key_builder__: ClassVar[Optional[KeyBuilderProtocol]] = None
    __serializer__: ClassVar[Optional[SerializerProtocol]] = None

    @classmethod
    def set_redis_adaptor(cls, adaptor: RedisAdaptor):
        """Sets the RedisAdaptor instance for all BaseRedisModel subclasses."""
        cls.__redis_adaptor__ = adaptor

    @classmethod
    def set_key_builder(cls, key_builder: KeyBuilderProtocol):
        """Sets the KeyBuilder instance for all BaseRedisModel subclasses."""
        if not isinstance(key_builder, KeyBuilderProtocol):
            raise ValueError(f"The key builder {key_builder} is not KeyBuilderProtocol's implemented.")
        cls.__key_builder__ = key_builder

    @classmethod
    def set_serializer(cls, serializer: SerializerProtocol):
        if not isinstance(serializer, SerializerProtocol):
            raise ValueError(f"The serializer {serializer} is not SerializerProtocol's implemented.")
        cls.__serializer__ = serializer

    @classmethod
    def get_driver(cls):
        if cls.__redis_adaptor__ is None:
            raise RuntimeError("RedisAdaptor has not been set. Call BaseRedisModel.set_redis_adaptor() first.")
        return cls.__redis_adaptor__.get_redis_driver(cls.__redis_type__)

    @classmethod
    def get(cls, pk: Any) -> SelfInstance:
        driver = cls.get_driver()
        primary_key = cls.primary_key(pk)
        result = driver.get(primary_key)
        return result.then(
            lambda x: cls.__serializer__.deserialize(x, cls)
        ).execute()

    def delete(self) -> None:
        driver = self.get_driver()
        return driver.delete(self.get_primary_key()).execute()

    def expire(self, ttl: int) -> None:
        driver = self.get_driver()
        return driver.expire(key=self.get_primary_key(), ttl=ttl).execute()

    def save(self) -> SelfInstance:
        driver = self.get_driver()
        value = self.__serializer__.serialize(self)
        return driver.commit(key=self.get_primary_key(), value=value).execute()

    def __setitem__(self, key, value):
        if key == '__redis_adaptor__':
            model_repeat_set_check(self, key, RepeatedSetAdaptorError, RedisAdaptor)
        if key == '__model_meta__':
            model_repeat_set_check(self, key, RepeatedSetModelMetadataError, ModelMetadata)
        if key == '__key_builder__':
            model_repeat_set_check(self, key, RepeatedSetKeyBuilderError, KeyBuilderProtocol)
        if key == '__serializer__':
            model_repeat_set_check(self, key, RepeatedSetSerializerError, SerializerProtocol)
        super().__setitem__(key, value)

    def pk_info(self):
        pk_field = self.__model_meta__.pk_info
        pk_field_name = list(pk_field.keys()).pop()
        return getattr(self, pk_field_name), pk_field_name

    def get_primary_key(self) -> str:
        """Get the primary key for this model instance.

        Returns:
            Redis key string (e.g., 'User:123')

        Raises:
            RuntimeError: If key_builder has not been set
        """
        pk_value, _ = self.pk_info()
        return self.primary_key(pk=pk_value)

    @classmethod
    def primary_key(cls, pk: Optional[Any] = None) -> str:
        """Generate the primary key for this model instance.

        Args:
            pk: Primary key value. If None, uses the instance's pk value.
                For class-level calls, pk must be provided.

        Returns:
            Redis key string (e.g., 'User:123')

        Raises:
            RuntimeError: If key_builder has not been set
            ValueError: If pk is None and cannot be determined
        """
        if cls.__key_builder__ is None:
            raise RuntimeError(
                "KeyBuilder has not been set. "
                "Call BaseRedisModel.set_key_builder() or initialize FlameModel first."
            )
        if pk is None:
            raise ValueError(
                "pk parameter is required for class-level primary_key() calls. "
                "For instance-level, use instance.get_primary_key() instead."
            )
        # Get primary key metadata
        pk_field_info = cls.__model_meta__.pk_info
        pk_field_name = list(pk_field_info.keys())[0]
        # Build and return the primary key
        return cls.__key_builder__.primary_key(
            model=cls,
            shard_tags=cls.__model_meta__.shard_tags,
            pk=pk,
            pk_field_name=pk_field_name,
            pk_field_info=pk_field_info
        )
