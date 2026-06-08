import asyncio
import csv
import re
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

def normalize_url(url_string):
    """Cleans and normalizes URLs to avoid duplicate paths."""
    if not url_string:
        return ""
    try:
        parsed = urlparse(url_string.strip())
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip('/')
        return urlunparse((scheme, netloc, path, '', '', ''))
    except Exception as e:
        print(f"⚠️ URL Normalization warning: {e}")
        return url_string

def final_clean_text(text):
    """Deep text cleaning to ensure machine-learning ready format."""
    if not text:
        return ""
    text = re.sub(r'^About\s+.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', '', text, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', text).strip()

def is_legit_review(text):
    """Rigorous filtering with defensive heuristics to block web layout boilerplate."""
    cleaned_len = len(text)
    
    # FIXED: Lowered threshold to catch vital short feedback like "Poor stitching."
    if cleaned_len < 8 or cleaned_len > 1000:
        return False
        
    text_lower = text.lower()
    
    if '₹' in text or 'inr' in text_lower or ('from' in text_lower and ('.00' in text_lower or '00 ' in text_lower)):
        return False
        
    if 'product specifications' in text_lower or 'material:' in text_lower or 'pack content:' in text_lower:
        return False

    ui_blacklist = [
        'currency', 'sort by', 'filter', 'cancel', 'shipping', 'cookie', 'javascript',
        'latest news', 'established in 1983', 'get the latest', 'subscribe', 'rights reserved',
        'pioneer in manufacturing', 'our products are manufactured', 'traditional dhoti',
        'prevent spam', 'marked with the icon', 'authenticate all reviews', 'trustworthiness',
        'security researchers', 'registry number', 'worship street', 'london, england', 
        'copyright 2026', 'judge.me', 'write a review', 'picture/video', 'privacy policy', 'terms and conditions'
    ]
    
    if any(phrase in text_lower for phrase in ui_blacklist):
        return False
        
    # POSITIVE INDICATOR FILTER: Ensures broad <p> tag text actually relates to commercial feedback
    review_keywords = [
        "quality", "delivery", "fabric", "fit", "service", "refund", "price", 
        "product", "order", "received", "stitching", "wear", "shirt", "dhoti", 
        "towel", "material", "good", "bad", "comfortable", "brand", "nice", "happy"
    ]
    if not any(keyword in text_lower for keyword in review_keywords):
        return False
        
    return True

async def crawl_for_products(page):
    """Extracts multiple product links to scale the scraping process."""
    print("🕸️  Phase 1: Crawling Judge.me to discover product pages...")
    product_links = set()
    try:
        await page.goto('https://judge.me/reviews/stores/ramrajcotton.in', wait_until='domcontentloaded', timeout=45000)
        await asyncio.sleep(3) 
        
        for _ in range(6):
            await page.evaluate("window.scrollBy(0, 1000);")
            await asyncio.sleep(1)
            
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            # FIXED: Avoid extracting system tracking parameters or loops
            if '/products/' in href and 'judge.me' not in href:
                full_url = href if href.startswith('http') else f"https://ramrajcotton.in{href}"
                product_links.add(normalize_url(full_url))
    except Exception as e:
        print(f"   ⚠️ Crawl issue: {e}. Falling back to manual seed links.")
        
    return list(product_links)

async def scrape_reviews_from_url(page, url):
    """Visits a specific sub-page and extracts clean user text elements."""
    reviews = []
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(1.5)
        
        # TARGETED EXTRACTION: Look closely at real review containers along with text fallbacks
        raw_elements = await page.evaluate("""() => {
            const elements = document.querySelectorAll('.jdgm-rev__body, .jdgm-rev__title, .spr-review-body, p');
            return Array.from(elements).map(el => el.innerText);
        }""")
        
        for raw_text in raw_elements:
            cleaned = final_clean_text(raw_text)
            if is_legit_review(cleaned):
                reviews.append(cleaned)
    except Exception as e:
        # FIXED: Log errors transparently instead of silently passing
        print(f"   ❌ Error processing layout for URL [{url}]: {e}")
    return reviews

async def main():
    print("=" * 70)
    print("PRODUCTION DEEP CRAWLER & SCRAPER — STABLE ML READY")
    print("=" * 70)
    
    clean_dataset = []
    seen = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Step 1: Run Crawler
        target_urls = await crawl_for_products(page)
        
        if not target_urls:
            print("   ⚠️ Target directory hidden. Injecting verified pathways...")
            fallback_list = [
                "https://ramrajcotton.in/products/newborn-baby-traditional-set-cream-1",
                "https://ramrajcotton.in/products/boys-cream-half-sleeves-dhoti-with-towel-set",
                "https://ramrajcotton.in/products/ultra-soft-quick-absorbent-bamboo-assorted-colours-bath-towel",
                "https://ramrajcotton.in/products/bamboo-cotton-white-shirt-soft-breathable-eco-friendly",
                "https://ramrajcotton.in/products/100-combed-cotton-white-vest-rn-sukra-pack-of-2",
                "https://ramrajcotton.in/products/cotton-premium-soft-feel-white-bath-towel-1046-pack-of-2"
            ]
            target_urls = [normalize_url(u) for u in fallback_list]
            
        print(f"   🎯 Pipeline Armed: Ready to process {len(target_urls)} distinct pages.")

        # Step 2: Loop through product paths
        print("\n🚀 Phase 2: Processing multi-page extraction queue...")
        for idx, url in enumerate(target_urls, 1):
            short_url = url.split('/products/')[-1] if '/products/' in url else "Main-Store"
            print(f"   [{idx}/{len(target_urls)}] Scraping page for: {short_url}")
            
            page_reviews = await scrape_reviews_from_url(page, url)
            for review in page_reviews:
                if review.lower() not in seen:
                    seen.add(review.lower())
                    # FIXED: Added metadata metric column (Review_Length)
                    clean_dataset.append([url, review, len(review)])
            
            await asyncio.sleep(1) 

        # Step 3: Run Official Store page fallback
        print("\n📦 Phase 3: Extracting bonus records from main store reviews...")
        bonus_url = normalize_url('https://ramrajcotton.in/pages/store-reviews')
        bonus_reviews = await scrape_reviews_from_url(page, bonus_url)
        for review in bonus_reviews:
            if review.lower() not in seen:
                seen.add(review.lower())
                clean_dataset.append([bonus_url, review, len(review)])

        await browser.close()

    # --- SAVE SHIELDED DATASET ---
    output_file = 'ramraj_clean_feedback.csv'
    if clean_dataset:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # FIXED: Added structured header label layout
            writer.writerow(['URL', 'Feedback', 'Review_Length'])
            writer.writerows(clean_dataset)
            
        print("\n" + "=" * 70)
        print(f"🎯 SUCCESS! Multi-URL dataset extraction complete.")
        print(f"   Total filtered rows saved: {len(clean_dataset)}")
        print(f"   Output file: {output_file}")
        print("=" * 70)
    else:
        print("\n❌ Dataset empty. Check network or element targets.")

if __name__ == "__main__":
    asyncio.run(main())