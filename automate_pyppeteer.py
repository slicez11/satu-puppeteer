#!/usr/bin/env python3
"""
Browser automation script using Pyppeteer
Goes to satu.unri.ac.id, logs in, and takes full page screenshots
"""

import os
import asyncio
import json
from datetime import datetime
from pyppeteer import launch
from PIL import Image
import numpy as np


def load_credentials(cred_file="cred.txt"):
    """Load credentials from file"""
    credentials = {}
    try:
        with open(cred_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    credentials[key] = value
        return credentials
    except FileNotFoundError:
        print(f"Credentials file {cred_file} not found!")
        return None


def load_urls(url_file="list_url.txt"):
    """Load URLs from file"""
    urls = []
    try:
        with open(url_file, 'r') as f:
            for line in f:
                url = line.strip()
                if url and url.startswith('http'):
                    urls.append(url)
        return urls
    except FileNotFoundError:
        print(f"URL file {url_file} not found!")
        return []


def auto_crop_image(image_path):
    """Auto crop image to remove sidebar and blank spaces"""
    try:
        # Open image
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Convert to grayscale for analysis
        gray = np.mean(img_array, axis=2)
        
        # Find non-white regions (assuming white background)
        # Threshold for "non-white" pixels
        threshold = 240
        non_white = gray < threshold
        
        # Find bounding box of content
        rows = np.any(non_white, axis=1)
        cols = np.any(non_white, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            print("No content found to crop")
            return image_path
        
        # Get bounding box coordinates
        top, bottom = np.where(rows)[0][[0, -1]]
        left, right = np.where(cols)[0][[0, -1]]
        
        # Add small padding
        padding = 20
        top = max(0, top - padding)
        left = max(0, left - padding)
        bottom = min(img.height, bottom + padding)
        right = min(img.width, right + padding)
        
        # Crop the image
        cropped = img.crop((left, top, right, bottom))
        
        # Save cropped image
        cropped_path = image_path.replace('.png', '_cropped.png')
        cropped.save(cropped_path, 'PNG')
        
        print(f"Image cropped: {cropped_path}")
        print(f"Original size: {img.size}, Cropped size: {cropped.size}")
        
        return cropped_path
        
    except Exception as e:
        print(f"Error cropping image: {e}")
        return image_path


async def login_and_visit_urls(login_url, urls_list, output_dir="screenshots"):
    """Login to the site and visit each URL to take screenshots"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load credentials
    credentials = load_credentials()
    if not credentials:
        return None
    
    # Launch browser
    print("Launching browser...")
    browser = await launch(
        headless=False,  # Set to True if you don't want to see the browser
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    
    try:
        page = await browser.newPage()
        
        # Set viewport size to accommodate wide content
        await page.setViewport({'width': 1440, 'height': 1440})
        
        # Maximize browser window to full screen
        await page.evaluate('''() => {
            window.moveTo(0, 0);
            window.resizeTo(screen.width, screen.height);
        }''')
        
        # LOGIN PROCESS
        print(f"Navigating to login page: {login_url}...")
        await page.goto(login_url, {'waitUntil': 'networkidle0'})
        print("Login page loaded")
        
        # Step 1: Enter email
        print("Step 1: Entering email...")
        await page.waitForSelector('input[type="email"], input[name*="email"], input[placeholder*="email"]')
        await page.type('input[type="email"], input[name*="email"], input[placeholder*="email"]', credentials['username'])
        print(f"Email entered: {credentials['username']}")
        
        # Click continue/lanjutkan button
        print("Clicking continue button...")
        # Try different selectors for the continue button
        continue_clicked = False
        try:
            # Try to find button with text "Lanjutkan"
            await page.click('button[type="submit"], input[type="submit"], .btn-primary, button.btn')
            continue_clicked = True
            print("Clicked continue button")
        except:
            try:
                # Alternative: find button by text content using XPath-like approach
                await page.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const lanjutkanBtn = buttons.find(btn => 
                        btn.textContent.includes('Lanjutkan') || 
                        btn.textContent.includes('Continue') ||
                        btn.textContent.includes('lanjutkan')
                    );
                    if (lanjutkanBtn) {
                        lanjutkanBtn.click();
                        return true;
                    }
                    return false;
                }''')
                continue_clicked = True
                print("Clicked continue button via text content")
            except Exception as e:
                print(f"Could not find continue button: {e}")
                return None
        
        if not continue_clicked:
            print("Warning: Continue button not found, trying to proceed anyway...")
            # Try pressing Enter as fallback
            await page.keyboard.press('Enter')
        
        # Wait for password page to load
        print("Waiting for password page...")
        await page.waitForNavigation({'waitUntil': 'networkidle0'})
        print("Password page loaded")
        
        # Step 2: Enter password
        print("Step 2: Entering password...")
        await page.waitForSelector('input[type="password"]')
        await page.type('input[type="password"]', credentials['password'])
        print("Password entered")
        
        # Click login button
        print("Clicking login button...")
        login_clicked = False
        try:
            # Try common login button selectors
            await page.click('button[type="submit"], input[type="submit"], .btn-primary, button.btn')
            login_clicked = True
            print("Clicked login button")
        except:
            try:
                # Alternative: find button by text content
                await page.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const loginBtn = buttons.find(btn => 
                        btn.textContent.includes('Login') || 
                        btn.textContent.includes('Masuk') ||
                        btn.textContent.includes('login') ||
                        btn.textContent.includes('masuk')
                    );
                    if (loginBtn) {
                        loginBtn.click();
                        return true;
                    }
                    return false;
                }''')
                login_clicked = True
                print("Clicked login button via text content")
            except Exception as e:
                print(f"Could not find login button: {e}")
                # Try pressing Enter as fallback
                await page.keyboard.press('Enter')
                login_clicked = True
                print("Pressed Enter as fallback")
        
        if not login_clicked:
            print("Warning: Login button not found, trying Enter key...")
            await page.keyboard.press('Enter')
        
        # Wait for login to complete
        print("Waiting for login to complete...")
        await page.waitForNavigation({'waitUntil': 'networkidle0'})
        print("Login completed successfully!")
        
        # VISIT EACH URL AND TAKE SCREENSHOTS
        screenshot_files = []
        all_form_data = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, url in enumerate(urls_list, 1):
            print(f"\n--- Visiting URL {i}/{len(urls_list)}: {url} ---")
            
            # Navigate with multiple wait conditions
            await page.goto(url, {'waitUntil': 'networkidle0'})
            print("Initial page load complete")
            
            # Wait for page to be fully interactive
            await page.waitForFunction('document.readyState === "complete"')
            print("Page fully loaded")
            
            # No CSS injection - keep pages as-is
            
            # Additional wait for any dynamic content
            await asyncio.sleep(5)
            print("Waiting for dynamic content to load...")
            
            # Wait for any images to load
            await page.waitForFunction('''() => {
                const images = Array.from(document.images);
                return images.every(img => img.complete);
            }''', {'timeout': 10000})
            print("All images loaded")
            
            # Scroll to load all content with better waiting
            print("Scrolling to load all content...")
            await page.evaluate('''() => {
                return new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 100;
                    let stableCount = 0;
                    let lastHeight = 0;
                    
                    const timer = setInterval(() => {
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        
                        // Check if height is stable (no new content loading)
                        if (scrollHeight === lastHeight) {
                            stableCount++;
                        } else {
                            stableCount = 0;
                            lastHeight = scrollHeight;
                        }
                        
                        // If height is stable for 3 iterations and we've scrolled enough
                        if (stableCount >= 3 && totalHeight >= scrollHeight) {
                            clearInterval(timer);
                            window.scrollTo(0, 0);
                            // Additional wait for any lazy-loaded content
                            setTimeout(resolve, 2000);
                        }
                    }, 200);
                });
            }''')
            print("Scrolling complete, waiting for final content...")
            
            # Final wait for any remaining dynamic content
            await asyncio.sleep(3)
            
            # Find all "Isi" links with the specific structure
            print("Finding all 'Isi' links...")
            isi_links = await page.evaluate('''() => {
                const links = [];
                
                // Find all links with "Isi" text and href containing "input"
                const isiElements = document.querySelectorAll('a.btn.btn-primary');
                isiElements.forEach(link => {
                    if (link.textContent.includes('Isi') && link.href.includes('input')) {
                        links.push(link.href);
                    }
                });
                
                return links;
            }''')
            
            print(f"Found {len(isi_links)} 'isi' links: {isi_links}")
            
            # Navigate to links at index 4-7 (rows 5-8)
            for idx in range(4, min(8, len(isi_links))):
                if idx < len(isi_links):
                    link = isi_links[idx]
                    print(f"Navigating to link {idx + 1}: {link}")
                    
                    # Navigate directly to the URL
                    await page.goto(link, {'waitUntil': 'networkidle0'})
                    
                    # Wait for page to load
                    await page.waitForFunction('document.readyState === "complete"')
                    await asyncio.sleep(2)
                    
                    # Extract form data and course info
                    print("Extracting form data and course information...")
                    form_data = await page.evaluate('''() => {
                        const data = {};
                        
                        // Get course information from the page header
                        const courseInfo = {};
                        
                        // Find all rows with course information
                        const infoRows = document.querySelectorAll('.row.border-gray-300');
                        infoRows.forEach(row => {
                            const labels = row.querySelectorAll('label');
                            const values = row.querySelectorAll('.fw-bold');
                            
                            labels.forEach((label, index) => {
                                const labelText = label.textContent.trim();
                                const valueDiv = values[index];
                                if (valueDiv) {
                                    let valueText = valueDiv.textContent.trim();
                                    
                                    // Clean up the text (remove extra whitespace, newlines)
                                    valueText = valueText.replace(/\\s+/g, ' ').trim();
                                    
                                    if (labelText === 'Program Studi') {
                                        courseInfo.program_studi = valueText;
                                    } else if (labelText === 'Semester') {
                                        courseInfo.semester = valueText;
                                    } else if (labelText === 'Mata Kuliah') {
                                        courseInfo.mata_kuliah = valueText;
                                    } else if (labelText === 'Dosen Pengampu') {
                                        courseInfo.dosen_pengampu = valueText;
                                    } else if (labelText === 'Kelas') {
                                        courseInfo.kelas = valueText;
                                    }
                                }
                            });
                        });
                        
                        data.course_info = courseInfo;
                        
                        // Get form action URL
                        const form = document.querySelector('form');
                        if (form) {
                            data.form_action = form.action;
                        }
                        
                        // Get CSRF token
                        const token = document.querySelector('input[name="_token"]');
                        if (token) {
                            data.csrf_token = token.value;
                        }
                        
                        // Get selected dosen option
                        const selectedOption = document.querySelector('input[name="dosenOption"]:checked');
                        if (selectedOption) {
                            data.dosen_option = selectedOption.value;
                        }
                        
                        // Get dosen hadir (present lecturer)
                        const dosenHadir = document.querySelector('#selectDosenHadir');
                        if (dosenHadir) {
                            data.dosen_hadir = {
                                value: dosenHadir.value,
                                text: dosenHadir.options[dosenHadir.selectedIndex]?.text || ''
                            };
                        }
                        
                        // Get dosen pengganti asing (foreign substitute)
                        const dosenPenggantiAsing = document.querySelector('#inputDosenPenggantiAsing');
                        if (dosenPenggantiAsing) {
                            data.dosen_pengganti_asing = dosenPenggantiAsing.value;
                        }
                        
                        // Get asal instansi (institution origin)
                        const asalInstansi = document.querySelector('#inputInstansiAsal');
                        if (asalInstansi) {
                            data.asal_instansi = asalInstansi.value;
                        }
                        
                        // Get tanggal rencana (planned date)
                        const tanggalRencana = document.querySelector('#inputTanggalRencana');
                        if (tanggalRencana) {
                            data.tanggal_rencana = tanggalRencana.value;
                        }
                        
                        // Get tanggal terlaksana (actual date)
                        const tanggalTerlaksana = document.querySelector('input[name="inputTanggalTerlaksana"]');
                        if (tanggalTerlaksana) {
                            data.tanggal_terlaksana = tanggalTerlaksana.value;
                        }
                        
                        // Get tema (theme)
                        const tema = document.querySelector('#inputTema');
                        if (tema) {
                            data.tema = tema.value;
                        }
                        
                        // Get pokok bahasan (topic of discussion)
                        const pokokBahasan = document.querySelector('#exampleFormControlTextarea1');
                        if (pokokBahasan) {
                            data.pokok_bahasan = pokokBahasan.value;
                        }
                        
                        // Get current URL
                        data.current_url = window.location.href;
                        
                        // Get page title
                        data.page_title = document.title;
                        
                        return data;
                    }''')
                    
                    # Add row info to form data
                    form_data['url_index'] = i
                    form_data['row_number'] = idx + 1
                    form_data['original_url'] = url
                    
                    # Add to combined data array
                    all_form_data.append(form_data)
                    
                    print(f"Form data collected for row {idx + 1}")
                    print(f"Form data: {json.dumps(form_data, indent=2, ensure_ascii=False)}")
                    
                    # Take screenshot of this page
                    filename = f"url_{i:02d}_row_{idx+1}_{timestamp}.png"
                    filepath = os.path.join(output_dir, filename)
                    
                    await page.screenshot({
                        'path': filepath,
                        'fullPage': True,
                        'quality': 90,
                        'type': 'png'
                    })
                    
                    # Auto crop the screenshot
                    cropped_path = auto_crop_image(filepath)
                    screenshot_files.append(cropped_path)
                    print(f"Screenshot saved: {filename}")
                    
                    # No need to go back - just continue to next link
            
            # Skip the original screenshot since we're taking individual ones
            continue
            
            # Take full page screenshot
            filename = f"url_{i:02d}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            
            # Get page height for reference (but don't modify width)
            page_height = await page.evaluate('''() => {
                return Math.max(document.body.scrollHeight, document.body.offsetHeight, 
                               document.documentElement.clientHeight, document.documentElement.scrollHeight, 
                               document.documentElement.offsetHeight);
            }''')
            
            # Get current viewport width
            viewport = page.viewport
            print(f"Page height: {page_height}px, Viewport width: {viewport['width']}px")
            
            # Take screenshot with full page height and width
            await page.screenshot({
                'path': filepath,
                'fullPage': True,
                'clip': None,  # Ensure we capture the full content area
                'quality': 90,  # High quality for better readability
                'type': 'png'   # PNG for better text clarity
            })
            
            screenshot_files.append(filepath)
            print(f"Full page screenshot saved: {filename}")
        
        # Save combined JSON data
        if all_form_data:
            combined_json_filename = f"combined_form_data_{timestamp}.json"
            combined_json_filepath = os.path.join(output_dir, combined_json_filename)
            
            with open(combined_json_filepath, 'w', encoding='utf-8') as f:
                json.dump(all_form_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Combined JSON data saved: {combined_json_filename}")
            print(f"📊 Total form data entries: {len(all_form_data)}")
        
        print(f"\n✅ Completed! {len(screenshot_files)} screenshots taken.")
        return screenshot_files
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
        
    finally:
        await browser.close()


async def main():
    """Main function"""
    login_url = "https://satu.unri.ac.id"
    urls_list = load_urls()
    
    if not urls_list:
        print("❌ No URLs found in list_url.txt")
        return
    
    print(f"📋 Found {len(urls_list)} URLs to visit:")
    for i, url in enumerate(urls_list, 1):
        print(f"   {i}. {url}")
    
    screenshot_files = await login_and_visit_urls(login_url, urls_list)
    
    if screenshot_files:
        print("\n✅ Automation completed successfully!")
        print(f"📸 Screenshots taken:")
        for file in screenshot_files:
            print(f"   - {file}")
    else:
        print("❌ Failed to complete automation")


if __name__ == "__main__":
    asyncio.run(main())
