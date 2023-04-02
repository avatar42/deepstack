import os
os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.3/bin")
os.add_dll_directory("C:/cuda/bin")

import tensorflow as tf
# import utils

raw_dataset = tf.data.TFRecordDataset("../deepstack-trainer/train-runs/deepstack/RMRR/events.out.tfevents.1643746547.ThorW.7584.0")

print(raw_dataset)
print("Debug=" + raw_dataset.__debug_string__())


for raw_record in raw_dataset.take(10):
    example = tf.train.Example()
    example.ParseFromString(raw_record.numpy())
    print(example)
