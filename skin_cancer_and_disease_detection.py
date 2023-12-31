
"""
Skin cancer lesion classification using the HAM10000 dataset
Dataset link:
https://www.kaggle.com/kmader/skin-cancer-mnist-ham10000
Data description: 
https://arxiv.org/ftp/arxiv/papers/1803/1803.10417.pdf
The 7 classes of skin cancer lesions included in this dataset are:
Melanocytic nevi (nv)
Melanoma (mel)
Benign keratosis-like lesions (bkl)
Basal cell carcinoma (bcc) 
Actinic keratoses (akiec)
Vascular lesions (vas)
Dermatofibroma (df)
"""


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import seaborn as sns
from PIL import Image
np.random.seed(42)
import keras
from keras.utils.np_utils import to_categorical # used for converting labels to one-hot-encoding
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D, BatchNormalization
from sklearn.model_selection import train_test_split
from scipy import stats
from sklearn.preprocessing import LabelEncoder
import matplotlib.cm
import tensorflow as tf

skin_df = pd.read_csv("C:/Users/Muhammed Rasmil/Desktop/project dataset/HAM10000_metadata.csv")

SIZE=32

# label encoding to numeric values from text
le = LabelEncoder()
le.fit(skin_df['dx'])
LabelEncoder()
print(list(le.classes_))
 
skin_df['label'] = le.transform(skin_df["dx"]) 
print(skin_df.sample(10))


# Data distribution visualization
fig = plt.figure(figsize=(12,8))

ax1 = fig.add_subplot(221)
skin_df['dx'].value_counts().plot(kind='bar', ax=ax1)
ax1.set_ylabel('Count')
ax1.set_title('Cell Type');

ax2 = fig.add_subplot(222)
skin_df['sex'].value_counts().plot(kind='bar', ax=ax2)
ax2.set_ylabel('Count', size=15)
ax2.set_title('Sex');

ax3 = fig.add_subplot(223)
skin_df['localization'].value_counts().plot(kind='bar')
ax3.set_ylabel('Count',size=12)
ax3.set_title('Localization')


plt.tight_layout()
plt.show()


# Distribution of data into various classes 
from sklearn.utils import resample
print(skin_df['dx'].value_counts())

#Balance data.
# Many ways to balance data... you can also try assigning weights during model.fit
#Separate each classes, resample, and combine back into single dataframe

df_0 = skin_df[skin_df['label'] == 0]
df_1 = skin_df[skin_df['label'] == 1]
df_2 = skin_df[skin_df['label'] == 2]
df_3 = skin_df[skin_df['label'] == 3]
df_4 = skin_df[skin_df['label'] == 4]
df_5 = skin_df[skin_df['label'] == 5]
df_6 = skin_df[skin_df['label'] == 6]

n_samples=500 
df_0_balanced = resample(df_0, replace=True, n_samples=n_samples, random_state=42) 
df_1_balanced = resample(df_1, replace=True, n_samples=n_samples, random_state=42) 
df_2_balanced = resample(df_2, replace=True, n_samples=n_samples, random_state=42)
df_3_balanced = resample(df_3, replace=True, n_samples=n_samples, random_state=42)
df_4_balanced = resample(df_4, replace=True, n_samples=n_samples, random_state=42)
df_5_balanced = resample(df_5, replace=True, n_samples=n_samples, random_state=42)
df_6_balanced = resample(df_6, replace=True, n_samples=n_samples, random_state=42)

#Combined back to a single dataframe
skin_df_balanced = pd.concat([df_0_balanced, df_1_balanced, 
                              df_2_balanced, df_3_balanced, 
                              df_4_balanced, df_5_balanced, df_6_balanced])

#Check the distribution. All classes should be balanced now.
print(skin_df_balanced['dx'].value_counts())



img_dir="C:/Users/Muhammed Rasmil/Desktop/project dataset/All Images/"
image_path = {}

for filename in os.listdir(img_dir):
    temp={os.path.splitext(filename)[0]:os.path.join(img_dir,filename)}
    image_path |= temp



#Define the path and add as a new column
skin_df_balanced['path'] = skin_df['image_id'].map(image_path.get)
#Use the path to read images.

skin_df_balanced['image'] = skin_df_balanced['path'].map(lambda x: np.asarray(Image.open(x).resize((SIZE,SIZE))))


#visualization
n_samples = 5  # number of samples for plotting
# Plotting
fig, m_axs = plt.subplots(7, n_samples, figsize = (4*n_samples, 3*7))
for n_axs, (type_name, type_rows) in zip(m_axs, 
                                         skin_df_balanced.sort_values(['dx']).groupby('dx')):
    n_axs[0].set_title(type_name)
    for c_ax, (_, c_row) in zip(n_axs, type_rows.sample(n_samples, random_state=1234).iterrows()):
        c_ax.imshow(c_row['image'],cmap=matplotlib.cm.Greys_r)
        c_ax.axis('off')

#Convert dataframe column of images into numpy array
X = np.asarray(skin_df_balanced['image'].tolist())
print(X.shape)
X = X/255
print(X.shape)  # Scale values to 0-1. You can also used standardscaler or other scaling methods.
Y=skin_df_balanced['label']  #Assign label values to Y
Y_cat = to_categorical(Y, num_classes=7) #Convert to categorical as this is a multiclass classification problem
#Split to training and testing
x_train, x_test, y_train, y_test = train_test_split(X, Y_cat, test_size=0.25, random_state=42)


#cnn

num_classes = 7
cnn = Sequential()
cnn.add(Conv2D(512, (3, 3), activation="relu", input_shape=(SIZE,SIZE,3)))
cnn.add(BatchNormalization())
cnn.add(MaxPool2D(pool_size=(2, 2)))  
cnn.add(Dropout(0.3))

cnn.add(Conv2D(256, (3, 3),activation='relu'))
cnn.add(BatchNormalization())
cnn.add(MaxPool2D(pool_size=(2, 2)))  
cnn.add(Dropout(0.3))

cnn.add(Conv2D(128, (3, 3),activation='relu'))
cnn.add(BatchNormalization())
cnn.add(MaxPool2D(pool_size=(2, 2)))  
cnn.add(Dropout(0.3))
cnn.add(Flatten())

cnn.add(Dense(64))
cnn.add(Dense(7,
activation='softmax',
kernel_regularizer=keras.regularizers.l1_l2(l1=0.01,l2=0.01)))
 
cnn.summary() 

cnn.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['acc'])

# Train


batch_size = 16
epochs = 60

history = cnn.fit(
    x_train, y_train,
    epochs=epochs,
    batch_size = batch_size,
    validation_data=(x_test, y_test),
    verbose=2)

scoreCnn = cnn.evaluate(x_test, y_test)
print('Test accuracy:', scoreCnn[1])


#ann code

num_classes = 7
ann = Sequential()
ann.add(Flatten(input_shape=(SIZE,SIZE,3)))
ann.add(Dense(512, activation="relu"))
ann.add(BatchNormalization())
ann.add(Dropout(0.3))

ann.add(Dense(256, activation='relu'))
ann.add(BatchNormalization())
ann.add(Dropout(0.3))

ann.add(Dense(128, activation='relu'))
ann.add(BatchNormalization())
ann.add(Dropout(0.3))

ann.add(Dense(64))
ann.add(Dense(num_classes,
activation='softmax',
kernel_regularizer=keras.regularizers.l1_l2(l1=0.01,l2=0.01)))

ann.summary()

ann.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['acc'])


batch_size = 16
epochs = 60

history = ann.fit(
    x_train, y_train,
    epochs=epochs,
    batch_size = batch_size,
    validation_data=(x_test, y_test),
    verbose=2)

scoreAnn = ann.evaluate(x_test, y_test)
print('Test accuracy:', scoreAnn[1])


#fnn ---------------------------------------------------------

num_classes = 7
fnn = Sequential()
fnn.add(Flatten(input_shape=(SIZE, SIZE, 3)))
fnn.add(Dense(512, activation="relu"))
fnn.add(BatchNormalization())
fnn.add(Dropout(0.3))

fnn.add(Dense(256, activation="relu"))
fnn.add(BatchNormalization())
fnn.add(Dropout(0.3))

fnn.add(Dense(128, activation="relu"))
fnn.add(BatchNormalization())
fnn.add(Dropout(0.3))

fnn.add(Dense(64, activation="relu"))
fnn.add(Dense(num_classes, activation="softmax", kernel_regularizer=keras.regularizers.l1_l2(l1=0.01, l2=0.01)))

fnn.summary()

fnn.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['acc'])

# Train
batch_size = 16
epochs = 60

history = fnn.fit(
    x_train, y_train,
    epochs=epochs,
    batch_size=batch_size,
    validation_data=(x_test, y_test),
    verbose=2)

scoreFNN = fnn.evaluate(x_test, y_test)
print('Test accuracy:', scoreFNN[1])


#----------------------------------------------------------------------------------


meth=["CNN","ANN","FNN"]
accRes=[scoreCnn[1] * 100,scoreAnn[1] * 100,scoreFNN[1] * 100]
plt.bar(meth,accRes)
plt.ylabel("Accuracy")
plt.title("Accuracy Comparison")
plt.show()



#Save the model

cnn.save("my_model.h5", include_optimizer=True)
print("saved")


converter = tf.lite.TFLiteConverter.from_keras_model_file('my_model.h5' ) # Your model's name
model = converter.convert()
file = open( 'model.tflite' , 'wb' ) 
file.write( model )
