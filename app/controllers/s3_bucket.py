import uuid

import boto3
import botocore
from pathlib import Path

from flask import current_app as app


class S3Bucket:
    def __init__(self):
        self.bucket_name = app.config['AWS_BUCKET_NAME']
        self.allowed_extensions = app.config['ALLOWED_EXTENSIONS']
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
        )

    def _generate_img_uid(self):
        return str(uuid.uuid4())[:8]

    def upload_cases_imgs(self, file, case_name, img_type='title') -> tuple[bool, str]:

        extension_files = file.filename.split(".")[-1]

        if extension_files not in self.allowed_extensions:
            return False, "File extension not allowed"

        file_name = f"{img_type}_{self._generate_img_uid()}.{extension_files}"

        img_path = Path("cases") / case_name.replace(' ', "-") / file_name

        try:
            self.s3.upload_fileobj(
                file,
                self.bucket_name,
                str(img_path),
                ExtraArgs={
                    "ContentType": file.content_type
                }
            )
            return True, f'https://{self.bucket_name}/' + str(img_path)
        except botocore.exceptions.ClientError as error:
            return False, error.response['Error']['Message']
