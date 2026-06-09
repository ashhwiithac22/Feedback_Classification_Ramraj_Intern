"""
Ramraj Cotton - Feedback Classification Web Interface
Same classification logic as command-line version - NO WARNINGS
"""

import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import os
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings('ignore')
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Ramraj Cotton Feedback Classifier",
    page_icon="🏭",
    layout="centered"
)

# ============================================
# LOAD MODEL (Cached for performance)
# ============================================
@st.cache_resource
def load_model():
    """Load the sentence transformer model once"""
    with st.spinner("Loading AI model... Please wait (first time only)..."):
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

@st.cache_resource
def create_embeddings():
    """Create department embeddings once - SAME as command line version"""
    department_examples = {
        'Manufacturing': [
            "stitching came undone",
            "fabric quality is poor",
            "color faded after wash",
            "product developed a hole",
            "material feels cheap",
            "shirt shrank after washing",
            "defective product received",
            "tear in the cloth",
            "button fell off",
            "button came off"
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
    
    model = load_model()
    dept_embeddings = {}
    for dept, examples in department_examples.items():
        dept_embeddings[dept] = model.encode(examples)
    
    return dept_embeddings, model

def classify_feedback(feedback, dept_embeddings, model):
    """Classify feedback to department - SAME logic as command line version"""
    if not feedback or len(feedback.strip()) < 3:
        return None
    
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

# ============================================
# LOAD MODEL AND EMBEDDINGS
# ============================================
st.write("### 🔄 Loading AI Model...")
dept_embeddings, model = create_embeddings()
st.success("✅ AI Model Ready!")

# ============================================
# MAIN UI
# ============================================

st.title("🏭 Ramraj Cotton")
st.markdown("### Feedback Routing System")

st.markdown("---")

# Department list
st.markdown("**Departments:** Manufacturing | Dispatch | Packaging | Accounts | Sales | Product Design | Customer Support")

st.markdown("---")

# Input section
st.markdown("**Enter customer feedback:**")

# FIXED: Added a proper label and hid it
feedback = st.text_area("Feedback", height=100, label_visibility="collapsed", placeholder="Type or paste feedback here...")

# Buttons
col1, col2 = st.columns(2)

with col1:
    route_button = st.button("🚀 Route Feedback", type="primary", use_container_width=True)

with col2:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

# Clear button
if clear_button:
    feedback = ""
    st.rerun()

# Classification
if route_button and feedback:
    with st.spinner("Analyzing..."):
        department = classify_feedback(feedback, dept_embeddings, model)
        if department:
            st.markdown("---")
            st.markdown(f"### Department: {department}")
            st.markdown(f"**Feedback:** {feedback}")
        else:
            st.error("Please enter valid feedback")
elif route_button and not feedback:
    st.warning("Please enter some feedback")

st.markdown("---")
st.markdown("*Powered by Sentence Transformers | Ramraj Cotton*")