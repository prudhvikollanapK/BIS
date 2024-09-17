const puppeteer = require('puppeteer');

(async () => {
    const blockedDomains = process.env.BLOCKED_DOMAINS ? JSON.parse(process.env.BLOCKED_DOMAINS) : [];
    console.log('Blocked Domains Environment Variable:', process.env.BLOCKED_DOMAINS);  // Log environment variable
    console.log('Parsed Blocked Domains:', blockedDomains);  // Log parsed domains

    const browser = await puppeteer.launch({
        headless: true,  // Switch to headless mode
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    await page.setRequestInterception(true);

    page.on('request', request => {
        const url = new URL(request.url());
        const hostname = url.hostname;

        console.log(`Request URL: ${request.url()}`);  // Log all URLs being requested
        console.log(`Hostname: ${hostname}`);  // Log just the hostname for clarity

        if (blockedDomains.some(domain => hostname.includes(domain.replace(/https?:\/\//, '').replace(/\//g, '')))) {
            console.log(`Blocking request to: ${hostname}`);
            request.abort();
        } else {
            console.log(`Allowing request to: ${hostname}`);
            request.continue();
        }
    });

    await page.goto('https://www.google.com');

})();
