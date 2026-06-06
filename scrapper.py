"""
Ramraj Cotton Feedback Extractor - ULTRA CLEAN VERSION
Extracts ONLY meaningful customer feedback sentences
"""

import asyncio
import csv
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Real customer review patterns (what actual feedback looks like)
REVIEW_PATTERNS = [
    r'I am very happy.*?\.',
    r'I am satisfied.*?\.',
    r'I had a very good experience.*?\.',
    r'I have been using.*?\.',
    r'I strongly recommend.*?\.',
    r'I would recommend.*?\.',
    r'The product (is|was).*?\.',
    r'Quality product.*?\.',
    r'Very good product.*?\.',
    r'Excellent quality.*?\.',
    r'Nice cloth.*?\.',
    r'Soft fabric.*?\.',
    r'Perfect fit.*?\.',
    r'Very comfortable.*?\.',
    r'Good quality.*?\.',
    r'Best quality.*?\.',
    r'Thanks.*?Quality Product.*?\.',
    r'Last two years.*?\.',
    r'The product received.*?\.',
    r'Damn good quality.*?\.',
    r'Super quality.*?\.',
    r'Works great.*?\.',
]

def extract_real_reviews(text: str) -> list:
    """Extract only sentences that look like real customer feedback"""
    if not text:
        return []
    
    reviews = []
    
    # Try each pattern
    for pattern in REVIEW_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean up
            clean = re.sub(r'\s+', ' ', match)
            clean = clean.strip()
            if 20 < len(clean) < 300:
                reviews.append(clean)
    
    # Also look for sentences starting with "I" (customer speaking)
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 30 and len(sentence) < 300:
            if sentence[0] == 'I' or sentence[0:3] == 'I ':
                # Filter out garbage
                skip_words = ['review collected', 'store invitation', 'invite', 'thumb', 'verified', 'india']
                if not any(word in sentence.lower() for word in skip_words):
                    clean = re.sub(r'\s+', ' ', sentence)
                    if clean and clean not in reviews:
                        reviews.append(clean)
    
    return reviews

async def extract_from_judgeme(page):
    """Extract clean reviews from Judge.me"""
    print("   Loading Judge.me...")
    await page.goto('https://judge.me/reviews/stores/ramrajcotton.in', wait_until='networkidle', timeout=30000)
    await page.wait_for_timeout(3000)
    
    for _ in range(3):
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(1000)
    
    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')
    
    reviews = []
    
    # Get all text from review divs
    review_divs = soup.find_all('div', class_=re.compile(r'review', re.I))
    
    for div in review_divs:
        text = div.get_text(separator=' ', strip=True)
        extracted = extract_real_reviews(text)
        for rev in extracted:
            if rev not in reviews:
                reviews.append(rev)
    
    # Also get from paragraphs
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text(strip=True)
        extracted = extract_real_reviews(text)
        for rev in extracted:
            if rev not in reviews:
                reviews.append(rev)
    
    return reviews

async def extract_from_ramrajcotton(page):
    """Extract clean reviews from Ramraj Cotton"""
    print("   Loading Ramraj Cotton...")
    await page.goto('https://ramrajcotton.in/pages/store-reviews', wait_until='domcontentloaded', timeout=30000)
    await page.wait_for_timeout(3000)
    
    print("   Scrolling...")
    for i in range(10):
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(1000)
    
    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')
    
    reviews = []
    
    # Get all text
    all_text = soup.get_text(separator=' ', strip=True)
    
    # Extract using patterns
    extracted = extract_real_reviews(all_text)
    for rev in extracted:
        if rev not in reviews:
            reviews.append(rev)
    
    # Also check paragraphs directly
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text(strip=True)
        extracted = extract_real_reviews(text)
        for rev in extracted:
            if rev not in reviews:
                reviews.append(rev)
    
    return reviews

async def main():
    print("="*80)
    print("RAMRAJ COTTON FEEDBACK EXTRACTOR - ULTRA CLEAN VERSION")
    print("="*80)
    print("\n📌 Extracting ONLY real customer feedback sentences\n")
    
    all_feedback = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("📦 Source 1: Judge.me Reviews")
        print("-" * 50)
        judge_reviews = await extract_from_judgeme(page)
        url1 = 'https://judge.me/reviews/stores/ramrajcotton.in'
        for review in judge_reviews:
            all_feedback.append((url1, review))
        print(f"   ✅ {len(judge_reviews)} reviews")
        
        print("\n📦 Source 2: Ramraj Cotton Official")
        print("-" * 50)
        ramraj_reviews = await extract_from_ramrajcotton(page)
        url2 = 'https://ramrajcotton.in/pages/store-reviews'
        for review in ramraj_reviews:
            all_feedback.append((url2, review))
        print(f"   ✅ {len(ramraj_reviews)} reviews")
        
        await browser.close()
    
    # Remove duplicates
    unique_feedback = []
    seen = set()
    for url, fb in all_feedback:
        key = fb.lower().strip()
        if key not in seen:
            seen.add(key)
            unique_feedback.append((url, fb))
    
    # Save to CSV
    csv_filename = 'ramraj_feedback.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Feedback'])
        for url, fb in unique_feedback:
            writer.writerow([url, fb])
    
    print("\n" + "="*80)
    print("✅ EXTRACTION COMPLETE!")
    print(f"   Total real customer reviews: {len(unique_feedback)}")
    print(f"   Saved to: {csv_filename}")
    
    if unique_feedback:
        print("\n📋 CLEAN CUSTOMER REVIEWS:")
        print("-" * 80)
        for i, (url, fb) in enumerate(unique_feedback, 1):
            print(f"\n{i}. {fb}")
            print(f"   Source: {'Judge.me' if 'judge.me' in url else 'Ramraj Cotton'}")
        
        judge_count = sum(1 for url, _ in unique_feedback if 'judge.me' in url)
        ramraj_count = sum(1 for url, _ in unique_feedback if 'ramrajcotton' in url)
        print(f"\n📊 Summary: Judge.me: {judge_count} | Ramraj Cotton: {ramraj_count} | Total: {len(unique_feedback)}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(main())