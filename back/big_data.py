import os
import datetime
import boto3
import logging
from typing import Dict


class AwsInstance(boto3.Session):
    """
    AWS Session instance with methods for interacting with S3.

    This class extends boto3.Session and provides methods for creating an S3 bucket,
    pushing data to S3, and handling late data pushing.
    """

    def __init__(self):
        access = os.getenv("AWS_ACCESS_ID")
        key = os.getenv("AWS_ACCESS_KEY")
        self.bucket_name = os.getenv("AWS_BUCKET")
        super().__init__(aws_access_key_id=access, aws_secret_access_key=key)
        self.s3 = self.resource("s3")
        self.create_bucket()

    def create_bucket(self) -> None:
        """
        Pushes a file to an Amazon S3 bucket after appending the current date to its name.\n
        Args:
            filepath (str): The local filepath of the file to be pushed to S3.
        """
        try:
            self.s3.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={"LocationConstraint": "eu-west-3"},
            )
        except Exception:
            logging.info(f"Bucket {self.bucket_name} exist")

    def push_to_s3(self, filepath: str) -> None:
        """
        Uploads a file to an AWS S3 bucket and logs the upload.\n
        Args:
            filepath (str): The local filepath of the file to be uploaded.
        """
        bucket = self.s3.Bucket(self.bucket_name)
        # get name for s3
        uploaded_file = filepath.split(".")
        date = datetime.date.today().strftime("%Y-%m-%d")
        uploaded_file[0] = uploaded_file[0] + "_" + date
        uploaded_file = ".".join(uploaded_file)
        # push zipped file to s3
        try:
            bucket.upload_file(filepath, uploaded_file)
            with open("s3_files.log", "a", encoding="UTF-8") as file:
                file.write(uploaded_file)
                file.write("\n")
        except Exception as e:
            print(e)

    def load_from_s3(self, last_uploaded: str, directory: str) -> None:
        """
        Downloads a file from an Amazon S3 bucket to a local directory.\n
        Args:
            last_uploaded (str): The name of the file to be downloaded from S3.
            directory (str): The local directory where the file will be saved.
        """
        bucket = self.s3.Bucket(self.bucket_name)
        dir_ = os.path.join("data", directory)
        local_filepath = os.path.join(dir_, last_uploaded)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
            print(f"Directory '{dir_}' created.")
        bucket.download_file(last_uploaded, local_filepath)
