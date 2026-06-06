class FeedbackClassifier:

    def classify(self, text):
        text = text.lower()

        # -------------------------------
        # 1. DISPATCH (delivery issues FIRST priority)
        # -------------------------------
        if any(word in text for word in [
            "not yet arrived", "not delivered", "delivery", "delay",
            "shipping", "dispatch", "transport", "courier", "not received"
        ]):
            return "Dispatch"

        # -------------------------------
        # 2. ACCOUNTS (money-related ONLY)
        # -------------------------------
        elif any(word in text for word in [
            "refund", "payment", "invoice mismatch", "credit note",
            "money not received", "gst", "bill issue"
        ]):
            return "Accounts"

        # -------------------------------
        # 3. PACKAGING (carton / box issues)
        # -------------------------------
        elif any(word in text for word in [
            "carton damaged", "package damaged", "box damaged",
            "missing items", "wrong sku", "packing issue"
        ]):
            return "Packaging"

        # -------------------------------
        # 4. MANUFACTURING (quality issues)
        # -------------------------------
        elif any(word in text for word in [
            "quality", "fabric", "color fade", "stitching",
            "defect", "shrink", "rough"
        ]):
            return "Manufacturing"

        # -------------------------------
        # 5. PRODUCT DESIGN (fit/size/design issues)
        # -------------------------------
        elif any(word in text for word in [
            "size", "fit", "design", "tight", "loose"
        ]):
            return "Product Design"

        # -------------------------------
        # 6. SALES (pricing / scheme / order)
        # -------------------------------
        elif any(word in text for word in [
            "order", "discount", "scheme", "price", "offer"
        ]):
            return "Sales"

        # -------------------------------
        # 7. DEFAULT
        # -------------------------------
        else:
            return "Customer Support"


# ---------------- MAIN PROGRAM ----------------

if __name__ == "__main__":

    clf = FeedbackClassifier()

    print("=======================================")
    print(" Dealer Feedback Classification System ")
    print("=======================================\n")

    while True:
        feedback = input("Enter feedback: ")

        if feedback.lower() == "exit":
            break

        result = clf.classify(feedback)

        print("Department:", result)
        print("----------------------\n")