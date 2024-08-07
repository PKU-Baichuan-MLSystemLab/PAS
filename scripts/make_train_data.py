import argparse
import json
import os
from copy import deepcopy

user_input_tmp = '''## Background

You are an expert in enhancing user prompts, proficient in providing detailed supplements. When identifying areas in user prompts needing further elaboration, you offer precise additions to help the user understand the core intent of their question more deeply. Focus on providing general methods and strategies, not specific details.
Note: Only supplement user prompts, do not directly answer them; keep supplementary content to around 30 words, and try not to exceed 30 words.

## Task

<User prompt>:
{prompt}
<Complementary information>:
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str)
    parser.add_argument("--output-file", type=str)
    args = parser.parse_args()

    with open(args.input_file) as f:
        with open(args.output_file, 'w') as fw:
            for line in f.readlines():
                data = json.loads(line)
                new_data = deepcopy(data)
                prompt = data['prompt']
                ape = data['ape']
                if data.get('result'):
                    if data['result']['Is_correct'] == 'No':
                        ape = data['result']['FinalAPE']

                user_input = user_input_tmp.format(prompt=prompt)
                new_data['messages'] = [{
                    'role': 'user',
                    'content': user_input
                }, {
                    'role': 'assistant',
                    'content': ape
                }]
                fw.write(json.dumps(new_data, ensure_ascii=False))
                fw.write('\n')
