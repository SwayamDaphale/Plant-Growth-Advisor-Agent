Perfect 👍 — your README is already very clean.
Since you want to include **instructions for Google Gemini API key setup** (because your project uses Gemini for recommendations), here’s how you can extend the documentation.

Below is the **modified README.md** with an additional **🔑 API Key Setup** section that explains how to generate and configure the Gemini API key.

---

```markdown
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
* 💬 **Optional LLM (Google Gemini) support** for enhanced recommendations
* 🖥️ **Web-based Interface** – HTML + Flask integration

---

## 🏗️ Project Structure

```

tree\_advisor/
│── main.py              # Core AI model and decision logic
│── web.py               # Flask web server for user interaction
│── tree\_advisor.py      # Model wrapper for Flask integration
│── .env                 # Stores your Gemini API key (do not commit to GitHub)
│── templates/
│   ├── index.html       # Frontend UI for user input
│   └── agriinfo.html    # Results display page
│── static/
│   └── style.css        # (Optional) Styling for frontend
│── requirements.txt     # Required dependencies
│── README.md            # Project documentation

````

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/tree-advisor.git
cd tree-advisor
````

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

---

## 🔑 Gemini API Key Setup

This project optionally integrates with **Google Gemini** for enhanced recommendations.
The API key provided may expire — you’ll need to generate your own.

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)

2. Sign in with your Google account.

3. Click **Create API key** (free tier available).

4. Copy the key generated.

5. In your project folder, create a file named **`.env`** (at the root level).

6. Add the following line inside `.env`:

   ```
   GOOGLE_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-2.0-flash
   ```

7. The app will automatically read the key from `.env`.

⚠️ **Note:** Keep `.env` out of GitHub (it’s already in `.gitignore`).

---

## ▶️ Running the Application

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
* **Temperature**: e.g., `25` (Celsius)
* **Land Size**: e.g., `200`, `2ac`, `1ha`
* **Purpose**: `Personal` or `Commercial`

---

## ✅ Example Usage

### Input:

```
Tree: Mango
Soil Type: lal mati
Region: Maharashtra
Rainfall: 1200
Temperature: 26
Purpose: Commercial
Land Size: 2ac
```

### Output:

```
Priority: High
Suitability: Yes
Reason: Lal mati soil with 1200 mm rainfall and pH ~6.5 is ideal for Mango.

Recommendations:
• Prepare land (clear weeds, loosen soil)
• Plant during rainy season
• Use mulch and monitor irrigation for 6 months

Commercial advice:
For commercial use, plan irrigation, adopt spacing for high yield, and research markets.
```

---

## 🔮 Future Enhancements

* Integration with **real-time weather APIs** for dynamic rainfall/pH updates
* **ChatGPT-style Q\&A** for user interaction
* Mobile-friendly **Flutter-based UI** for easier access
* Integration with **Firebase** for data storage

---

## 👨‍💻 Tech Stack

* **Python (Flask)** – Backend AI model
* **HTML/CSS** – User Interface
* **APIs** – Soil & Rainfall Data + Google Gemini
* **NLP Preprocessing** – Handle regional language inputs

---

## 📜 License

This project is licensed under the **MIT License** – free to use and modify.

```

---

✅ With this addition, anyone cloning your repo will know exactly how to **generate their own Gemini API key** and plug it into the project.  

Do you also want me to add a **fallback note** in README (saying that if no API key is provided, the project will still run using the rule-based system)?
```
