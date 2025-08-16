# Plant-Growth-Advisor-Agent

# 🌱 Tree Advisor – Intelligent Crop Recommendation System

## 📌 Overview

Tree Advisor is an AI-powered recommendation system that helps farmers, gardeners, and agricultural researchers decide whether a specific crop/tree can be harvested successfully under given conditions. The system considers **soil type, region-based pH values, and rainfall patterns** to provide an accurate harvesting decision.

This project integrates **Machine Learning, rule-based decision models, and external APIs** to fetch soil/rainfall data for unknown regions. It also supports multilingual inputs (e.g., Marathi in English letters like *lal mati*, *raktmati*, etc.), making it more user-friendly for local farmers.

---

## 🚀 Features

* 🌍 **Region-based pH estimation** (automatically fetches pH if not provided)
* ☔ **Rainfall support** (accepts both general inputs like *low*, *moderate*, *high* or numerical mm values)
* 🌾 **Soil type mapping** (supports terms like *lal mati*, *sandy*, *black soil*, etc.)
* ✅ **Harvesting decision output** (Yes/No with reasoning)
* 💬 **Optional ChatGPT-like extension** (future enhancement – users can ask follow-up agricultural queries)
* 🖥️ **Web-based Interface** – HTML + Flask integration

---

## 🏗️ Project Structure

```
tree_advisor/
│── main.py              # Core AI model and decision logic
│── web.py               # Flask web server for user interaction
│── templates/
│   └── index.html       # Frontend UI for user input
│── static/
│   └── style.css        # (Optional) Styling for frontend
│── requirements.txt     # Required dependencies
│── README.md            # Project documentation
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/tree-advisor.git
cd tree-advisor
```

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
python web.py
```

Then open **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)** in your browser.

---

## 📊 Input Parameters

* **Tree Name**: e.g., `Mango`, `Coconut`, `Banana`
* **Soil Type**: e.g., `lal mati`, `sandy`, `black soil`
* **Region**: e.g., `Maharashtra`, `Kerala`, `California`
* **Rainfall**: `low`, `moderate`, `high` OR numeric mm value

---

## ✅ Example Usage

### Input:

```
Tree: Mango
Soil Type: lal mati
Region: Maharashtra
Rainfall: 1200
```

### Output:

```
🌱 Recommendation: Suitable for Harvesting ✅
Reason: Lal mati soil with 1200 mm rainfall and pH ~6.5 is ideal for Mango.
```

---

## 🔮 Future Enhancements

* Integration with **real-time weather APIs** for dynamic rainfall/pH updates
* **ChatGPT-style Q\&A** for user interaction (farmers can ask agricultural questions)
* Mobile-friendly **Flutter-based UI** for easier access
* Integration with **Firebase** for data storage

---

## 👨‍💻 Tech Stack

* **Python (Flask)** – Backend AI model
* **HTML/CSS** – User Interface
* **APIs** – Soil & Rainfall Data
* **NLP Preprocessing** – Handle regional language inputs

---

## 📜 License

This project is licensed under the **MIT License** – free to use and modify.

---
