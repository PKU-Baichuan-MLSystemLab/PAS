import argparse
import pandas as pd
import json
import random

import pandas as pd
import requests
from requests.adapters import HTTPAdapter, Retry
import json
import os

from tqdm.contrib.concurrent import process_map

openai_key = os.environ.get('OPENAI_API_KEY')
openai_api = os.environ.get('OPENAI_API_ADDR')

retry_strategy = Retry(
    total=5,  # 最大重试次数（包括首次请求）
    backoff_factor=1,  # 重试之间的等待时间因子
    status_forcelist=[404, 429, 500, 502, 503, 504],  # 需要重试的状态码列表
    allowed_methods=["POST"]  # 只对POST请求进行重试
)

adapter = HTTPAdapter(
    # max_retries=retry_strategy,
    pool_maxsize=50, )
# 创建会话并添加重试逻辑
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)


def openai_chat(messages, model='gpt-4-turbo-2024-04-09', **kwargs):
    if isinstance(messages, str):
        messages = [{'role': 'user', 'content': messages}]

    headers = {'Content-Type': 'application/json'}
    headers['Authorization'] = f'Bearer {openai_key}'
    # import pdb;pdb.set_trace()
    for _ in range(10):
        try:
            response = session.post(openai_api + '/v1/chat/completions',
                                    headers=headers,
                                    timeout=5,
                                    data=json.dumps(
                                        dict(model=model,
                                             messages=messages,
                                             **kwargs)))
            if response.status_code != 200:
                print(response.status_code, response.text)
            assert response.status_code == 200
            response = json.loads(response.text)

            return response['choices'][0]['message']['content']
        except Exception as e:
            print(e)
            import time
            time.sleep(5)
    print('max tries')
    return ''


def get_turns(messages):
    return len(messages) / 2


def message2prompt(message):
    return message[0]['content']


def get_ape(data):
    prompt = data['prompt']
    task = data['能力']

    task_pe = json.load(open('task_pe.json'))
    pe = task_pe[task]

    inputs = pe.replace('PROMPT_PLACEHOLDER', prompt)

    ape = openai_chat(inputs)

    return {'prompt': prompt, 'ape': ape, '能力': task}


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str)
    parser.add_argument("--output-file", type=str)
    args = parser.parse_args()

    task_pe = json.load(open('task_pe.json'))

    df = pd.read_json(args.input_file, lines=True)
    df['turns'] = df['messages'].map(get_turns)

    df = df[df['turns'] == 1]

    df['prompt'] = df['messages'].map(message2prompt)
    df.drop('messages', axis=1, inplace=True)
    df_new = df[['prompt', 'task']]

    prompts = []
    for task in task_pe.keys():
        prompts += df_new[df_new['task'] == task].to_dict('records')

    apes = []

    apes = process_map(get_ape, prompts, max_workers=20)

    with open(args.output_file, 'a') as f:
        for ape in apes:
            f.write(json.dumps(ape, ensure_ascii=False))
            f.write('\n')
