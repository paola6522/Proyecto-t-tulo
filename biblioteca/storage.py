# biblioteca/storage.py
from cloudinary_storage.storage import RawMediaCloudinaryStorage as BaseRawMediaCloudinaryStorage

class RawMediaCloudinaryStorage(BaseRawMediaCloudinaryStorage):
    """
    Usamos la clase RAW oficial de cloudinary_storage.
    Esto fuerza resource_type='raw' y usa la config correcta para PDFs.
    """
    pass

