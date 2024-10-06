import os
from aws_func import S3_BUCKET_NAME, setup_aws_clients, translate_text_func


def test_translate_text_func(aws_clients):
    text_org = '胫骨平台骨折是指胫骨（小腿的骨头）上部涉及膝关节的骨折。'
    text_translated = translate_text_func(aws_clients, text_org)

    print('Original Text:', text_org)
    print('Translated Text:', text_translated)



if __name__ == "__main__":
    aws_clients = setup_aws_clients()

    test_translate_text_func(aws_clients)

 