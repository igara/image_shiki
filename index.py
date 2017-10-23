from keras.models import Sequential
from keras.layers import Activation, Dense, Dropout
from keras.utils.np_utils import to_categorical
from keras.optimizers import Adagrad
from keras.optimizers import Adam
import numpy as np
from PIL import Image
import os

# 学習用のデータを作る.
image_list = []
label_list = []

train_label = 0
# ./data/train 以下のorange,appleディレクトリ以下の画像を読み込む。
for dir in os.listdir("data/train"):
    if dir == ".DS_Store":
        continue
    if dir == ".keep":
        continue

    dir1 = "data/train/" + dir

    for file in os.listdir(dir1):
        if file != ".DS_Store":
            # 配列label_listに正解ラベルを追加(りんご:0 オレンジ:1)
            label_list.append(train_label)
            filepath = dir1 + "/" + file
            # 画像を25x25pixelに変換し、1要素が[R,G,B]3要素を含む配列の25x25の２次元配列として読み込む。
            # [R,G,B]はそれぞれが0-255の配列。
            image = np.array(Image.open(filepath).resize((25, 25)))
            # print(filepath)
            # 配列を変換し、[[Redの配列],[Greenの配列],[Blueの配列]] のような形にする。
            image = image.transpose(2, 0, 1)
            # さらにフラットな1次元配列に変換。最初の1/3はRed、次がGreenの、最後がBlueの要素がフラットに並ぶ。
            image = image.reshape(1, image.shape[0] * image.shape[1] * image.shape[2]).astype("float32")[0]
            # 出来上がった配列をimage_listに追加。
            image_list.append(image / 255.)
    train_label += 1

# kerasに渡すためにnumpy配列に変換。
image_list = np.array(image_list)

# ラベルの配列を1と0からなるラベル配列に変更
# 0 -> [1,0], 1 -> [0,1] という感じ。
Y = to_categorical(label_list)

# モデルを生成してニューラルネットを構築
model = Sequential()
model.add(Dense(200, input_dim=1875))
model.add(Activation("relu"))
model.add(Dropout(0.2))

model.add(Dense(200))
model.add(Activation("relu"))
model.add(Dropout(0.2))

model.add(Dense(2))
model.add(Activation("softmax"))

# オプティマイザにAdamを使用
opt = Adam(lr=0.001)
# モデルをコンパイル
model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
# 学習を実行。10%はテストに使用。
model.fit(image_list, Y, nb_epoch=1500, batch_size=100, validation_split=0.1)
model.save("train.h5")

print("\n\n\n\n\n\n\n\n")
print("--------------- train finish ---------------")
print("\n\n\n\n\n\n\n\n")

# テスト用ディレクトリ(./data/train/)の画像でチェック。正解率を表示する。
total = 0.
ok_count = 0.
test_label = 0
for dir in os.listdir("data/train"):
    if dir == ".DS_Store":
        continue
    if dir == ".keep":
        continue

    dir1 = "data/test/" + dir 

    for file in os.listdir(dir1):
        if file != ".DS_Store":
            label_list.append(test_label)
            filepath = dir1 + "/" + file
            image = np.array(Image.open(filepath).resize((25, 25)))
            print(filepath)
            image = image.transpose(2, 0, 1)
            image = image.reshape(1, image.shape[0] * image.shape[1] * image.shape[2]).astype("float32")[0]
            result = model.predict_classes(np.array([image / 255.]))
            print("label:", test_label, "result:", result[0])

            total += 1.

            if test_label == result[0]:
                ok_count += 1.
            print(result)
    test_label += 1

print("seikai: ", ok_count / total * 100, "%")
