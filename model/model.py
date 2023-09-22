import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.models import load_model as tf_load_model
from tqdm import tqdm

class YouTubeTitleGenerator:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.embedding_dim = 256
        self.rnn_units = 1024
        self.model = None

    def preprocess_data(self, titles):
        self.tokenizer.fit_on_texts(titles)
        total_words = len(self.tokenizer.word_index) + 1

        # Convert list of titles into sequences of tokens
        input_sequences = []
        for line in titles:
            token_list = self.tokenizer.texts_to_sequences([line])[0]
            for i in range(1, len(token_list)):
                n_gram_sequence = token_list[:i+1]
                input_sequences.append(n_gram_sequence)

        # Pad sequences and create predictors and label
        max_sequence_len = max([len(x) for x in input_sequences])
        input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))
        
        predictors, label = input_sequences[:,:-1], input_sequences[:,-1]
        label = tf.keras.utils.to_categorical(label, num_classes=total_words)

        return predictors, label, max_sequence_len, total_words

    def build_model(self, total_words):
        model = Sequential()
        model.add(Embedding(input_dim=total_words, output_dim=self.embedding_dim))
        model.add(LSTM(self.rnn_units))
        model.add(Dense(total_words, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.model = model
        
    def generate_batches(self, titles, batch_size=10000):
        n = len(titles)
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(titles)
        total_words = len(tokenizer.word_index) + 1

        for i in range(0, n, batch_size):
            end = min(i + batch_size, n)
            input_sequences = []
            for line in titles[i:end]:
                token_list = tokenizer.texts_to_sequences([line])[0]
                for i in range(1, len(token_list)):
                    n_gram_sequence = token_list[:i + 1]
                    input_sequences.append(n_gram_sequence)

            max_sequence_len = max([len(x) for x in input_sequences])
            input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len-1, padding='pre'))
            
            predictors, label = input_sequences[:, :-1], input_sequences[:, -1]
            label = tf.keras.utils.to_categorical(label, num_classes=total_words)
            
            yield predictors, label, max_sequence_len, total_words

    def train(self, titles, batch_size=10000):
        if not self.model:
            _, _, _, total_words = next(self.generate_batches(titles, batch_size=batch_size))
            self.build_model(total_words)
        for predictors, label, max_sequence_len, total_words in self.generate_batches(titles, batch_size=batch_size):
            self.model.fit(predictors, label, epochs=100, verbose=1)


    def generate_title(self, prompt, max_sequence_len, total_words, num_words=10):
        for _ in range(num_words):
            token_list = self.tokenizer.texts_to_sequences([prompt])[0]
            token_list = pad_sequences([token_list], maxlen=max_sequence_len-2, padding='pre')
            predicted = np.argmax(self.model.predict(token_list), axis=-1)
            output_word = ""
            for word, index in self.tokenizer.word_index.items():
                if index == predicted:
                    output_word = word
                    break
            prompt += " " + output_word
        return prompt

    def save_model(self, filepath):
        self.model.save(filepath)

    def load_model(self, filepath, titles):
        _, _, max_sequence_len, total_words = self.preprocess_data(titles)
        self.model = tf_load_model(filepath)
        return max_sequence_len, total_words

if __name__ == "__main__":
    generator = YouTubeTitleGenerator()
    with open("../scraped_titles.txt", 'r', encoding='utf-8') as file:
        titles = file.readlines()
    generator.train(titles)
    generator.save_model("youtube_title_generator_model.h5")
