async function loadFragments() {
    try {
        const response = await fetch("https://vranc.github.io/db/fragments.json");
        if (!response.ok) {
            throw new Error("Failed to load fragments.json");
        }
        const data = await response.json();

    data.lines.forEach(item => {
        console.log(`${item.currencyTypeName}: ${item.chaosEquivalent}c`);
});

    } catch (error) {
        console.error("Error loading fragments:", error);
    }
}

loadFragments();