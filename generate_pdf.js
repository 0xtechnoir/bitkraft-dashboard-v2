const puppeteer = require('puppeteer');

(async () => {
  const appUrl = 'http://localhost:8050/';
  const outputFile = 'output.pdf';

  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.goto(appUrl, { waitUntil: 'networkidle2' });

  // Configure PDF options (optional)
  const pdfOptions = {
    path: outputFile,
    format: 'A4',
    printBackground: true,
    margin: { top: '1cm', bottom: '1cm', left: '1cm', right: '1cm' },
    scale: 0.6, // Scale the content (reduce the value if the content doesn't fit)
  };

  // Generate the PDF
  await page.pdf(pdfOptions);

  await browser.close();

  console.log(`PDF generated successfully: ${outputFile}`);
})();
