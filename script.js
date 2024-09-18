const http = require('http');
const playwright = require('playwright');

const server = http.createServer(async (req, res) => {
    const blockedDomains = process.env.BLOCKED_DOMAINS ? JSON.parse(process.env.BLOCKED_DOMAINS) : [];
    console.log('Blocked Domains:', blockedDomains);

    const browser = await playwright.chromium.launch({
        headless: true
    });

    const context = await browser.newContext();
    const page = await context.newPage();

    await page.route('**/*', (route) => {
        const url = new URL(route.request().url());
        const hostname = url.hostname;

        console.log(`Request URL: ${route.request().url()}`);
        console.log(`Hostname: ${hostname}`);

        if (blockedDomains.some(domain => hostname.includes(domain.replace(/https?:\/\//, '').replace(/\//g, '')))) {
            console.log(`Blocking request to: ${hostname}`);
            route.abort();
        } else {
            console.log(`Allowing request to: ${hostname}`);
            route.continue();
        }
    });

    if (req.url.startsWith('/search') || req.url === '/') {
        if (req.url === '/') {
            await page.goto('https://www.google.com');
        } else {
            const searchQuery = decodeURIComponent(req.url.split('?q=')[1]);
            console.log(`Search Query: ${searchQuery}`);

            if (blockedDomains.some(domain => searchQuery.includes(domain.replace(/https?:\/\//, '').replace(/\//g, '')))) {
                res.writeHead(403, { 'Content-Type': 'text/plain' });
                res.end(`Search for blocked domain "${searchQuery}" is restricted.`);
                await browser.close();
                return;
            }

            await page.goto(`https://www.google.com/search?q=${searchQuery}`);

            await page.evaluate((blockedDomains) => {

                document.querySelectorAll('a').forEach(link => {
                    const href = link.href;

                    if (blockedDomains.some(domain => href.includes(domain))) {
                        link.style.display = 'none';
                    }
                });
            }, blockedDomains);
        }

        const content = await page.content();

        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(content);
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }

    await browser.close();
});

server.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
