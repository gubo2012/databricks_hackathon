import logging
import boto3


# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Set up AWS clients
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "wukong-hackathon"  # Replace with your actual S3 bucket name


# Initialize AWS clients
def setup_aws_clients():
    try:
        return {
            'polly': boto3.client('polly', region_name=AWS_REGION),
            'transcribe': boto3.client('transcribe', region_name=AWS_REGION),
            's3': boto3.client('s3', region_name=AWS_REGION),
            'translate': boto3.client('translate', region_name=AWS_REGION)
        }
    except Exception as e:
        logger.error(f"Error setting up AWS clients: {e}")
        return None


# Function to translate text using AWS Translate
def translate_text_func(aws_clients, text, source_lang='auto', target_lang='en'):
    try:
        result = aws_clients['translate'].translate_text(Text=text, SourceLanguageCode=source_lang, TargetLanguageCode=target_lang)
        translated_text = result.get('TranslatedText')
        logger.info(f"Translated Text: {translated_text}")
        return translated_text
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return None