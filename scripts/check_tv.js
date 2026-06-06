const https = require('https');

function checkSymbol(sym) {
  https.get('https://s.tradingview.com/widgetembed/?symbol=' + sym, (res) => {
    let data = '';
    res.on('data', d => data += d);
    res.on('end', () => {
      const match = data.match(/"symbol":\s*"([^"]+)"/);
      console.log(`${sym} resolved to: ${match ? match[1] : 'Not found'}`);
    });
  });
}

checkSymbol('NSE:VTL');
checkSymbol('NASDAQ:AAPL');
checkSymbol('BSE:VTL');
