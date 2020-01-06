import os
import librosa
#import matplotlib.pyplot as plt
import librosa.display
import numpy as np
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from tqdm import tqdm


DATA_PATH = "./all/train/train/audio/"

def get_labels(path=DATA_PATH):
    labels = os.listdir(path)
    label_indices = np.arange(0,len(labels))
    return labels, label_indices, to_categorical(label_indices)

def wav2mfcc(file_path,max_len=11):
    wave,sr = librosa.load(file_path,mono=True,sr=None)
    wave = wave[::3]
    mfcc = librosa.feature.mfcc(wave,sr=16000)
    
    if(max_len > mfcc.shape[1]):
        pad_width = max_len - mfcc.shape[1]
        mfcc = np.pad(mfcc,pad_width=((0,0),(0,pad_width)),mode='constant')
       
    else:
        mfcc[:, :max_len]
        
    return mfcc

def save_data_to_array(path=DATA_PATH, max_len=11):
    labels, _, _ = get_labels(path)
    
    for label in labels:
        mfcc_vectors = []
        wavfiles = [path + label + '/' + wavfile for wavfile in os.listdir(path + '/' + label)]
        for wavfile in tqdm(wavfiles, "Saving vectors of label - '{}'".format(label)):
            mfcc = wav2mfcc(wavfile,max_len = max_len)
            mfcc_vectors.append(mfcc)
        np.save(label + '.npy' , mfcc_vectors)
            
            
def get_train_test(spilt_ratio=0.6,random_state=42):
    labels , indices, _ = get_labels(DATA_PATH)
    
    X = np.load(labels[0] + '.npy')
    y = np.zeros(X.shape[0])
    
    for i, label in enumerate(labels[1:]):
        x = np.load(label + '.npy')
        X = np.vstack((X,x))
        y = np.append(y, np.full(x.shape[0],fill_value = (i+1)))
    
    assert X.shape[0] == len(y)
    
    return train_test_split(X,y,test_size=(1 - spilt_ratio) , random_state = random_state , shuffle =True)


def prepare_dataset(path=DATA_PATH):
    labels, _, _ = get_labels(path)
    data = {}
    for label in labels:
        data[label] = {}
        data[label]['path'] = [path  + label + '/' + wavfile for wavfile in os.listdir(path + '/' + label)]

        vectors = []

        for wavfile in data[label]['path']:
            wave, sr = librosa.load(wavfile, mono=True, sr=None)
            # Downsampling
            wave = wave[::3]
            mfcc = librosa.feature.mfcc(wave, sr=16000)
            vectors.append(mfcc)

        data[label]['mfcc'] = vectors

    return data


def load_dataset(path=DATA_PATH):
    data = prepare_dataset(path)

    dataset = []

    for key in data:
        for mfcc in data[key]['mfcc']:
            dataset.append((key, mfcc))

    return dataset[:100]