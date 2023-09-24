import torch
from faster_whisper import WhisperModel
import pandas as pd

class audio2text:
    def __init__(self, model='large-v2', gpu_index=0):
        device = torch.device("cuda:"+str(gpu_index))
        self.model = WhisperModel(model, device='cuda', device_index= gpu_index, compute_type="float16")
        #self.model.to(device)
    def process(self, path):
        result=[]
        segments, info = self.model.transcribe(path, beam_size=5)
        for index, item in enumerate(segments):
            tmp = pd.DataFrame({'start': [item.start], 'duration': [item.end-item.start], 'text': [item.text]}, index=[index])
            result.append(tmp)
        return pd.concat(result, axis=0)
    
