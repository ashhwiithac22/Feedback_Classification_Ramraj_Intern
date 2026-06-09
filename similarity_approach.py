"""
Ramraj Cotton - Similarity-Based Feedback Classification
Enter feedback, get department - No confidence scores printed
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

# Load model (downloads once, takes ~30 seconds first time)
print("Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Ready!\n")

# Department examples (semantic meaning, not exact keywords)
department_examples = {
    'Manufacturing': [
        "stitching came undone",
        "fabric quality is poor",
        "color faded after wash",
        "product developed a hole",
        "material feels cheap",
        "shirt shrank after washing",
        "defective product received",
        "tear in the cloth"
    ],
    
    'Dispatch': [
        "order not delivered",
        "product never shipped",
        "delivery delayed",
        "tracking not working",
        "courier lost package",
        "received very late",
        "shipment pending",
        "OTP",
        "delivery OTP"
    ],
    
    'Packaging': [
        "carton damaged",
        "package arrived torn",
        "missing items",
        "wrong product packed",
        "box was open",
        "poor packaging",
        "received wrong item",
        "seal broken",
        "used item",
        "plastic cover",
        "cover damaged",
        "someone else's order"
    ],
    
    'Accounts': [
        "refund not received",
        "money deducted no order",
        "invoice incorrect",
        "gst calculation wrong",
        "payment failed",
        "billing issue",
        "amount charged twice"
    ],
    
    'Sales': [
        "discount not given",
        "scheme benefits missing",
        "offer not applied",
        "price too high",
        "stock not available",
        "quotation mismatch"
    ],
    
    'Product Design': [
        "size too large",
        "size too small",
        "fitting issue",
        "length too long",
        "tight fit",
        "loose fit",
        "size mismatch",
        "fits like tent",
        "loose stomach",
        "large size"
    ],
    
    'Customer Support': [
        "no response from support",
        "nobody answers call",
        "issue unresolved",
        "staff rude",
        "customer care not responding",
        "complaint not addressed",
        "automated replies",
        "no human response"
    ]
}

# Convert examples to embeddings
dept_embeddings = {}
for dept, examples in department_examples.items():
    dept_embeddings[dept] = model.encode(examples)

def classify_feedback(feedback):
    """Classify feedback to department"""
    feedback_emb = model.encode([feedback])
    
    best_dept = None
    best_score = -1
    
    for dept, examples_emb in dept_embeddings.items():
        similarities = cosine_similarity(feedback_emb, examples_emb)[0]
        max_sim = similarities.max()
        
        if max_sim > best_score:
            best_score = max_sim
            best_dept = dept
    
    return best_dept

# Main loop
print("="*50)
print("RAMRAJ COTTON - FEEDBACK ROUTING SYSTEM")
print("="*50)
print("\nEnter customer feedback. Type 'exit' to stop.\n")

while True:
    feedback = input("Enter feedback: ").strip()
    
    if feedback.lower() in ['exit', 'quit', 'q']:
        print("\nExited. Thank you!")
        break
    
    if not feedback:
        continue
    
    department = classify_feedback(feedback)
    print(f"Department: {department}\n")