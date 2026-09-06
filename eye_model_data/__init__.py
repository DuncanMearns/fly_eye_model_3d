from eye_model_3d import EyeModel
from pathlib import Path
from abc import ABC, abstractmethod
import pandas as pd


__all__ = ["ZhaoDataset", "MappedDataset"]


class modelgetter:

    def __init__(self, folder):
        self.folder = folder

    def __get__(self, obj, cls):
        return {
            f.stem: f for f in Path(__file__).parent.joinpath("datasets", self.folder).iterdir()
        }


class DataLoader(ABC):

    _models = modelgetter(...)

    def __class_getitem__(cls, name):
        try:
            path = cls._models[name]
        except KeyError:
            raise KeyError(f"Unknown model: {name!r}")
        return cls.load(path)

    @staticmethod
    @abstractmethod
    def _model(cls, df, **kwargs):
        ...

    @classmethod
    def load(cls, path, **kwargs):
        df = pd.read_csv(path)
        df_left = df.query("side == 'left'")
        df_right = df.query("side == 'right'")
        eye_model_left = cls._model(df_left, **kwargs)
        kwargs["is_right"] = True
        eye_model_right = cls._model(df_right, **kwargs)
        return {
            "left": eye_model_left,
            "right": eye_model_right,
        }


class ZhaoDataset(DataLoader):

    _models = modelgetter("zhao_et_al_2025")

    @staticmethod
    def _model(df, **kwargs):
        xyz_l = df[["lens_x", "lens_y", "lens_z"]].values
        xyz_c = df[["cone_x", "cone_y", "cone_z"]].values
        pq = df[["p", "q"]].values.astype("i4")
        return EyeModel(xyz_l, xyz_c, pq, **kwargs)


class MappedDataset(DataLoader):

    _models = modelgetter("mapped")

    @staticmethod
    def _model(df, **kwargs):
        xyz_l = df[["x", "y", "z"]].values
        xyz_u = df[["dx", "dy", "dz"]].values
        xyz_c = xyz_l - xyz_u
        pq = df[["p", "q"]].values.astype("i4")
        columns = df["column_id"].values
        return EyeModel(xyz_l, xyz_c, pq, columns, **kwargs)
