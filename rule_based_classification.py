"""
Rule-Based Classification for Ramraj Cotton Feedback
Routes customer feedback to appropriate departments
"""

import csv
import re

# Department keywords mapping
DEPARTMENT_RULES = {
    'Manufacturing': {
        'keywords': [
            'stitching', 'fabric', 'quality', 'defect', 'tear', 'loose thread',
            'material', 'durable', 'soft', 'comfortable', 'cotton', 'bamboo',
            'innerwears', 'hankey', 'towel', 'vest', 'shirt', 'product quality'
        ],
        'description': 'Product quality, fabric, stitching, material defects'
    },
    
    'Delivery': {
        'keywords': [
            'delivery', 'shipping', 'courier', 'arrived', 'late', 'tracking',
            'received', 'package', 'packed', 'shipped'
        ],
        'description': 'Shipping, delivery time, packaging, courier issues'
    },
    
    'Accounts': {
        'keywords': [
            'refund', 'payment', 'billing', 'money', 'price', 'cost',
            'expensive', 'cheap', 'worth', 'economic', 'reasonable price'
        ],
        'description': 'Pricing, refunds, payments, value for money'
    },
    
    'Sales': {
        'keywords': [
            'size', 'fit', 'small', 'large', 'fitting', 'sizes',
            'recommend', 'wrong product', 'stock', 'available', 'order'
        ],
        'description': 'Size issues, product recommendations, availability'
    },
    
    'Designing': {
        'keywords': [
            'design', 'color', 'colour', 'pattern', 'style', 'look',
            'beautiful', 'vibrant', 'traditional', 'modern', 'colours',
            'designs', 'printed', 'embroidery'
        ],
        'description': 'Design, color, pattern, style, aesthetics'
    }
}

# Garbage keywords to skip (not customer feedback)
GARBAGE_KEYWORDS = [
    'shipped from by', 'prevents spam', 'trusted reviews', 'medals celebrate',
    'company registration number', '© 2026', 'our system prevents'
]

def classify_feedback(text):
    """
    Classify a single feedback into a department using rule-based matching.
    Returns department name or 'General' if no match.
    """
    if not text or len(text) < 5:
        return 'Garbage'
    
    text_lower = text.lower()
    
    # First, check if it's garbage
    for garbage in GARBAGE_KEYWORDS:
        if garbage in text_lower:
            return 'Garbage'
    
    # Check each department's keywords
    for department, rules in DEPARTMENT_RULES.items():
        for keyword in rules['keywords']:
            if keyword in text_lower:
                return department
    
    # If no department matched
    return 'General'

def process_feedback_csv(input_file, output_file):
    """
    Read feedback CSV, classify each feedback, and save with department column
    """
    classified_results = []
    department_counts = {}
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        
        # Try to detect if header exists
        first_row = next(reader)
        if first_row[0].lower() == 'url' and first_row[1].lower() == 'feedback':
            header = first_row
        else:
            # No header, first row is data
            header = ['URL', 'Feedback']
            # Process the first row as data
            feedback_text = first_row[1] if len(first_row) > 1 else first_row[0]
            department = classify_feedback(feedback_text)
            classified_results.append(['', feedback_text, department])
            department_counts[department] = department_counts.get(department, 0) + 1
        
        # Process remaining rows
        for row in reader:
            if len(row) >= 2:
                url = row[0]
                feedback = row[1]
            elif len(row) == 1:
                url = ''
                feedback = row[0]
            else:
                continue
            
            department = classify_feedback(feedback)
            classified_results.append([url, feedback, department])
            department_counts[department] = department_counts.get(department, 0) + 1
    
    # Save to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['URL', 'Feedback', 'Department'])
        writer.writerows(classified_results)
    
    return department_counts, len(classified_results)

def display_summary(department_counts, total_count):
    """Print a summary of classification results"""
    print("\n" + "="*70)
    print("CLASSIFICATION SUMMARY")
    print("="*70)
    print(f"\nTotal feedback processed: {total_count}")
    print("\nDepartment Distribution:")
    print("-" * 40)
    
    for department, count in sorted(department_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_count) * 100
        bar = '█' * int(percentage)
        print(f"  {department:<15}: {count:>3} ({percentage:>5.1f}%) {bar}")
    
    print("\n" + "="*70)

def main():
    # File paths
    input_file = 'ramraj_clean_feedback.csv'  # Your input CSV file
    output_file = 'routed_feedback.csv'  # Output with department column
    
    print("="*70)
    print("RAMRAJ COTTON - RULE-BASED CLASSIFICATION SYSTEM")
    print("="*70)
    print("\n📌 Loading feedback data...")
    
    try:
        # Process the CSV file
        department_counts, total = process_feedback_csv(input_file, output_file)
        
        print(f"✅ Processed {total} feedback entries")
        print(f"✅ Saved classified results to: {output_file}")
        
        # Display summary
        display_summary(department_counts, total)
        
        # Show sample of routed feedback
        print("\n📋 SAMPLE OF ROUTED FEEDBACK:")
        print("-" * 70)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for i, row in enumerate(reader):
                if i >= 10:  # Show first 10 samples
                    break
                if len(row) >= 3:
                    feedback = row[1][:80] + "..." if len(row[1]) > 80 else row[1]
                    print(f"  [{row[2]}] {feedback}")
        
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found!")
        print("   Please make sure ramraj_feedback.csv exists in the current directory.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()