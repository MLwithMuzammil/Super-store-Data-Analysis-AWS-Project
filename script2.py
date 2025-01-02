import pandas as pd
import boto3
from datetime import datetime as dt
import os
from io import StringIO

def process_and_upload_csv(
    input_csv_path: str,
    bucket_name: str,
    date_column: str,
    s3_prefix: str = "orders/snapshot_day=2017-04-152014-05-13"
) -> None:
    """
    Process CSV file and upload filtered data to S3 in partitioned folders.
    
    Args:
        input_csv_path (str): Path to input CSV file
        bucket_name (str): S3 bucket name
        date_column (str): Name of the date column in CSV
        s3_prefix (str): Prefix for S3 folders
    """
    try:
        # Initialize S3 client (Use env variables or AWS profile)
        s3_client = boto3.client('s3',
        aws_access_key_id='',
        aws_secret_access_key='',
        region_name='eu-north-1'
)

        # Read CSV file
        print(f"Reading CSV file: {input_csv_path}")
        df = pd.read_csv(input_csv_path, encoding='ISO-8859-1')
        
        # Convert date column to datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        
        # Drop rows with invalid dates
        df.dropna(subset=[date_column], inplace=True)
        
        # Get unique dates
        unique_dates = df[date_column].dt.date.unique()
        
        # Process each date
        for date in unique_dates:
            # Filter data for current date
            date_str = date.strftime('%Y-%m-%d')
            daily_data = df[df[date_column].dt.date == date]
            
            # Create partition folder name (ensure trailing slash)
            partition_folder = f"{s3_prefix}{date_str}/"
            
            # Convert filtered DataFrame to CSV string
            csv_buffer = StringIO()
            daily_data.to_csv(csv_buffer, index=False)
            
            # Define S3 key
            s3_key = f"{partition_folder}data.csv"
            
            # Upload to S3
            print(f"Uploading data for date {date_str} to S3...")
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=csv_buffer.getvalue()
            )
            print(f"Successfully uploaded to s3://{bucket_name}/{s3_key}")
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise

def main():
    # Configuration
    input_csv_path = "SampleSuperstore.csv"
    bucket_name = "stock-price-1"
    date_column = "Order Date"
    
    # Process and upload
    process_and_upload_csv(
        input_csv_path=input_csv_path,
        bucket_name=bucket_name,
        date_column=date_column
    )

if __name__ == "__main__":
    main()