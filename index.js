'use strict';

let keyword = null;
if (process.argv[2]) {
    keyword = process.argv[2];
} else {
    console.log("コマンドライン引数にキーワードの指定がされていません");
    console.log("例)node index.js [keyword] [instagram or twitter]");
    process.exit(1);
}

let sns = null;
let targetUrl = null;
let sns_img_url_format = null;
if (process.argv[3] && process.argv[3] === "instagram") {
    sns = "instagram";
    targetUrl = `https://www.instagram.com/explore/tags/${keyword}`;
    sns_img_url_format = /^https:\/\/scontent-nrt1-1.cdninstagram.com\/\S*_n.jpg$/;
} else if (process.argv[3] && process.argv[3]==="twitter") {
    sns = "twitter";
    targetUrl = `https://twitter.com/search?q=${keyword}`;
    sns_img_url_format = /^https:\/\/pbs.twimg.com\/media\/\S*.jpg$/;
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
const fs = require('fs');
if (!fs.existsSync(save_img_dir)) {
    fs.mkdirSync(save_img_dir);
}

const chromeLauncher = require('chrome-launcher');
const CDP = require('chrome-remote-interface');

/**
 * Headless Chromeを起動する
 */
async function startHeadlessChrome() {
    try {
        return await chromeLauncher.launch({
            startingUrl: 'target:brank',
            chromeFlags: ['--headless', '--disable-gpu']
        });
    } catch (error) {
        console.log(error);
    }
}

/**
 * main
 */
async function main() {
    const chrome = await startHeadlessChrome();
    const options = {
        port: chrome.port
    };
    CDP(options, async(client) => {
        try {
            // extract domains
            const {Network, Page, Runtime, Input, DOM} = client;
            // setup handlers
            Network.requestWillBeSent((params) => {
                // console.log(params.request.url);
            });
            // enable events then start!
            await Promise.all([
                Network.enable(),
                Page.enable(),
                Runtime.enable(),
            ]);
            await Page.navigate({url: targetUrl});
            // ローディングアイコンが消える時
            await Page.loadEventFired();

            // SPAの描画を待つ
            await sleep(3000);

            let count = 0;
            if (sns === 'twitter') {
                while(count < scroll) {
                    count++;

                    await Input.synthesizeScrollGesture({
                        x: 400,
                        y: 400,
                        xDistance: 0,
                        yDistance: -2000,
                    });
                    console.log(`${count}回スクロールをしました。`);
                }
            } else if (sns === "instagram") {
                while(count < scroll) {
                    if (count === 0) {
                        const js = `document.querySelector('a[href*="/explore/tags/${keyword}/"]').click()`;
                        await Runtime.evaluate({expression: js});
                        count++;
                        console.log('更読みボタンを押下しました');
                    } else {
                        count++;
                        await Input.synthesizeScrollGesture({
                            x: 400,
                            y: 400,
                            xDistance: 0,
                            yDistance: -2000,
                        });
                        console.log(`${count}回スクロールをしました。`);
                    }
                }
            }

            const res = await Page.getResourceTree();
            const exec = require('child_process').execSync;

            let imgs = [];
            res.frameTree.resources.forEach((element, index) => {
                if (element.url.match(sns_img_url_format)) {
                    imgs.push(element.url);
                    console.log(element.url);
                }
            });
            imgs.forEach((url, index) => {
                exec(`(cd ${save_img_dir} && curl -Os ${url})`);
                const result = exec(`echo $?`).toString();
                if (index === imgs.length) {
                    console.log("ダウンロード完了しました。");
                }
            });
        } catch (error) {
            console.log(error);
        } finally {
            // close the connection to the remote instance.
            await client.close();
            // headless chrome close
            await chrome.kill();
        }
    }).on('error', (err) => {
        // cannot connect to the remote endpoint
        console.error(err);
    });
}

/**
 * 指定したms待機
 * @param {int} time 
 */
function sleep(time) {
    const d1 = new Date();
    while (true) {
        const d2 = new Date();
        if (d2 - d1 > time) {
            return;
        }
    }
}

main();
