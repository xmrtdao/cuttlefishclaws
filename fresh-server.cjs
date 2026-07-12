const express = require('express');
const path = require('path');
const app = express();
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  next();
});
app.use(express.static(path.join(__dirname, 'dist-fresh')));
app.get('*', (req, res) => res.sendFile(path.join(__dirname, 'dist-fresh', 'index.html')));
app.listen(3458, () => console.log('Fresh test on 3458'));
