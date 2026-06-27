import pytest
from modules.point_3d import Point3D


class TestPoint3DInit:
    def test_default_values(self):
        p = Point3D()
        assert p.get_x() == 0
        assert p.get_y() == 0
        assert p.get_z() == 0

    def test_custom_values(self):
        p = Point3D(1, 2, 3)
        assert p.get_x() == 1
        assert p.get_y() == 2
        assert p.get_z() == 3

    def test_negative_values(self):
        p = Point3D(-10, -20, -30)
        assert p.get_x() == -10
        assert p.get_y() == -20
        assert p.get_z() == -30


class TestPoint3DStr:
    def test_str_default(self):
        p = Point3D()
        assert str(p) == "x: 0, y: 0, z: 0"

    def test_str_custom(self):
        p = Point3D(5, 10, 15)
        assert str(p) == "x: 5, y: 10, z: 15"


class TestPoint3DSetters:
    def test_set_x(self):
        p = Point3D()
        p.set_x(99)
        assert p.get_x() == 99

    def test_set_y(self):
        p = Point3D()
        p.set_y(88)
        assert p.get_y() == 88

    def test_set_z(self):
        p = Point3D()
        p.set_z(77)
        assert p.get_z() == 77

    def test_set_overwrite_existing(self):
        p = Point3D(1, 2, 3)
        p.set_x(10)
        p.set_y(20)
        p.set_z(30)
        assert p.get_x() == 10
        assert p.get_y() == 20
        assert p.get_z() == 30


class TestPoint3DMax:
    def test_max_updates_all(self):
        p = Point3D(0, 0, 0)
        p.max(5, 10, 15)
        assert p.get_x() == 5
        assert p.get_y() == 10
        assert p.get_z() == 15

    def test_max_no_update_when_smaller(self):
        p = Point3D(100, 200, 300)
        p.max(1, 2, 3)
        assert p.get_x() == 100
        assert p.get_y() == 200
        assert p.get_z() == 300

    def test_max_partial_update(self):
        p = Point3D(5, 5, 5)
        p.max(10, 0, 10)
        assert p.get_x() == 10
        assert p.get_y() == 5
        assert p.get_z() == 10

    def test_max_equal_value(self):
        p = Point3D(5, 5, 5)
        p.max(5, 5, 5)
        assert p.get_x() == 5
        assert p.get_y() == 5
        assert p.get_z() == 5


class TestPoint3DMin:
    def test_min_updates_all(self):
        p = Point3D(100, 200, 300)
        p.min(1, 2, 3)
        assert p.get_x() == 1
        assert p.get_y() == 2
        assert p.get_z() == 3

    def test_min_no_update_when_larger(self):
        p = Point3D(0, 0, 0)
        p.min(5, 10, 15)
        assert p.get_x() == 0
        assert p.get_y() == 0
        assert p.get_z() == 0

    def test_min_partial_update(self):
        p = Point3D(5, 5, 5)
        p.min(0, 10, 0)
        assert p.get_x() == 0
        assert p.get_y() == 5
        assert p.get_z() == 0

    def test_min_equal_value(self):
        p = Point3D(5, 5, 5)
        p.min(5, 5, 5)
        assert p.get_x() == 5
        assert p.get_y() == 5
        assert p.get_z() == 5


class TestPoint3DShift:
    def test_shift_positive(self):
        p = Point3D(1, 2, 3)
        p.shift(10, 20, 30)
        assert p.get_x() == 11
        assert p.get_y() == 22
        assert p.get_z() == 33

    def test_shift_negative(self):
        p = Point3D(10, 20, 30)
        p.shift(-5, -10, -15)
        assert p.get_x() == 5
        assert p.get_y() == 10
        assert p.get_z() == 15

    def test_shift_zero(self):
        p = Point3D(5, 10, 15)
        p.shift(0, 0, 0)
        assert p.get_x() == 5
        assert p.get_y() == 10
        assert p.get_z() == 15

    def test_shift_all(self):
        p = Point3D(1, 2, 3)
        p.shift_all(5)
        assert p.get_x() == 6
        assert p.get_y() == 7
        assert p.get_z() == 8

    def test_shift_all_negative(self):
        p = Point3D(10, 20, 30)
        p.shift_all(-10)
        assert p.get_x() == 0
        assert p.get_y() == 10
        assert p.get_z() == 20
