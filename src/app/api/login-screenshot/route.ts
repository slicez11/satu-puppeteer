import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    const { username, password } = await request.json();

    // Default credentials
    const defaultUsername = "hussein.al.muhtadeebillah@lecturer.unri.ac.id";
    const loginUrl = "https://satu.unri.ac.id";

    const userEmail = username || defaultUsername;
    const userPassword = password || "";

    let browser;
    try {
        const isVercel = !!process.env.VERCEL_ENV;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        let puppeteer: any;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        let launchOptions: any = {
            headless: true,
        };

        if (isVercel) {
            const chromium = (await import("@sparticuz/chromium")).default;
            puppeteer = await import("puppeteer-core");
            launchOptions = {
                ...launchOptions,
                args: chromium.args,
                executablePath: await chromium.executablePath(),
            };
        } else {
            puppeteer = await import("puppeteer");
        }

        browser = await puppeteer.launch(launchOptions);
        const page = await browser.newPage();

        // Set viewport size
        await page.setViewport({ width: 1440, height: 1440 });

        // LOGIN PROCESS
        console.log(`Navigating to login page: ${loginUrl}...`);
        await page.goto(loginUrl, { waitUntil: 'networkidle0' });
        console.log("Login page loaded");

        // Step 1: Enter email
        console.log("Step 1: Entering email...");

        // Wait for email input and capture selector
        await page.waitForSelector('input[type="email"], input[name*="email"], input[placeholder*="email"]');

        // Try different email input selectors
        const emailSelectors = [
            'input[type="email"]',
            'input[name*="email"]',
            'input[placeholder*="email"]',
            'input[name="email"]',
            'input[id*="email"]'
        ];

        let emailSelector = null;
        for (const selector of emailSelectors) {
            try {
                await page.waitForSelector(selector, { timeout: 1000 });
                emailSelector = selector;
                break;
            } catch {
                continue;
            }
        }

        if (!emailSelector) {
            throw new Error("Email input field not found");
        }

        await page.type(emailSelector, userEmail);
        console.log(`Email entered: ${userEmail}`);
        console.log(`Email selector used: ${emailSelector}`);

        // Click continue/lanjutkan button
        console.log("Clicking continue button...");

        // Try different continue button selectors
        const continueSelectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            '.btn-primary',
            'button.btn',
            'button:contains("Lanjutkan")',
            'button:contains("Continue")',
            'input[value*="Lanjutkan"]',
            'input[value*="Continue"]'
        ];

        let continueSelector = null;
        let continueClicked = false;

        for (const selector of continueSelectors) {
            try {
                await page.waitForSelector(selector, { timeout: 1000 });
                await page.click(selector);
                continueSelector = selector;
                continueClicked = true;
                console.log(`Clicked continue button with selector: ${selector}`);
                break;
            } catch {
                continue;
            }
        }

        // Alternative: find button by text content
        if (!continueClicked) {
            try {
                const textButtonClicked = await page.evaluate(() => {
                    const buttons = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                    const lanjutkanBtn = buttons.find(btn =>
                        btn.textContent?.includes('Lanjutkan') ||
                        btn.textContent?.includes('Continue') ||
                        btn.textContent?.includes('lanjutkan') ||
                        (btn as HTMLInputElement).value?.includes('Lanjutkan') ||
                        (btn as HTMLInputElement).value?.includes('Continue')
                    );
                    if (lanjutkanBtn) {
                        (lanjutkanBtn as HTMLElement).click();
                        return true;
                    }
                    return false;
                });

                if (textButtonClicked) {
                    continueClicked = true;
                    continueSelector = "button by text content";
                    console.log("Clicked continue button via text content");
                }
            } catch {
                console.log("Could not find continue button by text");
            }
        }

        if (!continueClicked) {
            console.log("Warning: Continue button not found, trying Enter key...");
            await page.keyboard.press('Enter');
        }

        // Wait for password page to load
        console.log("Waiting for password page...");
        await page.waitForNavigation({ waitUntil: 'networkidle0' });
        console.log("Password page loaded");

        // Step 2: Enter password
        console.log("Step 2: Entering password...");

        // Wait for password input and capture selector
        await page.waitForSelector('input[type="password"]');

        const passwordSelectors = [
            'input[type="password"]',
            'input[name*="password"]',
            'input[name="password"]',
            'input[id*="password"]'
        ];

        let passwordSelector = null;
        for (const selector of passwordSelectors) {
            try {
                await page.waitForSelector(selector, { timeout: 1000 });
                passwordSelector = selector;
                break;
            } catch {
                continue;
            }
        }

        if (!passwordSelector) {
            throw new Error("Password input field not found");
        }

        await page.type(passwordSelector, userPassword);
        console.log("Password entered");
        console.log(`Password selector used: ${passwordSelector}`);

        // Click login button
        console.log("Clicking login button...");

        const loginSelectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            '.btn-primary',
            'button.btn',
            'button:contains("Login")',
            'button:contains("Masuk")',
            'input[value*="Login"]',
            'input[value*="Masuk"]'
        ];

        let loginSelector = null;
        let loginClicked = false;

        for (const selector of loginSelectors) {
            try {
                await page.waitForSelector(selector, { timeout: 1000 });
                await page.click(selector);
                loginSelector = selector;
                loginClicked = true;
                console.log(`Clicked login button with selector: ${selector}`);
                break;
            } catch {
                continue;
            }
        }

        // Alternative: find button by text content
        if (!loginClicked) {
            try {
                const textLoginClicked = await page.evaluate(() => {
                    const buttons = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                    const loginBtn = buttons.find(btn =>
                        btn.textContent?.includes('Login') ||
                        btn.textContent?.includes('Masuk') ||
                        btn.textContent?.includes('login') ||
                        btn.textContent?.includes('masuk') ||
                        (btn as HTMLInputElement).value?.includes('Login') ||
                        (btn as HTMLInputElement).value?.includes('Masuk')
                    );
                    if (loginBtn) {
                        (loginBtn as HTMLElement).click();
                        return true;
                    }
                    return false;
                });

                if (textLoginClicked) {
                    loginClicked = true;
                    loginSelector = "button by text content";
                    console.log("Clicked login button via text content");
                }
            } catch {
                console.log("Could not find login button by text");
            }
        }

        if (!loginClicked) {
            console.log("Warning: Login button not found, trying Enter key...");
            await page.keyboard.press('Enter');
        }

        // Wait for login to complete
        console.log("Waiting for login to complete...");
        await page.waitForNavigation({ waitUntil: 'networkidle0' });
        console.log("Login completed successfully!");

        // Wait for dashboard to fully load
        await page.waitForFunction('document.readyState === "complete"');
        await new Promise(resolve => setTimeout(resolve, 3000)); // Additional wait for dynamic content

        // Take screenshot of dashboard
        const screenshot = await page.screenshot({
            type: 'png',
            fullPage: true,
        });

        // Return response with screenshot and element selectors
        return new NextResponse(screenshot, {
            headers: {
                'Content-Type': 'image/png',
                'Content-Disposition': 'inline; filename="dashboard-screenshot.png"',
                'X-Email-Selector': emailSelector || 'not-found',
                'X-Password-Selector': passwordSelector || 'not-found',
                'X-Continue-Selector': continueSelector || 'not-found',
                'X-Login-Selector': loginSelector || 'not-found',
                'X-Login-Status': 'success'
            },
        });

    } catch (error) {
        console.error('Login error:', error);
        return new NextResponse(
            JSON.stringify({
                error: "Login failed",
                message: error instanceof Error ? error.message : "Unknown error",
                status: 'failed'
            }),
            {
                status: 500,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}
