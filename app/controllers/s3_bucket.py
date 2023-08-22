import uuid
import typing

import boto3
import botocore
from pathlib import Path


class S3Bucket:
    def init_app(self, app):
        self.bucket_name = app.config["AWS_BUCKET_NAME"]
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=app.config["AWS_ACCESS_KEY"],
            aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"],
        )

    def _generate_img_uid(self):
        return str(uuid.uuid4())

    def upload_cases_imgs(
        self, file, file_name: str, case_name: str, img_type="title"
    ) -> str:
        extension_files = file_name.split(".")[-1]

        re_file_name = f"{img_type}_{self._generate_img_uid()}.{extension_files}"

        img_path = Path("cases") / case_name.replace(" ", "-") / re_file_name

        try:
            self.s3.upload_fileobj(
                file,
                self.bucket_name,
                str(img_path),
                ExtraArgs={"ContentType": file.content_type},
            )
            return f"https://{self.bucket_name}/" + str(img_path)
        except botocore.exceptions.ClientError as error:
            raise TypeError(error.response["Error"]["Message"])

    def delete_cases_imgs(self, file_url: str):
        file_path = file_url.replace(f"https://{self.bucket_name}/", "").strip()
        self.s3.delete_object(Bucket=self.bucket_name, Key=file_path)
