import openai
import pandas as pd
import tiktoken
import requests

def estimate_token_count(text, model):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


class SrtSummarizer:
    def __init__(self, api_key, prompt, proxies, model='gpt-3.5-turbo', max_token_count=4000, ):
        openai.api_key = api_key
        self.prompt = prompt
        self.max_token_count = max_token_count
        self.model = model

        session = requests.Session()
        session.proxies.update(proxies)
        openai.api_session = session

    def srt_segmentation(self, srt):
        ## srt to segmentation
        token_count = self.max_token_count / 1.3   ## using 1.3 to
        tmp = 0
        tmp_str = ''
        result = []
        for index, row in srt.iterrows():

            tmp = tmp + estimate_token_count(row['text'], self.model)
            tmp_str = tmp_str + ',' + row['text']
            if tmp > token_count:
                result.append([tmp, tmp_str])
                tmp_str = ''
                tmp = 0
        
        result.append([tmp, tmp_str])  ## last segment

        return result

    def summarize(self, srt):
        segments = self.srt_segmentation(srt)
        responses = []
        for item in segments:
            res = self.get_responce(item[1], item[0] * 0.2)
            responses.append(res)
        if  len(responses)>1:
            return self.merge_responses(responses)
        elif len(responses)==1:
            return responses[0]
        else:
            return 

    def merge_responses(self, responses):
        tmp_str = '.'.join(responses)
        token_count = estimate_token_count(tmp_str, self.model)
        if token_count > self.max_token_count / 2:
            print('warning, the responses needed to merge are too long!', 'token_acount=', token_count)
            print('return simple merge of response from all segments')
            return '\n'.join(responses)
        else:
            res = self.get_responce(tmp_str, token_count)
            return res

    def get_responce(self, text, max_tokens, temperature=0.6):
        max_tokens = int(max_tokens)
        payload = {
            'messages': [{"role": "system", "content": self.prompt},
                         {"role": "user", "content": text}],
            'max_tokens': max_tokens,
            'temperature': temperature,
            'model': self.model,
        }
        response = openai.ChatCompletion.create(**payload)

        # 提取助手的回答
        assistant_reply = response['choices'][0]['message']['content']

        return assistant_reply


if __name__ == "__main__": 
    ### usage examples

    srt=pd.read_csv('demo.csv')
    api_key = 'your-openai-key'
    prompt = 'extract key takeaways the transcript, answer in zh-Hans'
    model = 'gpt-3.5-turbo'
    max_token_count = 4000
    srt_summarize = SrtSummarizer(api_key, prompt, model, max_token_count)

    result=srt_summarize.summarize(srt)
    print(result)
