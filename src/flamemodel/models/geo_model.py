from typing import Any, List, Optional, Tuple
from .redis_model import BaseRedisModel
from ..d_type import SelfInstance
from ..utils.action import Action


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
        geo_act = driver.geoadd(pk_key, (lon, lat, member_id))
        # step2. Save full data to hash
        hash_key = f"{pk_key}:data"
        hash_driver = self.__redis_adaptor__.get_redis_driver('hash')
        serialized = self.__serializer__.serialize(self)
        hash_act = hash_driver.hset(hash_key, member_id, serialized)
        return Action.transaction(
            [geo_act, hash_act],
            runtime_mode=self.__redis_adaptor__.runtime_mode,
            client=self.__redis_adaptor__.proxy
        ).then(lambda _: self).execute()

    @classmethod
    def add(cls, pk: Any, *members: SelfInstance) -> int:
        """Batch add geographical location points"""
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        hash_driver = cls.__redis_adaptor__.get_redis_driver('hash')
        hash_key = f"{pk_key}:data"
        # Geo batch add
        acts = []
        for member in members:
            lon, lat, member_id = member.geo_tuple
            # Hash batch add
            acts.append(
                hash_driver.hset(hash_key, member_id, cls.__serializer__.serialize(member))
            )
            acts.append(driver.geoadd(pk_key, (lon, lat, member_id)))
        return Action.sequence(
            acts,
            runtime_mode=cls.__redis_adaptor__.runtime_mode,
            result_from_index=-1,
            client=cls.__redis_adaptor__.proxy
        ).execute()

    @classmethod
    def search_radius(cls, pk: Any, longitude: float, latitude: float,
                      radius: float, unit: str = "m",
                      count: Optional[int] = None) -> List[SelfInstance]:

        """Search around the specified coordinates and return the complete object"""

        def _post_operation(res):
            hash_key = f"{pk_key}:data"
            hash_driver = cls.__redis_adaptor__.get_redis_driver('hash')
            actions = []
            for member_id in res:
                data = hash_driver.hget(hash_key, member_id)
                actions.append(
                    data.then(
                        lambda x: cls.__serializer__.deserialize(x, cls)
                    )
                )
            return Action.sequence(
                actions,
                runtime_mode=cls.__redis_adaptor__.runtime_mode,
                result_from_index=None,
                client=cls.__redis_adaptor__.proxy
            ).then(lambda x: x[:count]).execute()

        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        return driver.georadius(
            pk_key, longitude,
            latitude, radius, unit
        ).then(_post_operation).execute()

    @classmethod
    def get_by_member(cls, pk: Any, member_id: str) -> Optional[SelfInstance]:
        """Get the full data through member_id"""

        def _final_handler(r):
            result = cls.__serializer__.deserialize(r, cls)
            if result:
                return result
            return None

        pk_key = cls.primary_key(pk)
        hash_key = f"{pk_key}:data"
        hash_driver = cls.__redis_adaptor__.get_redis_driver('hash')
        return hash_driver.hget(hash_key, member_id).then(_final_handler).execute()

    def delete_self(self) -> int:
        """Delete the current location point (remove from Geo and Hash)"""
        pk_key = self.get_primary_key()
        acts = []
        _, _, member_id = self.geo_tuple
        # step1. delete geo data
        driver = self.__redis_adaptor__.get_redis_driver('zset')
        acts.append(driver.zrem(pk_key, member_id))
        # step2. delete hash data
        hash_key = f"{pk_key}:data"
        hash_driver = self.__redis_adaptor__.get_redis_driver('hash')
        acts.append(hash_driver.hdel(hash_key, member_id))
        return Action.sequence(
            acts,
            runtime_mode=self.__redis_adaptor__.runtime_mode,
            result_from_index=-1,
            client=self.__redis_adaptor__.proxy
        ).execute()
