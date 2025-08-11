const readline = require('readline');
const https = require('https');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function ask(question) {
    return new Promise(resolve => rl.question(question, answer => resolve(answer)));
}

function fetchFragments(league) {
    const url = `https://poe.ninja/api/data/currencyoverview?league=${encodeURIComponent(league)}&type=Fragment`;
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    resolve(json);
                } catch (e) {
                    reject(e);
                }
            });
        }).on('error', reject);
    });
}

async function main() {
    console.log("Path of Exile Boss Profit Calculator");

    const league = await ask("Enter the league name (e.g., Ancestor, Standard): ");
    console.log(`Fetching boss fragment prices for ${league}...`);
    try {
        const data = await fetchFragments(league);
        if (data && data.lines) {
            console.log("\n--- Boss Fragment Prices (in chaos) ---");
            data.lines.forEach(line => {
                if (line.currencyTypeName && line.chaosEquivalent) {
                    console.log(`${line.currencyTypeName}: ${line.chaosEquivalent}`);
                }
            });
            console.log("");
        } else {
            console.log("No fragment data found.");
        }
    } catch (err) {
        console.error("Error fetching fragment prices:", err.message);
    }

    const runs = parseInt(await ask("Number of boss runs: "), 10);
    const costPerRun = parseFloat(await ask("Cost per run (chaos): "));
    const avgLootValue = parseFloat(await ask("Average loot value per run (chaos): "));

    const totalCost = runs * costPerRun;
    const totalLoot = runs * avgLootValue;
    const profit = totalLoot - totalCost;

    console.log("\n--- Results ---");
    console.log(`Total cost: ${totalCost} chaos`);
    console.log(`Total loot value: ${totalLoot} chaos`);
    console.log(`Net profit: ${profit} chaos`);

    rl.close();
}

main();