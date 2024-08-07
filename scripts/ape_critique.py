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

critique_tmp = '''## Background

High-quality prompt engineering can significantly improve the application potential and answer quality of ChatGPT. 
It is known that there is a technology called automatic prompt engineering technology, which automatically supplements the user's fuzzy input in one or more aspects such as style, format, and content.
As an expert proficient in ChatGPT Prompt Engineering, your task is to diagnose whether the automatic prompt word (APE) is a valid supplement to the user input (Prompt) and provide an analysis.
Generally speaking, the correct APE can prompt or guide the depth, standardization, and win rate of ChatGPT's answer content, thereby improving the level and professionalism of ChatGPT's answer. 
The wrong APE can easily deviate from the user's true intention, causing the results to deviate from the requirements; or when prompt has given the answer constraints, it may add contradictory constraints or excessively extended additional requirements, causing ChatGPT to easily reduce the user Prompt by focusing on the content of the APE.

## Workflow

Please analyze and judge the APE and, then modify the incorrect APE. Here are 3 steps for this task, you must do it step by step:
1. Analyze APE based on the APE standards
2. Determine whether APE is correct.
3. If the APE is wrong, please modify APE as final APE, otherwise copy origin APE as final APE.

The criteria for incorrect APE are:
1. APE deviates from the true intention of Prompt and conflicts with Prompt
2. APE provides too much superfluous additions to complex Prompt.
3. APE directly answers Prompt instead of supplementing Prompt.
4. APE makes excessive demands on Prompt.
5. The language of ape is consistent with that of user prompt.

### Cases of APE diagnosis

Here I list examples for APE diagnosis. Please remind that these examples are incomplete.

#### Case1

<Prompt>:
鲁迅和周树人是什么关系

<APE>:
请简要介绍鲁迅（本名周树人）的生平和文学贡献，用Markdown格式列出。

<Output>:
{{
    "Reason": "Prompt问题和APE内容不相关，APE内容偏移Prompt意图。",
    "Is_correct": "No",
    "FinalAPE": "请简要介绍鲁迅和周树人的关系。"
}}

#### Case2

<Prompt>:
脑科学是什么

<APE>:
可以先简要介绍脑科学定义，然后列出它的研究领域和应用实例，可适当引用权威资料，注意输出内容结构清晰，容易理解。

<Output>:
{{
    "Reason": "APE准确描述了科普回答的一般回答范式，能够提升回答的丰富性和专业度。",
    "Is_correct": "Yes",
    "FinalAPE": "可以先简要介绍脑科学定义，然后列出它的研究领域和应用实例，可适当引用权威资料，注意输出内容结构清晰，容易理解。"
}}

#### Case3

<Prompt>:
每次家长和孩子发生冲突，事后孩子都不会主动思考，为什么和家长发生冲突，自己哪里错了，有想法应该如何与大人沟通或抗争？没有反思、复盘，类似冲突频发，自己也没成长，怎么办？

<APE>:
在撰写解决策略时，应考虑辅导孩子如何进行自我反省，学习有效沟通技巧，并理解不同观点。同时，需要提醒家长也需学习理解和尊重孩子的想法。

<Output>:
{{
    "Reason": "APE提供了Prompt问题的回复思路，并且看到了Promp问题中家长的不足，使得回复水平更好、角度更全面。",
    "Is_correct": "Yes",
    "FinalAPE": "在撰写解决策略时，应考虑辅导孩子如何进行自我反省，学习有效沟通技巧，并理解不同观点。同时，需要提醒家长也需学习理解和尊重孩子的想法。"
}}

#### Case4

<Prompt>:
What is technological singularity and intelligence explosion?

<APE>:
请分析和介绍技术奇点和智能爆炸的定义及其影响，以确保回复内容具有逻辑性、条理性，并便于用户理解。

<Output>:
{{
    "Reason": "The content of the APE isn't consistent with the language of the user's prompt",
    "Is_correct": "No",
    "FinalAPE": "Please analyze and introduce the definitions and impacts of technological singularity and intelligence explosion to ensure that your response is logical, organized, and easy for users to understand."
}}


## Output format

The output is required to be in json format: {{"Reason": str, "Is_correct": str,  "Final APE": str}}. The language of analysis needs to be consistent with the prompt, and the "Is_correct" can only be "Yes" or "No".

## Task

According to the above requirements, complete the following task

<Prompt>:
{prompt}

<APE>:
{ape}

<Output>:
'''

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
                                    timeout=10,
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


def get_critique(data):
    prompt = data['prompt']
    ape = data['ape']

    critique_inputs = critique_tmp.format(prompt=prompt, ape=ape)
    for _ in range(5):
        response = openai_chat(critique_inputs)
        response = response.strip('` \n')
        if response.startswith('json'):
            response = response[4:]
        response = response.strip('` \n')
        try:
            result = json.loads(response.strip())
            break
        except:
            result = None
            pass
    return {'prompt': prompt, 'ape': ape, 'result': result}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str)
    parser.add_argument("--output-file", type=str)
    args = parser.parse_args()

    df = pd.read_json(args.input_file, lines=True)
    prompts = df.to_dict('records')

    critiques = process_map(get_critique, prompts)

    with open(args.output_file, 'a') as f:
        for critique in critiques:
            f.write(json.dumps(critique, ensure_ascii=False))
            f.write('\n')
