'use strict';
const puppeteer = require('puppeteer');
const fetch = require('node-fetch');
const path = require('path');
const pngToJpeg = require('png-to-jpeg');
const fs = require('fs');

let keyword = null;
if (process.argv[2]) {
  keyword = process.argv[2];
} else {
  console.log("コマンドライン引数にキーワードの指定がされていません");
  console.log("例)node chrome_launcher.js [keyword] [instagram or twitter or google]");
  process.exit(1);
}

let sns = null;
let targetUrl = null;
let sns_img_url_format = null;
if (process.argv[3] && process.argv[3] === "instagram") {
  sns = "instagram";
  targetUrl = `https://www.instagram.com/explore/tags/${keyword}`;
  sns_img_url_format = /^https:\/\/scontent-nrt1-1.cdninstagram.com\/\S*_n.jpg$/;
} else if (process.argv[3] && process.argv[3] === "twitter") {
  sns = "twitter";
  targetUrl = `https://twitter.com/search?q=${keyword}`;
  sns_img_url_format = /^https:\/\/pbs.twimg.com\/media\/\S*.jpg$/;
} else if (process.argv[3] && process.argv[3] === "google") {
  sns = "google";
  targetUrl = `https://www.google.co.jp/search?q=${keyword}&source=lnms&tbm=isch`;
  sns_img_url_format = /^(data:image\/(jpeg|png);base64,|https:\/\/encrypted\-tbn0\.gstatic\.com\/images\?q=)\S*$/;
} else {
  console.log("第二引数にスクレイピング可能なSNSの指定をしていません");
  console.log("Instagram or Twitter");
  process.exit(1);
}

let scroll = null;
if (process.argv[4]) {
  scroll = process.argv[4];
} else {
  scroll = 1;
  console.log("1回スクロールした分の画像を取得します");
}

const save_img_dir = __dirname + `/data/scraping/${sns}/${keyword}`;
if (!fs.existsSync(save_img_dir)) {
  fs.mkdirSync(save_img_dir);
}

/**
 * Headless Chromeを起動する
 */
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  try {
    await page.goto(targetUrl);
    await page.waitFor(5000);

    let count = 0;
    if (sns === 'twitter') {
      while (count < scroll) {
        count++;
        await page._client.send(
          'Input.synthesizeScrollGesture',
          {
            x: 400,
            y: 400,
            xDistance: 0,
            yDistance: -2000,
          }
        );
        console.log(`${count}回スクロールをしました。`);
      }
    } else if (sns === "instagram") {
      while(count < scroll) {
        if (count === 0) {
          count++;
          const nextElement = await page.$(`a[href*="/explore/tags/${keyword}/"]`);
          await nextElement.click();
          console.log('更読みボタンを押下しました');
        } else {
          count++;
          await page._client.send(
            'Input.synthesizeScrollGesture',
            {
              x: 400,
              y: 400,
              xDistance: 0,
              yDistance: -2000,
            }
          );
          console.log(`${count}回スクロールをしました。`);
        }
      }
    } else if (sns === "google") {
      while (count < scroll) {
        count++;
        await page._client.send(
          'Input.synthesizeScrollGesture',
          {
            x: 400,
            y: 400,
            xDistance: 0,
            yDistance: -2000,
          }
        );
        console.log(`${count}回スクロールをしました。`);
      }
    }
    const res = await page._client.send(
      'Page.getResourceTree'
    );

    let imgs = [];
    res.frameTree.resources.forEach((element, index) => {
      if (element.url.match(sns_img_url_format)) {
        imgs.push(element.url);
        // console.log(element.url);
      }
    });
    imgs.forEach(async(url, index) => {
      let contentType = null;
      let buffer = null;
      if (url.match(/(image\/(jpeg|png))/)) {
        contentType = url.match(/(image\/(jpeg|png))/)[0];
        buffer = new Buffer(url.replace(/(data:image\/(jpeg|png);base64,)/g , ''), 'base64');
      } else {
        const response = await fetch(url);
        contentType = response.headers.get('content-type');                
        buffer = await response.buffer();
      }
      const ext1 = path.extname(url);
      let ext2 = null;
      if (contentType === 'image/jpeg') {
        ext2 = '.jpg';
      } else if (contentType === 'image/png') {
        ext2 = '.jpg';
        buffer = await pngToJpeg({quality: 90})(buffer);
      }
      const filename = ext1 ? path.basename(url) : path.basename(url) + ext2;
      await fs.writeFileSync(`${save_img_dir}/${filename}`, buffer);
      if (index === imgs.length - 1) {
        console.log("ダウンロード完了しました。");
      }
    });
  } catch (error) {
    console.log(error);
  } finally {
    await browser.close();
  }
})();
