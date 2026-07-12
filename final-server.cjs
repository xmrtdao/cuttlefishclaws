const express = require('express');
const path = require('path');
const app = express();
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  next();
});
app.use(express.static(path.join(__dirname, 'dist-final')));
app.get('*', (req, res) => res.sendFile(path.join(__dirname, 'dist-final', 'index.html')));
app.listen(3459, () => console.log('Final test on 3459'));
