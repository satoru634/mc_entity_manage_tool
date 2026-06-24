class Point3D:
    def __init__(self, x: int = 0, y: int = 0, z: int = 0) -> None:
        self.__x = x
        self.__y = y
        self.__z = z
        return

    def __str__(self) -> str:
        return "x: {0}, y: {1}, z: {2}".format(self.__x, self.__y, self.__z)

    def get_x(self) -> int:
        return self.__x

    def get_y(self) -> int:
        return self.__y

    def get_z(self) -> int:
        return self.__z

    def set_x(self, x: int) -> None:
        self.__x = x
        return

    def set_y(self, y: int) -> None:
        self.__y = y
        return

    def set_z(self, z: int) -> None:
        self.__z = z
        return

    def max(self, x: int, y: int, z: int) -> None:
        self.__x = max(x, self.__x)
        self.__y = max(y, self.__y)
        self.__z = max(z, self.__z)
        return

    def min(self, x: int, y: int, z: int) -> None:
        self.__x = min(x, self.__x)
        self.__y = min(y, self.__y)
        self.__z = min(z, self.__z)
        return

    def shift(self, x: int, y: int, z: int) -> None:
        self.__x += x
        self.__y += y
        self.__z += z
        return

    def shift_all(self, shift_count: int) -> None:
        self.shift(shift_count, shift_count, shift_count)
        return
