import asyncio
import csv
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

def final_clean_text(text):
    """Prunes metadata blocks and normalizes text for NLP models."""
    if not text:
        return ""
    text = re.sub(r'^About\s+.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', '', text, flags=re.IGNORECASE)
    text = re.sub(r'review collected (organically|from invite)', '', text, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', text).strip()

async def get_product_links(page):
    """Crawl Phase: Discover individual product review directories."""
    print("🕸️  Crawling main page for product specific links...")
    product_urls = set()
    try:
        await page.goto('https://judge.me/reviews/stores/ramrajcotton.in', wait_until='networkidle', timeout=60000)
        
        # Scroll down to load product grids
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, 1000);")
            await asyncio.sleep(1)
            
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract links containing product paths
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/products/' in href:
                # Handle relative paths cleanly
                full_url = href if href.startswith('http') else f"https://judge.me{href}"
                product_urls.add(full_url)
                
    except Exception as e:
        print(f" ⚠️ Crawl warning: {e}")
    return list(product_urls)

async def scrape_product_page(page, url):
    """Scrape Phase: Extract targets directly from dynamic product nodes."""
    reviews = []
    try:
        await page.goto(url, wait_until='load', timeout=30000)
        await asyncio.sleep(1) # Brief pause for widget hydration
        
        # Pull text contexts right out of active browser rendering maps
        reviews_data = await page.evaluate("""() => {
            const elements = document.querySelectorAll('.jdgm-rev__body, .jdgm-rev__title');
            return Array.from(elements).map(el => el.innerText);
        }""")
        
        for raw_text in reviews_data:
            cleaned = final_clean_text(raw_text)
            if len(cleaned) > 15 and "verified by" not in cleaned.lower():
                reviews.append(cleaned)
    except Exception:
        pass # Quietly bypass timeouts on broken links to keep loop moving
    return reviews

async def main():
    print("=" * 70)
    print("DEEP CRAWLER & SCRAPER - BULK VOLUME MODE")
    print("=" * 70)
    
    clean_dataset = []
    seen = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Step 1: Crawl to build target list
        discovered_links = await get_product_links(page)
        print(f"   🎯 Found {len(discovered_links)} product review pathways to harvest.")

        # Step 2: Loop over discovered links to pull distinct reviews
        print("\n🚀 Beginning mass collection loop...")
        for idx, url in enumerate(discovered_links, 1):
            print(f"   [{idx}/{len(discovered_links)}] Scraping deep path...")
            product_reviews = await scrape_product_page(page, url)
            
            for review in product_reviews:
                if review.lower() not in seen:
                    seen.add(review.lower())
                    clean_dataset.append([url, review])
            
            # Rate limiting safety to avoid getting blocked by Judge.me
            await asyncio.sleep(0.5)

        # Step 3: Run the backup official store page scraper to maximize data
        print("\n📦 Processing Backup Source: Ramraj Cotton Store Reviews...")
        try:
            await page.goto('https://ramrajcotton.in/pages/store-reviews', wait_until='load')
            for _ in range(4):
                await page.evaluate("window.scrollBy(0, 800);")
                await asyncio.sleep(0.5)
            soup = BeautifulSoup(await page.content(), 'html.parser')
            for p_tag in soup.select('main p, #main p, .shopify-section p'):
                cleaned = final_clean_text(p_tag.get_text(strip=True))
                ui_keywords = [
    'currency', 'sort by', 'filter', 'cancel', 'shipping', 'cookie', 'javascript',
    'latest news', 'established in 1983', 'get the latest'
]
                if len(cleaned) > 20 and not any(k in cleaned.lower() for k in ui_keywords):
                    if cleaned.lower() not in seen:
                        seen.add(cleaned.lower())
                        clean_dataset.append(['https://ramrajcotton.in/pages/store-reviews', cleaned])
        except Exception as e:
            print(f"   ⚠️ Store fallback warning: {e}")

        await browser.close()

    # --- SAVE RESULTS ---
    output_file = 'ramraj_bulk_clean_feedback.csv'
    if clean_dataset:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Feedback'])
            writer.writerows(clean_dataset)
            
        print("\n" + "=" * 70)
        print(f"🎯 COLLECTION MASS COMPLETED! Saved {len(clean_dataset)} Clean Rows.")
        print(f"   Dataset saved to: {output_file}")
        print("=" * 70)
    else:
        print("\n❌ Crawl structural execution failed. No links captured.")

if __name__ == "__main__":
    asyncio.run(main())