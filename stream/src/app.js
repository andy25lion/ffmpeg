const express = require("express");
var serveIndex = require('serve-index');
var recursive = require("recursive-readdir");
var path = require('path');
const fs = require('fs');
var morgan = require('morgan');
const app = express();
const server = require('http').Server(app);
const io = require('socket.io')(server);
const request = require('request');
const basicAuth = require('express-basic-auth')
const exec = require('child_process').exec;
const readLastLines = require('read-last-lines');
const proxy = require('express-http-proxy');
const { createProxyMiddleware } = require('http-proxy-middleware');


app.set('view engine', 'pug');
app.set('views', path.join(__dirname, '/views'));

const FILE_DIRECTORY = __dirname;
const CONFIG_PATH = process.env.CONFIG_PATH || './config.json';
const APP_CONFIG = JSON.parse(fs.readFileSync(CONFIG_PATH));


app.use(basicAuth({ users: APP_CONFIG.users, challenge: true}));
app.use('/', express.static(path.join(__dirname, '/static')));
app.use('/files', express.static(APP_CONFIG.storagePath));
app.use('/files', serveIndex(APP_CONFIG.storagePath));
app.use(morgan('combined'));

let frontendModel = { streams: {}};

function reloadLiveVideoFiles(doneCallback) {
  channels = APP_CONFIG.streams.length;
  channelsDone = 0;
  for (const stream of APP_CONFIG.streams){
    if (stream.type == 'liveimg') {
      frontendModel.streams[stream.name] = {
        playlistPath: 'NA',
        lastFile: path.join('/files', stream.name, stream.liveSegment+'?date='+Date.now()),
        delayedUpdate: stream.delayedUpdate,
        type: stream.type,
        refreshInterval: stream.refreshInterval,
      };
      channelsDone += 1;
      continue;
    }
    if (stream.type.startsWith('video')) {
      playlistFile = path.join(APP_CONFIG.storagePath, stream.name, stream.livePlaylistName);
      if (!fs.existsSync(playlistFile)) {
        console.log('file not found')
        channelsDone += 1;
        continue;
      }
      readLastLines.read(playlistFile, 1).then((lines) => {
        const file = lines.split(',')[0]
        if (file.endsWith('.mp4')){
          frontendModel.streams[stream.name] = {
            playlistPath: playlistFile,
            lastFile: path.join('/files', stream.name, file),
            delayedUpdate: stream.delayedUpdate,
            type: stream.type,
            refreshInterval: stream.refreshInterval,
          };
        }
        channelsDone += 1;
        if (channelsDone == channels) doneCallback();
      });
      continue;
    }
    if (stream.type == 'proxy') {
      frontendModel.streams[stream.name] = {
        playlistPath: 'NA',
        lastFile: stream.proxy.endpoint,
        delayedUpdate: stream.delayedUpdate,
        type: stream.type,
        refreshInterval: stream.refreshInterval,
      };
      channelsDone += 1;
      continue;
    }
    if (stream.type == 'hls') {
      playlistFile = path.join('files', stream.name, stream.livePlaylistName);
      frontendModel.streams[stream.name] = {
        playlistPath: playlistFile,
        lastFile: playlistFile,
        delayedUpdate: stream.delayedUpdate,
        type: stream.type,
        refreshInterval: stream.refreshInterval,
      };
      channelsDone += 1;
      continue;
    }
  }
  if (channelsDone == channels) doneCallback();
}

app.get('/model', (req, res) => {
  reloadLiveVideoFiles(() => {
    res.send(frontendModel);
  });
});

app.get('/liveview', (req, res) => {
  reloadLiveVideoFiles(() => {
    res.render('liveview', frontendModel);
  });
});

server.listen(APP_CONFIG.port, () => {
  console.log(`Live view app listening on port ` + APP_CONFIG.port);
});

//Initial config
for (const stream of APP_CONFIG.streams){
  if (stream.type == 'proxy') {
    app.use(stream.proxy.endpoint, createProxyMiddleware({ target: stream.proxy.target, changeOrigin: true }));
  }
}