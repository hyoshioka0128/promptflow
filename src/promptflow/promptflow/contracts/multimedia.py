import base64
import hashlib
import os
import uuid
from os import PathLike
from pathlib import Path
from typing import Callable


class PFBytes(bytes):
    """This class is used to represent a bytes object in PromptFlow.
    It has all the functionalities of a bytes object,
    and also has some additional methods to help with serialization and deserialization.
    """

    def __new__(cls, value: bytes, *args, **kwargs):
        # Here we must only pass the value to the bytes constructor,
        # otherwise we will get a type error that the constructor doesn't take such args.
        # See https://docs.python.org/3/reference/datamodel.html#object.__new__
        return super().__new__(cls, value)

    def __init__(self, data: bytes, mime_type: str, path : str = None):
        super().__init__()
        # Use this hash to identify this bytes.
        self._hash = hashlib.sha1(data).hexdigest()[:8]
        self._mime_type = mime_type
        self._path = path

    @staticmethod
    def get_extension_from_path(path: Path):
        return path.suffix[1:]

    @staticmethod
    def get_extension_from_type(mime_type: str):
        ext = mime_type.split("/")[-1]
        if ext == "*":
            return None
        return ext

    def save_to_file(self, file_path: PathLike):
        with open(file_path, 'wb') as file:
            file.write(self)

    @classmethod
    def get_file_reference_encoder(cls, folder_path: PathLike, relative_path: PathLike=None) -> Callable:
        def pfbytes_file_reference_encoder(obj):
            """Dumps PFBytes to a file and returns its reference."""
            if isinstance(obj, PFBytes):
                path = folder_path / relative_path if relative_path else folder_path
                ext = PFBytes.get_extension_from_type(obj._mime_type)
                file_name = f"{uuid.uuid4()}.{ext}" if ext else f"{uuid.uuid4()}"
                os.makedirs(path, exist_ok=True)
                obj.save_to_file(os.path.join(path, file_name))
                return {"pf_mime_type": obj._mime_type, "path": str(relative_path / file_name) if relative_path else file_name}
            raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)
        return pfbytes_file_reference_encoder


class Image(PFBytes):
    def __init__(self, data: bytes, mime_type: str = "image/*", path: str = None):
        return super().__init__(data, mime_type, path)

    @staticmethod
    def from_file(f: Path):
        ext = PFBytes.get_extension_from_path(f)
        mime_type = f"image/{ext}" if ext else "image/*"
        with open(f, "rb") as fin:
            return Image(fin.read(), mime_type=mime_type, path=f.name)

    def __str__(self):
        return f"Image({self._hash})"

    def to_base64(self):
        return base64.b64encode(self).decode("utf-8")

    def serialize(self, encoder: Callable):
        if encoder is None:
            return {"pf_mime_type": self._mime_type, "hash": self._hash}
        return encoder(self)
