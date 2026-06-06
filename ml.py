import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

dataset = [

{"feedback": "product not yet arrived", "department": "Dispatch"},
{"feedback": "order not delivered on time", "department": "Dispatch"},
{"feedback": "delivery delay in shipment", "department": "Dispatch"},
{"feedback": "shipment not received", "department": "Dispatch"},
{"feedback": "refund not received", "department": "Accounts"},
{"feedback": "invoice mismatch in billing", "department": "Accounts"},
{"feedback": "payment not updated", "department": "Accounts"},
{"feedback": "carton damaged during transit", "department": "Packaging"},
{"feedback": "package was open on delivery", "department": "Packaging"},
{"feedback": "missing items in box", "department": "Packaging"},
{"feedback": "fabric quality is low", "department": "Manufacturing"},
{"feedback": "color fade after wash", "department": "Manufacturing"},
{"feedback": "stitching defect found", "department": "Manufacturing"},
{"feedback": "size issue in vest", "department": "Product Design"},
{"feedback": "fit is too tight", "department": "Product Design"},
{"feedback": "design not attractive", "department": "Product Design"},
{"feedback": "discount not applied correctly", "department": "Sales"},
{"feedback": "scheme not updated", "department": "Sales"},
{"feedback": "price mismatch in order", "department": "Sales"},
{"feedback": "issue not resolved by support", "department": "Customer Support"},
{"feedback": "no response from support team", "department": "Customer Support"},

]

df = pd.DataFrame(dataset)

X = df["feedback"]
y = df["department"]


vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

model = LogisticRegression()
model.fit(X_train, y_train)

def predict_department(text):
    text_vec = vectorizer.transform([text])
    return model.predict(text_vec)[0]


print("=======================================")
print(" Dealer Feedback ML Classification System ")
print("=======================================\n")

while True:
    feedback = input("Enter feedback: ")

    if feedback.lower() == "exit":
        break

    result = predict_department(feedback)

    print("Department:", result)
