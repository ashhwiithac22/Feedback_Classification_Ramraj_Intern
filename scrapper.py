"""
Ramraj Cotton Feedback Extractor - WORKING VERSION
Extracts actual customer review text from Judge.me
"""

import asyncio
import csv
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

def is_real_review(text: str) -> bool:
    """Check if text is actual customer review content."""
    if not text or len(text) < 20:
        return False
    
    text_lower = text.lower()
    
    # Skip UI elements and boilerplate (fixed regex patterns)
    skip_patterns = [
        'write a review', 
        'visit store', 
        'rating', 
        'rated .* stars',
        'picture/video', 
        'name \(displayed publicly', 
        'anonymous',
        'store published', 
        'based on .* reviews', 
        'filter by', 
        'sort by',
        'review collected from', 
        'review collected organically',
        'thumb_up', 
        'thumb_down', 
        'read more', 
        'show less',
        'verified', 
        'store info',
        'products',
        'customer photos'
    ]
    
    for pattern in skip_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False
    
    # Must contain review indicators (actual customer feedback)
    review_indicators = [
        'good', 'nice', 'quality', 'soft', 'great', 'excellent', 'best', 
        'love', 'happy', 'satisfied', 'recommend', 'comfortable', 'durable', 
        'perfect', 'awesome', 'bad', 'poor', 'issue', 'problem', 'disappointed',
        'product', 'fit', 'price', 'worth', 'delivery', 'service', 'using',
        'experience', 'satisfied', 'wonderful', 'amazing'
    ]
    
    return any(indicator in text_lower for indicator in review_indicators)

async def extract_all_from_judgeme(page):
    """Extract ONLY real customer reviews from Judge.me."""
    print("   Loading Judge.me page...")
    await page.goto('https://judge.me/reviews/stores/ramrajcotton.in', wait_until='networkidle', timeout=30000)
    
    await page.wait_for_timeout(5000)
    
    # Scroll to load all reviews
    print("   Scrolling to load ALL reviews...")
    last_height = 0
    scroll_count = 0
    
    for _ in range(15):  # Max 15 scrolls
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(2000)
        
        new_height = await page.evaluate('document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
        scroll_count += 1
    
    print(f"   Completed {scroll_count} scrolls")
    
    # Get page content
    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')
    
    feedbacks = []
    
    # Method 1: Look for review content divs
    review_contents = soup.find_all('div', class_=re.compile(r'review__content|review-content|review-text', re.I))
    print(f"   Found {len(review_contents)} review content containers")
    
    for container in review_contents:
        # Get text from paragraphs inside
        paragraphs = container.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if is_real_review(text):
                text = re.sub(r'\s+', ' ', text)
                if text and text not in feedbacks:
                    feedbacks.append(text)
    
    # Method 2: Look for review blocks
    if len(feedbacks) == 0:
        print("   Trying alternative selectors...")
        review_blocks = soup.find_all('div', class_=re.compile(r'review', re.I))
        
        for block in review_blocks:
            # Look for paragraph text
            text_elem = block.find('p')
            if text_elem:
                text = text_elem.get_text(strip=True)
                if is_real_review(text):
                    text = re.sub(r'\s+', ' ', text)
                    if text not in feedbacks:
                        feedbacks.append(text)
    
    # Method 3: Get all paragraphs that look like reviews
    if len(feedbacks) < 10:
        print("   Extracting from all paragraphs...")
        all_paragraphs = soup.find_all('p')
        
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if is_real_review(text) and len(text) > 30:
                text = re.sub(r'\s+', ' ', text)
                if text not in feedbacks:
                    feedbacks.append(text)
    
    return feedbacks

async def extract_all_from_ramrajcotton(page):
    """Extract reviews from Ramraj Cotton official site."""
    print("   Loading Ramraj Cotton reviews page...")
    
    try:
        await page.goto('https://ramrajcotton.in/pages/store-reviews', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(5000)
        
        # Scroll a few times
        for i in range(3):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(1500)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        feedbacks = []
        
        # Get all text and split into lines
        page_text = soup.get_text(separator='\n', strip=True)
        lines = page_text.split('\n')
        
        # Look for review-like lines
        review_patterns = [
            r'(?i)(quality|good|nice|great|excellent|best|love|happy|satisfied)',
            r'(?i)(comfortable|durable|perfect|awesome|wonderful)',
            r'I (am|have|had|will)',
            r'Very good',
            r'Best quality',
            r'Really good'
        ]
        
        for line in lines:
            line = line.strip()
            if 30 < len(line) < 500:
                # Check if it matches any review pattern
                for pattern in review_patterns:
                    if re.search(pattern, line):
                        # Clean up the line
                        line = re.sub(r'\d+%\(\d+\)', '', line)
                        line = re.sub(r'R\d+%', '', line)
                        line = re.sub(r'\(Pack of \d+\)', '', line)
                        line = re.sub(r'\s+', ' ', line)
                        
                        if line and line not in feedbacks:
                            feedbacks.append(line)
                        break
        
        return feedbacks[:50]  # Limit to 50 reviews
        
    except Exception as e:
        print(f"   Error: {str(e)[:100]}")
        return []

async def main():
    print("="*70)
    print("RAMRAJ COTTON FEEDBACK EXTRACTOR - WORKING VERSION")
    print("="*70)
    
    all_feedback = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to False to see what's happening
        page = await browser.new_page()
        
        # Source 1: Judge.me
        print("\n📦 Source 1: Judge.me Reviews")
        print("-" * 50)
        judge_feedback = await extract_all_from_judgeme(page)
        url1 = 'https://judge.me/reviews/stores/ramrajcotton.in'
        for fb in judge_feedback:
            all_feedback.append((url1, fb))
        print(f"   ✅ Extracted {len(judge_feedback)} real customer reviews")
        
        # Display sample from Judge.me
        if judge_feedback:
            print("\n   Sample reviews from Judge.me:")
            for i, fb in enumerate(judge_feedback[:3], 1):
                print(f"   {i}. {fb[:100]}...")
        
        # Source 2: Ramraj Cotton Official
        print("\n📦 Source 2: Ramraj Cotton Official Store Reviews")
        print("-" * 50)
        ramraj_feedback = await extract_all_from_ramrajcotton(page)
        url2 = 'https://ramrajcotton.in/pages/store-reviews'
        for fb in ramraj_feedback:
            all_feedback.append((url2, fb))
        print(f"   ✅ Extracted {len(ramraj_feedback)} real customer reviews")
        
        await browser.close()
    
    # Remove duplicates
    unique_feedback = []
    seen = set()
    for url, fb in all_feedback:
        if fb not in seen:
            seen.add(fb)
            unique_feedback.append((url, fb))
    
    # Save to CSV - ONLY 2 COLUMNS
    csv_filename = 'ramraj_feedback.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Feedback'])
        for url, fb in unique_feedback:
            writer.writerow([url, fb])
    
    print("\n" + "="*70)
    print("✅ EXTRACTION COMPLETE!")
    print(f"   Total real customer reviews extracted: {len(unique_feedback)}")
    print(f"   Data saved to: {csv_filename}")
    
    if unique_feedback:
        print("\n📋 ALL EXTRACTED REVIEWS:")
        print("-"*70)
        for i, (url, fb) in enumerate(unique_feedback, 1):
            print(f"\n{i}. URL: {url.split('/')[2]}")
            print(f"   Review: {fb}")
    else:
        print("\n⚠️ No reviews extracted. Let me try a different approach...")
        
        # Fallback: Direct text extraction
        print("\n   Attempting fallback extraction...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://judge.me/reviews/stores/ramrajcotton.in', wait_until='networkidle')
            await page.wait_for_timeout(5000)
            
            # Get all visible text
            visible_text = await page.evaluate('document.body.innerText')
            lines = visible_text.split('\n')
            
            fallback_feedback = []
            for line in lines:
                line = line.strip()
                if 40 < len(line) < 300:
                    # Check if it's a review (starts with name pattern or has review words)
                    if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+\.?', line) or \
                       any(word in line.lower() for word in ['quality', 'good', 'nice', 'great', 'excellent', 'product']):
                        if not any(skip in line.lower() for skip in ['verified', 'india', 'read more', 'thumb']):
                            fallback_feedback.append(line)
            
            await browser.close()
            
            # Save fallback results
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Feedback'])
                for fb in fallback_feedback[:20]:
                    writer.writerow(['https://judge.me/reviews/stores/ramrajcotton.in', fb])
            
            print(f"   Fallback extracted {len(fallback_feedback)} reviews")
            print(f"   Saved to {csv_filename}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(main())