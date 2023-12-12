import string, random
from services.s3 import MinioClient
import uuid
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def convert_id_int_to_str(id):
    return "0"*(6 - len(str(id))) + str(id)

def upload_to(instance, filename):
    if hasattr(instance, "game_id"):
        instance.img.name = ".".join([str(uuid.uuid4()), instance.img.name.split(".")[-1]])
        name = f"game/{instance.game_id}/{instance.img.name}"
        # MinioClient.upload_data(name,instance.img.file, instance.img.size)
        return name
    else:
        instance.file.name = ".".join([str(uuid.uuid4()), instance.file.name.split(".")[-1]])
        name = f"game/{instance.file.name}"
        # MinioClient.upload_data(name, instance.file.file, instance.file.size)
        return name
    