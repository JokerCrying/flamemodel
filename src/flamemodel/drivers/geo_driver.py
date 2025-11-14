from .base_driver import BaseDriver


class GeoDriver(BaseDriver):
    def geoadd(self, key: str, *values):
        # values: (longitude, latitude, member)
        return self.adaptor.proxy.geoadd(key, *values)

    def georadius(self, key: str, longitude: float, latitude: float, radius: float, unit: str = "m"):
        return self.adaptor.proxy.georadius(key, longitude, latitude, radius, unit=unit)

    def geopos(self, key: str, *members):
        return self.adaptor.proxy.geopos(key, *members)

    def geodist(self, key: str, member1: str, member2: str, unit: str = "m"):
        return self.adaptor.proxy.geodist(key, member1, member2, unit=unit)
