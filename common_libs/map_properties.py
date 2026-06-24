import re
import humps
import os
import math


class MapProperties:
    def __init__(self, input_path: str) -> None:
        self.__input_path = input_path

        self.__org_properties = [
            "minZoom",
            "maxZoom",
            "minRegionX",
            "minRegionZ",
            "maxRegionX",
            "maxRegionZ",
        ]

        self.min_zoom = 0
        self.max_zoom = 0
        self.min_region_x = 0
        self.min_region_z = 0
        self.max_region_x = 0
        self.max_region_z = 0
        self.dpi_scale = 1
        self.world_tile_size = 256
        self.zoom_info_list = {}
        return

    def get(self):
        with open(os.path.join(self.__input_path, "unmined.map.properties.js")) as f:
            data = f.read()

        for property in self.__org_properties:
            pattern = property + r": [+-]?\d{1,5}"
            m = re.search(pattern, data).group()
            snake_property = humps.decamelize(property)
            formula = "self.{} = value".format(snake_property)
            value = int(m.split("{}: ".format(property))[-1])
            exec(formula)

        self.world_min_x = self.min_region_x * 512
        self.world_min_y = self.min_region_z * 512
        self.world_width = (self.max_region_x + 1 - self.min_region_x) * 512
        self.world_height = (self.max_region_z + 1 - self.min_region_z) * 512
        self.world_max_zoom_factor = 2**self.max_zoom
        self.map_zoom_levels = self.max_zoom - self.min_zoom

        for z in range(self.map_zoom_levels + 1):
            world_zoom = self.min_zoom + z
            world_zoom_factor = 2**world_zoom

            self.zoom_info_list[world_zoom] = {
                "resolutions": (z**2) * self.dpi_scale / self.world_max_zoom_factor,
                "world_zoom_factor": world_zoom_factor,
                "min_tile_x": math.floor(
                    self.world_min_x * world_zoom_factor / self.world_tile_size
                ),
                "min_tile_y": math.floor(
                    self.world_min_y * world_zoom_factor / self.world_tile_size
                ),
                "max_tile_x": math.ceil(
                    (self.world_min_x + self.world_width)
                    * world_zoom_factor
                    / self.world_tile_size
                )
                - 1,
                "max_tile_y": math.ceil(
                    (self.world_min_y + self.world_height)
                    * world_zoom_factor
                    / self.world_tile_size
                )
                - 1,
            }

        return
