"""
Rule-Based Classification for Ramraj Cotton Feedback
Enter feedback → Get department → Auto-save to CSV
"""

import re
import csv
import os
from datetime import datetime

# Department keywords mapping
DEPARTMENT_RULES = {

    'Manufacturing': {
        'keywords': [
            'fabric quality',
            'stitching',
            'defect',
            'faded',
            'fading',
            'shrank',
            'shrinking',
            'defective',
            'poor quality',
            'color faded',
            'color mismatch',
            'stitching came off',
            'shrank after wash',
            'defective items',
            'fabric damaged',
            'product damaged',
            'material damaged',
            'material quality',
            'fabric is poor',
            'stitching defect',
            'fabric quality is poor',
            'quality issue',
            'color issue',
            'tear in fabric',
            'fabric torn',
            'torn fabric'
        ]
    },

    'Dispatch': {
        'keywords': [
            'delivery',
            'shipped',
            'dispatch',
            'shipping',
            'courier',
            'not delivered',
            'never delivered',
            'never shipped',
            'tracking',
            'late',
            'delayed',
            'order not delivered',
            'product was never shipped',
            'received very late',
            'delay in delivery',
            'delivery delay',
            'shipment',
            'shipment pending',
            'pending shipment',
            'pending delivery',
            'product not yet shipped',
            'yet to receive',
            'not received',
            'order not received'
        ]
    },

    'Packaging': {
        'keywords': [
            'package',
            'packing',
            'carton',
            'torn',
            'damaged package',
            'missing items',
            'wrong product packed',
            'package arrived torn',
            'carton was damaged',
            'missing items in shipment',
            'received wrong product',
            'wrong product received',
            'wrong item sent',
            'wrong item',
            'received wrong item',
            'incorrect product',
            'wrong sku',
            'packing quality',
            'poor packing',
            'poor packaging',
            'carton damaged',
            'box damaged',
            'package damaged',
            'damaged carton',
            'box torn',
            'open package'
        ]
    },

    'Accounts': {
        'keywords': [
            'money',
            'refund',
            'payment',
            'billing',
            'invoice',
            'gst',
            'refund not received',
            'money deducted',
            'invoice incorrect',
            'gst calculation wrong',
            'price differs',
            'money paid',
            'paid but not received',
            'payment updated',
            'billing issue',
            'invoice mismatch',
            'credit note',
            'credit memo',
            'payment pending'
        ]
    },

    'Sales': {
        'keywords': [
            'discount',
            'scheme',
            'offer',
            'quotation',
            'stock',
            'unavailable',
            'discount promised',
            'scheme benefits',
            'offer not applied',
            'stock not supplied',
            'fast moving items unavailable',
            'price high',
            'price issue',
            'cost high',
            'expensive',
            'pricing problem',
            'too expensive',
            'price too high',
            'high price'
        ]
    },

    'Product Design': {
        'keywords': [
            'size',
            'fit',
            'large',
            'small',
            'fitting issue',
            'size too large',
            'size too small',
            'tight fit',
            'loose fit',
            'loose fitting',
            'size chart',
            'measurement',
            'length',
            'width',
            'sizing',
            'size mismatch',
            'fit issue',
            'length mismatch'
        ]
    },

    'Customer Support': {
        'keywords': [
            'response',
            'support',
            'call',
            'answered',
            'unanswered',
            'unresolved',
            'rude',
            'behavior',
            'no response',
            'nobody answers',
            'support team',
            'issue unresolved',
            'staff rude',
            'customer care',
            'no proper response',
            'not responding',
            'support not responding',
            'worst company',
            'worst service',
            'never buying again',
            'avoid this brand',
            'waste of money',
            'total waste'
        ]
    }
}


def keyword_match(text, keyword):
    """Exact phrase / word matching using regex boundaries."""
    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
    return re.search(pattern, text) is not None


def classify_feedback(text):
    """Classify feedback into department based on keyword matching"""
    if not text or len(text.strip()) < 3:
        return "Unclassified"

    text_lower = text.lower()

    # HIGH PRIORITY ACCOUNTS RULES
    accounts_priority = [
        'refund',
        'payment',
        'invoice',
        'billing',
        'gst',
        'credit note',
        'credit memo',
        'money deducted',
        'payment pending'
    ]

    for keyword in accounts_priority:
        if keyword_match(text_lower, keyword):
            return "Accounts"

    # HIGH PRIORITY SALES RULES
    sales_priority = [
        'discount',
        'scheme',
        'offer',
        'quotation',
        'stock'
    ]

    for keyword in sales_priority:
        if keyword_match(text_lower, keyword):
            return "Sales"

    # NORMAL PRIORITY ROUTING
    priority_order = [
        'Product Design',
        'Packaging',
        'Dispatch',
        'Customer Support',
        'Manufacturing'
    ]

    for department in priority_order:
        for keyword in DEPARTMENT_RULES[department]['keywords']:
            if keyword_match(text_lower, keyword):
                return department

    return "Customer Support"


def save_feedback(feedback, department):
    """Save feedback and classified department to CSV file."""
    file_name = "routed_feedback.csv"
    file_exists = os.path.isfile(file_name)

    with open(file_name, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(["Timestamp", "Feedback", "Department"])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, feedback, department])


def main():
    print("=" * 60)
    print("RAMRAJ COTTON - FEEDBACK CLASSIFICATION SYSTEM")
    print("=" * 60)
    print("\nEnter customer feedback to see the routing department.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        feedback = input("Enter feedback: ").strip()

        if feedback.lower() in ['exit', 'quit', 'q']:
            print("\n✅ Exited. Thank you!")
            break

        if not feedback:
            print("Please enter some feedback.\n")
            continue

        department = classify_feedback(feedback)
        
        # Save to CSV
        save_feedback(feedback, department)
        
        print(f"Department: {department}")
        print("✅ Saved to routed_feedback.csv\n")


if __name__ == "__main__":
    main()

