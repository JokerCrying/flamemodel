from typing import Any, List, Optional, Tuple
from .redis_model import BaseRedisModel
from ..d_type import SelfInstance


class Geo(BaseRedisModel):
    __redis_type__ = 'geo'

    @classmethod
    def _geo_fields(cls) -> Tuple[str, str, str]:
        """:return (member_field, longitude_field, latitude_field)"""
        meta = cls.__model_meta__
        member = list(meta.member_field.keys())[0]
        lon = list(meta.lng_field.keys())[0]
        lat = list(meta.lat_field.keys())[0]
        return member, lon, lat

    @property
    def geo_tuple(self) -> Tuple[float, float, str]:
        """:return (longitude, latitude, member_id)"""
        member_f, lon_f, lat_f = self._geo_fields()
        return (
            float(getattr(self, lon_f)),
            float(getattr(self, lat_f)),
            str(getattr(self, member_f))
        )

    def save(self) -> SelfInstance:
        """save Geo + Hash"""
        pk_key = self.get_primary_key()
        driver = self.get_driver()
        # step1. Save Geo data and hash key id
        lon, lat, member_id = self.geo_tuple
        driver.geoadd(pk_key, lon, lat, member_id)
        # step2. Save full data to hash
        hash_key = f"{pk_key}:data"
        hash_driver = self.__redis_adaptor__.get_redis_driver('hash')
        serialized = self.__serializer__.serialize(self)
        hash_driver.hset(hash_key, member_id, serialized)
        return self

    @classmethod
    def add(cls, pk: Any, *members: SelfInstance) -> int:
        """Batch add geographical location points"""
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        hash_driver = cls.__redis_adaptor__.get_redis_driver('hash')
        hash_key = f"{pk_key}:data"
        # Geo batch add
        geo_values = []
        for member in members:
            lon, lat, member_id = member.geo_tuple
            geo_values.extend([lon, lat, member_id])
            # Hash batch add
            hash_driver.hset(hash_key, member_id, cls.__serializer__.serialize(member))
        return driver.geoadd(pk_key, *geo_values)

    @classmethod
    def search_radius(cls, pk: Any, longitude: float, latitude: float,
                      radius: float, unit: str = "m",
                      count: Optional[int] = None) -> List[SelfInstance]:
        """Search around the specified coordinates and return the complete object"""
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        # step1. get member ids from geo
        member_ids = driver.georadius(pk_key, longitude, latitude, radius, unit)
        # step2. get full data in hash
        hash_key = f"{pk_key}:data"
        hash_driver = cls.__redis_adaptor__.get_redis_driver('hash')
        results = []
        for member_id in member_ids:
            data = hash_driver.hget(hash_key, member_id)
            if data:
                results.append(cls.__serializer__.deserialize(data, cls))
        return results[:count]

    @classmethod
    def get_by_member(cls, pk: Any, member_id: str) -> Optional[SelfInstance]:
        """Get the full data through member_id"""
        pk_key = cls.primary_key(pk)
        hash_key = f"{pk_key}:data"
        hash_driver = cls.__redis_adaptor__.get_redis_driver('hash')

        data = hash_driver.hget(hash_key, member_id)
        if data:
            return cls.__serializer__.deserialize(data, cls)
        return None

    def delete_self(self) -> int:
        """Delete the current location point (remove from Geo and Hash)"""
        pk_key = self.get_primary_key()
        _, _, member_id = self.geo_tuple
        # step1. delete geo data
        driver = self.__redis_adaptor__.get_redis_driver('zset')
        driver.zrem(pk_key, member_id)
        # step2. delete hash data
        hash_key = f"{pk_key}:data"
        hash_driver = self.__redis_adaptor__.get_redis_driver('hash')
        return hash_driver.hdel(hash_key, member_id)
