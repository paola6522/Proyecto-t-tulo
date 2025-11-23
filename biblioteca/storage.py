from cloudinary_storage.storage import MediaCloudinaryStorage

class RawMediaCloudinaryStorage(MediaCloudinaryStorage):
    resource_type = "raw"
