const API_BASE = "http://127.0.0.1:8000";

const searchForm = document.getElementById("searchForm");
const searchType = document.getElementById("searchType");
const searchInput = document.getElementById("searchInput");
const results = document.getElementById("results");

const historyButton = document.getElementById("historyButton");
const historyResults = document.getElementById("historyResults");

// Display a value safely as text
function formatValue(value) {
    if (Array.isArray(value)) {
        return value.length ? value.join(", ") : "Not available";
    }

    return value || "Not available";
}

// Create a heading
function createHeading(text) {
    const heading = document.createElement("h3");
    heading.textContent = text;
    return heading;
}

// Display drug search results
function displayDrug(drug) {
    const card = document.createElement("div");
    card.className = "result-card";

    const fda = drug.openfda || {};

    card.appendChild(createHeading(
        formatValue(fda.brand_name?.[0] || fda.generic_name?.[0])
    ));

    const details = [
        ["Generic name", fda.generic_name],
        ["Manufacturer", fda.manufacturer_name],
        ["Purpose", drug.purpose],
        ["Indications", drug.indications_and_usage],
        ["Warnings", drug.warnings]
    ];

    details.forEach(([label, value]) => {
        const paragraph = document.createElement("p");
        paragraph.textContent = `${label}: ${formatValue(value)}`;
        card.appendChild(paragraph);
    });

    results.appendChild(card);
}

// Display clinical trial results
function displayTrial(trial) {
    const card = document.createElement("div");
    card.className = "result-card";

    card.appendChild(createHeading(
        trial.title || "Clinical Trial"
    ));

    const id = document.createElement("p");
    id.textContent = `Trial ID: ${trial.trial_id || "Not available"}`;
    card.appendChild(id);

    const source = document.createElement("p");
    source.textContent = `Source: ${trial.source || "ClinicalTrials.gov"}`;
    card.appendChild(source);

    if (trial.url) {
        const link = document.createElement("a");
        link.href = trial.url;
        link.textContent = "View Clinical Trial";
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        card.appendChild(link);
    }

    results.appendChild(card);
}

// Search drugs or clinical trials
searchForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const type = searchType.value;
    const value = searchInput.value.trim();

    if (!value) {
    results.textContent = "Please enter a drug name or clinical trial keyword.";
    searchInput.focus();
    return;
}

if (value.length < 2) {
    results.textContent = "Please enter at least 2 characters.";
    searchInput.focus();
    return;
}

if (value.length > 100) {
    results.textContent = "Search term must not exceed 100 characters.";
    searchInput.focus();
    return;
}

    results.textContent = "Searching...";

    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                search_type: type,
                search_value: value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Search failed");
        }

        results.replaceChildren();

        if (!data.results || data.results.length === 0) {
            results.textContent = "No results found.";
        } else {
            data.results.forEach((item) => {
                if (type === "drug") {
                    displayDrug(item);
                } else {
                    displayTrial(item);
                }
            });
        }

        // Refresh saved search history
        await loadHistory();

    } catch (error) {
    results.textContent =
        "Unable to complete your search. Please check that the backend server is running and try again.";
    console.error("Search error:", error);
}
});

// Load search history
async function loadHistory() {
    if (!historyResults) return;

    historyResults.textContent = "Loading search history...";

    try {
        const response = await fetch(`${API_BASE}/history`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Could not load history");
        }

        historyResults.replaceChildren();

        if (!data.history || data.history.length === 0) {
            historyResults.textContent = "No search history available.";
            return;
        }

        data.history.forEach((entry) => {
            const card = document.createElement("div");
            card.className = "history-card";

            const heading = createHeading(
                `${entry.search_type.toUpperCase()}: ${entry.search_value}`
            );

            const date = document.createElement("p");
            date.textContent = `Searched at: ${entry.searched_at}`;

            const referencesButton = document.createElement("button");
            referencesButton.textContent = "View References";

            const referenceArea = document.createElement("div");

            referencesButton.addEventListener("click", () => {
                loadReferences(entry.id, referenceArea);
            });

            card.appendChild(heading);
            card.appendChild(date);
            card.appendChild(referencesButton);
            card.appendChild(referenceArea);

            historyResults.appendChild(card);
        });

    } catch (error) {
        historyResults.textContent = `History error: ${error.message}`;
    }
}

// Load references for one saved search
async function loadReferences(searchId, target) {
    target.textContent = "Loading references...";

    try {
        const response = await fetch(
            `${API_BASE}/references/${searchId}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Could not load references");
        }

        target.replaceChildren();

        if (!data.references || data.references.length === 0) {
            target.textContent = "No references saved for this search.";
            return;
        }

        data.references.forEach((reference) => {
            const card = document.createElement("div");
            card.className = "reference-card";

            const heading = createHeading(reference.source_name);

            const link = document.createElement("a");
            link.href = reference.reference_url;
            link.textContent = "Open source";
            link.target = "_blank";
            link.rel = "noopener noreferrer";

            const status = document.createElement("p");
            status.textContent =
                `Verification status: ${reference.verification_status}`;

            card.appendChild(heading);
            card.appendChild(link);
            card.appendChild(status);

            ["pending", "verified", "rejected"].forEach((newStatus) => {
                const button = document.createElement("button");
                button.textContent = `Mark ${newStatus}`;

                button.addEventListener("click", () => {
                    updateVerification(
                        reference.id,
                        newStatus,
                        searchId,
                        target
                    );
                });

                card.appendChild(button);
            });

            target.appendChild(card);
        });

    } catch (error) {
        target.textContent = `Reference error: ${error.message}`;
    }
}

// Update a reference's manual verification status
async function updateVerification(referenceId, status, searchId, target) {
    try {
        const response = await fetch(
            `${API_BASE}/references/${referenceId}/verification`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ status })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Could not update status");
        }

        await loadReferences(searchId, target);

    } catch (error) {
        target.textContent = `Update error: ${error.message}`;
    }
}

// View search history when the button is clicked
if (historyButton) {
    historyButton.addEventListener("click", loadHistory);
}