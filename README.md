# 画像式

## スクレイピング

```
npm install
```

chrome-launcherとchrome-remote-interfaceを使用したもの

```
node chrome_launcher.js [keyword] [instagram or twitter or google] [更読み回数]
```

puppeteerを使用したもの

```
node puppeteer.js [keyword] [instagram or twitter or google] [更読み回数]
```


## 画像認識

スクレイピングした画像はdata/scraping/[sns]/[keyword]に格納されるので
train/[keyword]となるように画像を置く

```
pip install keras tensorflow Pillow h5py
```

学習

```
tensorboard --logdir=tflog/
python save_model.py [画像認識したい画像のパス]
```

作成済みのモデルを使用

```
python use_model.py [画像認識したい画像のパス] [作成した学習済みモデル]
```

vi ~/.keras/keras.json

```
{
    "floatx": "float32",
    "epsilon": 1e-07,
    "backend": "tensorflow",
    "image_data_format": "channels_first"
}
```
