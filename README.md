# PAS: Data-Efficient Plug-and-Play Prompt Augmentation System

## Abstract

In recent years, the rise of Large Language Models (LLMs) has spurred a growing demand for plug-and-play AI systems. Among the various AI techniques, prompt engineering stands out as particularly significant. However, users often face challenges in writing prompts due to the steep learning curve and significant time investment, and existing automatic prompt engineering (APE) models can be difficult to use. To address this issue, we propose PAS, an LLM-based plug-and-play APE system.
PAS utilizes LLMs trained on high-quality, automatically generated prompt complementary datasets, resulting in exceptional performance. In comprehensive benchmarks, PAS achieves state-of-the-art (SoTA) results compared to previous APE models, with an average improvement of 6.09 points. Moreover, PAS is highly efficient, achieving SoTA performance with only 9000 data points. Additionally, PAS can autonomously generate prompt augmentation data without requiring additional human labor. Its flexibility also allows it to be compatible with all existing LLMs and applicable to a wide range of tasks.
PAS excels in human evaluations, underscoring its suitability as a plug-in for users. This combination of high performance, efficiency, and flexibility makes PAS a valuable system for enhancing the usability and effectiveness of LLMs through improved prompt engineering.

## Table of Contents

- [PAS: Data-Efficient Plug-and-Play Prompt Augmentation System](#pas-data-efficient-plug-and-play-prompt-augmentation-system)
  - [Abstract](#abstract)
  - [Table of Contents](#table-of-contents)
  - [Model](#model)
  - [Data](#data)
    - [PAS Dataset](#pas-dataset)
    - [PAS data generation](#pas-data-generation)
      - [instructions](#instructions)

## Model

Model details:

- Params: 7B
- Context length: 4096
- Epoch: 2
- Learning rate: 2e-5

The model to generating prompt complementary is coming soon, stay tuned!

We have released training dataset in [trainml_ape](data/trainml_ape.jsonl), and advise you to use the training framework, [Llama-Factory](https://github.com/hiyouga/LLaMA-Factory) to finetune your own PAS model.

## Data

### PAS Dataset

We have released training dataset in [trainml_ape](data/trainml_ape.jsonl). The data format is:

```json
{
    "prompt": {prompt},
    "ape": {ape},
    "result": {critique_reasult},
    "messages": {message}
}
```

- prompt: original prompt from open-source datasets.
- ape: initially generated complementary prompt data.
- result: the result after regeneration process.
- messages: training data with messages format for OpenAI chat completion task.

### PAS data generation

This project involves generating and refining complementary prompt data for PAS data generation. The key components of the project are as follows:

- data/ape_seed.jsonl: Contains the seed data for different categories.
- data/task_pe.jsonl: Holds the prompt data for different categories.
- script/ape_data_gen.py: A script for generating complementary prompt data.
- script/make_train_data.py: Converts the generated data into a format suitable for training LLMs.
- script/ape_critique.py: A script for selecting and regenerating complementary prompt data.

#### instructions

1. Seed Data: Start with ape_seed.jsonl, which contains the initial seed data categorized by different classes.
2. Prompt Data: Use task_pe.jsonl to access the categorized prompt data.
3. Data Generation: Run ape_data_gen.py to generate complementary prompt data based on the seed and prompt data.
4. Data Conversion: Use make_train_data.py to convert the generated data into the appropriate format for LLM training.
5. Data Selection & Regeneration: Execute ape_critique.py to select and regenerate high-quality complementary prompt data, ensuring optimal data for training purposes.

## Citation

If you find PAS useful for your research and applications, please cite using this BibTeX:
```bibtex
@article{zheng2024pas,
  title={PAS: Data-Efficient Plug-and-Play Prompt Augmentation System},
  author={Zheng, Miao and Liang, Hao and Yang, Fan and Sun, Haoze and Li, Tianpeng and Xiong, Lingchu and Zhang, Yan and Wu, Yozhen and Li, Kun and Sheng, Yanjun and others},
  journal={arXiv preprint arXiv:2407.06027},
  year={2024}
}
```