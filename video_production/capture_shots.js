const puppeteer = require('/Users/aspa/Desktop/abhishek/IP_Sakti/sih_frontend_antigrav/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');

const OUT_DIR = '/Users/aspa/Desktop/abhishek/IP_Sakti/video_production/shots';

const delay = (ms) => new Promise(r => setTimeout(r, ms));

async function clickByText(page, text) {
  return await page.evaluate((targetText) => {
    const elements = Array.from(document.querySelectorAll('button, a, div[role="button"]'));
    const match = elements.find(el => (el.innerText || '').toLowerCase().includes(targetText.toLowerCase()));
    if (match) {
      match.scrollIntoView({ behavior: 'instant', block: 'center' });
      match.click();
      return true;
    }
    return false;
  }, text);
}

async function main() {
  console.log('Launching browser for comprehensive capture...');
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--window-size=1920,1080'],
    headless: 'new'
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  // 1. Landing Top
  console.log('1. Landing Top');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  await delay(1500);
  await page.screenshot({ path: path.join(OUT_DIR, '01_landing_hero.png') });

  // 2. Landing Mid
  console.log('2. Landing Mid');
  await page.evaluate(() => window.scrollBy({ top: 800, behavior: 'instant' }));
  await delay(800);
  await page.screenshot({ path: path.join(OUT_DIR, '02_landing_features.png') });

  // 3. Landing Stats / Architecture
  console.log('3. Landing Bottom');
  await page.evaluate(() => window.scrollBy({ top: 1200, behavior: 'instant' }));
  await delay(800);
  await page.screenshot({ path: path.join(OUT_DIR, '03_landing_stats.png') });

  // 4. App - Step 1: Jurisdiction
  console.log('4. App - Step 1: Jurisdiction');
  await page.goto('http://localhost:5173/app', { waitUntil: 'networkidle0' });
  await delay(1200);
  await page.screenshot({ path: path.join(OUT_DIR, '04_app_step1_jurisdiction.png') });

  // 5. App - Step 2: Classification & Formulation
  console.log('5. App - Step 2: Classification');
  await clickByText(page, 'CLASSIFICATION');
  await delay(800);
  // Try typing formulation details if input/textarea exists
  const inputs = await page.$$('input[type="text"], textarea');
  if (inputs.length > 0) {
    await inputs[0].type('Ashwagandha (Withania somnifera 500mg) & Curcumin Nano-emulsion for bioavailability enhancement', { delay: 10 });
  }
  await delay(600);
  await page.screenshot({ path: path.join(OUT_DIR, '05_app_step2_formulation.png') });

  // 6. App - Step 3: Issue Routing
  console.log('6. App - Step 3: Issue Routing');
  await clickByText(page, 'ISSUE ROUTING');
  await delay(800);
  await page.screenshot({ path: path.join(OUT_DIR, '06_app_step3_issues.png') });

  // 7. App - Step 4: Analysis Result
  console.log('7. App - Step 4: Analysis');
  await clickByText(page, 'ANALYSIS');
  await delay(800);
  await page.screenshot({ path: path.join(OUT_DIR, '07_app_step4_analysis.png') });

  // 8. App - Step 5: Sources
  console.log('8. App - Step 5: Sources');
  await clickByText(page, 'SOURCES');
  await delay(800);
  await page.screenshot({ path: path.join(OUT_DIR, '08_app_step5_sources.png') });

  // 9. App - Step 6: Action Plan
  console.log('9. App - Step 6: Action Plan');
  await clickByText(page, 'ACTION PLAN');
  await delay(800);
  await page.screenshot({ path: path.join(OUT_DIR, '09_app_step6_action_plan.png') });

  // 10. App - Export Markets View
  console.log('10. App - Export Markets');
  await clickByText(page, 'Export Markets');
  await delay(800);
  await page.screenshot({ path: path.join(OUT_DIR, '10_app_export_markets.png') });

  // 11. App - Law Version Timeline
  console.log('11. App - Law Timeline');
  await clickByText(page, 'Law Version Timeline');
  await delay(800);
  await page.screenshot({ path: path.join(OUT_DIR, '11_app_law_timeline.png') });

  // 12. App - Evaluation Dashboard
  console.log('12. App - Evaluation Dashboard');
  await clickByText(page, 'Evaluation');
  await delay(800);
  await page.screenshot({ path: path.join(OUT_DIR, '12_app_eval_dashboard.png') });

  // 13. App - Chat View
  console.log('13. App - Chat View');
  await clickByText(page, 'Chat');
  await delay(800);
  // Try typing a chat query
  const chatInput = await page.$('input, textarea');
  if (chatInput) {
    await chatInput.type('Is a nano-formulation of Ashwagandha patentable under Section 3(p) of Indian Patents Act?', { delay: 10 });
  }
  await delay(500);
  await page.screenshot({ path: path.join(OUT_DIR, '13_app_chat_query.png') });

  await browser.close();
  console.log('All shots captured successfully!');
}

main().catch(console.error);
