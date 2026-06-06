const https = require('https');
const fs = require('fs');

const url = "https://s.tradingview.com/widgetembed/?frameElementId=tradingview_123&symbol=NSE:VTL&interval=D&symboledit=0&saveimage=0&toolbarbg=121216&studies=%5B%5D&theme=dark&style=1&timezone=Asia%2FKolkata&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en";

https.get(url, (res) => {
  let data = '';
  res.on('data', d => data += d);
  res.on('end', () => {
    fs.writeFileSync('tv_response.html', data);
    console.log('Saved response.');
  });
});
