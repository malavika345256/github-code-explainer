
const API_URL = "http://127.0.0.1:8001/explain";

async function analyzeRepository() {
    const repoInput = document.getElementById("repoUrl");
    const button = document.getElementById("analyzeBtn");
    const status = document.getElementById("status");
    const result = document.getElementById("result");
    const explanation = document.getElementById("explanation");

    const repoUrl = repoInput.value.trim();

    if (!repoUrl) {
        status.textContent = "Please enter a GitHub repository URL.";
        return;
    }

    if (!repoUrl.startsWith("https://github.com/")) {
        status.textContent = "Please enter a valid GitHub repository URL.";
        return;
    }

    button.disabled = true;
    button.textContent = "Analyzing repository...";
    status.textContent = "Connecting to the backend and analyzing code...";
    result.hidden = true;
    explanation.textContent = "";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                repo_url: repoUrl
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || `Server error: ${response.status}`
            );
        }

        if (data.success === false) {
            throw new Error(data.detail || "Repository analysis failed.");
        }

        explanation.textContent =
            data.explanation || data.detail || JSON.stringify(data, null, 2);

        result.hidden = false;
        status.textContent = "Analysis completed successfully!";

    } catch (error) {
        console.error("Repository analysis error:", error);

        status.textContent =
            "Error: " + error.message +
            ". Check the backend terminal for details.";

    } finally {
        button.disabled = false;
        button.textContent = "🚀 Analyze Repository";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("analyzeBtn");

    if (button) {
        button.addEventListener("click", analyzeRepository);
    }
});
