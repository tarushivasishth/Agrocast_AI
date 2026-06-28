const API_URL = "http://127.0.0.1:8000"; // FastAPI backend URL

// Tabs
const tabBtns = document.querySelectorAll(".tabBtn");
const tabContents = document.querySelectorAll(".tabContent");

tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        tabBtns.forEach(b => b.classList.replace("bg-green-600", "bg-gray-200"));
        tabBtns.forEach(b => b.classList.replace("text-white", "text-gray-800"));
        btn.classList.replace("bg-gray-200", "bg-green-600");
        btn.classList.replace("text-gray-800", "text-white");

        tabContents.forEach(c => c.classList.add("hidden"));
        document.getElementById(btn.dataset.tab).classList.remove("hidden");
    });
});

// Elements
const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("preview");
const predictBtn = document.getElementById("predictBtn");
const predictionResult = document.getElementById("predictionResult");
const diseaseNameEl = document.getElementById("diseaseName");
const confidenceEl = document.getElementById("confidence");

const adviceBtn = document.getElementById("adviceBtn");
const adviceResult = document.getElementById("adviceResult");
const adviceText = document.getElementById("adviceText");
const docsList = document.getElementById("docsList");

const historyList = document.getElementById("historyList");

let predictionHistory = [];

// Preview image
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
        preview.src = reader.result;
        preview.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
});

// Predict disease
predictBtn.addEventListener("click", async () => {
    if (!fileInput.files.length) {
        alert("Please select an image!");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    predictionResult.classList.add("hidden");
    diseaseNameEl.textContent = "Loading...";
    confidenceEl.textContent = "";

    try {
        const response = await fetch(`${API_URL}/predict`, { method: "POST", body: formData });
        if (!response.ok) throw new Error("Prediction failed");

        const data = await response.json();
        diseaseNameEl.textContent = data.disease_name;
        confidenceEl.textContent = `Confidence: ${(data.confidence).toFixed(2)}%`;
        predictionResult.classList.remove("hidden");

        // Save history
        predictionHistory.unshift({
            disease_name: data.disease_name,
            confidence: (data.confidence ).toFixed(2),
            timestamp: new Date().toLocaleString()
        });
        renderHistory();

        // Switch to advice tab automatically
        // document.querySelector('[data-tab="adviceTab"]').click();

         // Automatically switch to advice tab after short delay
        setTimeout(() => {
            document.querySelector('[data-tab="adviceTab"]').click();
        }, 5000); // 1 second delay (adjust if needed)

    } catch (err) {
        alert("Error: " + err.message);
    }
});

// Get advice
adviceBtn.addEventListener("click", async () => {
    const disease_name = diseaseNameEl.textContent;
    if (!disease_name) return;

    adviceText.innerHTML = "Fetching advice...";  // use innerHTML
    docsList.innerHTML = "";
    adviceResult.classList.remove("hidden");

    try {
        const response = await fetch(`${API_URL}/get_advice/${disease_name}`);
        if (!response.ok) throw new Error("Failed to get advice");

        const data = await response.json();
        adviceText.innerHTML = data.advice; // render HTML, including <br> tags

        docsList.innerHTML = "";
        data.retrieved_docs.forEach(doc => {
            const li = document.createElement("li");
            li.innerHTML = `<a href="${doc.url}" target="_blank" class="text-blue-600 hover:underline">${doc.crop} - ${doc.disease}</a> (distance: ${doc.distance.toFixed(2)})`;
            docsList.appendChild(li);
        });
    } catch (err) {
        adviceText.innerHTML = "Error: " + err.message; // use innerHTML here too
    }
});


// Render prediction history
function renderHistory() {
    historyList.innerHTML = "";
    predictionHistory.forEach(item => {
        const li = document.createElement("li");
        li.className = "bg-green-100 rounded-lg p-3 shadow hover:bg-green-200 transition";
        li.innerHTML = `<span class="font-bold">${item.disease_name}</span> - Confidence: ${item.confidence}% <br><span class="text-gray-600 text-sm">${item.timestamp}</span>`;
        historyList.appendChild(li);
    });
}
