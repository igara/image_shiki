from keras.models import load_model
import numpy as np
from PIL import Image
import os
import shutil
import sys
import re
import datetime

# 学習用のデータを作る.
label_list = []

r = re.compile("^(?!\.\S*)")
traindir = [x for x in os.listdir("data/train") if r.match(x)]
if len(traindir) < 2:
    print("data/train配下の学習させるデータのフォルダを2つ以上あるように設置してください")
    sys.exit()

# コマンドライン引数
argvs = sys.argv
if (len(argvs) != 3):
    print("コマンドラインの指定を下記のようにしてください")
    print("python use_model.py [画像認識したい画像のパス] [作成した学習済みモデル]")
    sys.exit()

image_path = argvs[1]
if not os.path.exists(image_path):
    print("指定した画像が存在しません")
    sys.exit()

learn_path = argvs[2]
if not os.path.exists(learn_path):
    print("指定したモデルが存在しません")
    sys.exit()

if os.path.exists("data/test/"):
    shutil.rmtree("data/test/")
    os.mkdir("data/test/")

# ./data/testにディレクトリを作成する
for dir in traindir:
    if dir == ".DS_Store":
        continue
    if dir == ".keep":
        continue

    test_dir = "data/test/" + dir
    os.mkdir(test_dir)
    shutil.copy(image_path, test_dir)

# モデルを生成してニューラルネットを構築
model = load_model(learn_path)

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
            image = np.array(Image.open(filepath).resize((128, 128)))
            image = image.transpose(2, 0, 1)
            result = model.predict_classes(np.array([image / 255.]))

            total += 1.

            if test_label == result:
                ok_count += 1.
    test_label += 1

print("この画像は" + traindir[result[0]])
