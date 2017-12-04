from keras.models import Sequential
from keras.layers import Activation, Dense, Dropout, Conv2D, MaxPooling2D, Flatten
from keras.utils.np_utils import to_categorical
from keras.optimizers import Adam
import numpy as np
from PIL import Image
import os
import shutil
import sys
import re
import datetime

# 学習用のデータを作る.
image_list = []
label_list = []

train_label = 0

r = re.compile("^(?!\.\S*)")
traindir = [x for x in os.listdir("data/train") if r.match(x)]
if len(traindir) < 2:
    print("data/train配下の学習させるデータのフォルダを2つ以上あるように設置してください")
    sys.exit()

# コマンドライン引数
argvs = sys.argv
if (len(argvs) != 2):
    print("コマンドラインの指定を下記のようにしてください")
    print("python save_model.py [画像認識したい画像のパス]")
    sys.exit()

image_path = argvs[1]
if not os.path.exists(image_path):
    print("指定した画像が存在しません")
    sys.exit()

if os.path.exists("data/test/"):
    shutil.rmtree("data/test/")
    os.mkdir("data/test/")

# ./data/trainディレクトリ以下の画像を読み込む。
for dir in traindir:
    if dir == ".DS_Store":
        continue
    if dir == ".keep":
        continue

    test_dir = "data/test/" + dir
    os.mkdir(test_dir)
    shutil.copy(image_path, test_dir)

    dir1 = "data/train/" + dir

    for file in os.listdir(dir1):
        if file != ".DS_Store":
            # 配列label_listに正解ラベルを追加(りんご:0 オレンジ:1)
            label_list.append(train_label)
            filepath = dir1 + "/" + file
            # 画像を25x25pixelに変換し、1要素が[R,G,B]3要素を含む配列の100x100の２次元配列として読み込む。
            # [R,G,B]はそれぞれが0-255の配列。
            image = np.array(Image.open(filepath).resize((100, 100)))
            # 配列を変換し、[[Redの配列],[Greenの配列],[Blueの配列]] のような形にする。
            image = image.transpose(2, 0, 1)
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
model.add(Conv2D(32, (3, 3), padding="same", input_shape=image_list.shape[1:]))
model.add(Activation('relu'))
model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(train_label))
model.add(Activation("softmax"))

# オプティマイザにAdamを使用
opt = Adam(lr=0.001)
# モデルをコンパイル
model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
# 学習を実行。10%はテストに使用。
model.fit(image_list, Y, epochs=10, batch_size=100, validation_split=0.1)

d = datetime.datetime.now()
# モデルを保存する
model.save(d.strftime("%Y%m%d%H%M%S") + ".h5")

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
        if file != ".DS_Store" and file != ".keep":
            label_list.append(test_label)
            filepath = dir1 + "/" + file
            image = np.array(Image.open(filepath).resize((100, 100)))
            image = image.transpose(2, 0, 1)
            result = model.predict_classes(np.array([image / 255.]))

            total += 1.

            if test_label == result:
                ok_count += 1.
    test_label += 1

print("この画像は" + traindir[result[0]])
