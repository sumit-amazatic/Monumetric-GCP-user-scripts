## in this script we are deleting OLD backups from gcp bucket
import os
from google.cloud import storage
from datetime import datetime, timedelta
from pytz import timezone
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.dirname(os.path.realpath(__file__)) + "/console-234301-5a1f42a57128.json"

def delete_file_from_bucket(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
    print('Blob {} deleted.'.format(blob_name))

def is_delete(date_obj):
    utc_date_obj = (date_obj).replace(tzinfo=timezone('UTC'))
    utc_file_date = (date_obj).replace(tzinfo=timezone('UTC'))
    now = (datetime.now()).replace(tzinfo=timezone('UTC'))

    weekly_backup_days = [1, 7, 14, 21, 28]

    def check_year():
        return (now - timedelta(days=365)) > utc_date_obj

    def check_seven_to_twelve_months():
        if (now - timedelta(days=181)) > utc_file_date:
            return utc_file_date.day != 14
        return False

    def check_one_to_six():
        if ((now - timedelta(days=31)) > utc_file_date) and ((now - timedelta(days=181)) < utc_file_date):
            return utc_file_date.day not in weekly_backup_days
        return False

    return (check_year() or check_seven_to_twelve_months() or check_one_to_six())


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        if is_delete((blob.updated).replace(tzinfo=timezone('UTC'))):
            ## Be careful bellow line this may delete entire bucket
            delete_file_from_bucket(bucket_name, (blob.name).encode("utf-8"))
            print("fileName:- ", blob.name, " Deleted")

buckets_list = ["tier-master-bucket", "stats-master-bucket", "aggregator-production-master-ssd-bucket", "aggregator-production-master-bucket"]

for bucket_name in buckets_list:
    try:
    	list_blobs(bucket_name)
    except Exception:
     	print("Bucket not found:- "+ bucket_name)
