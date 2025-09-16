fetch("https://poe.ninja/api/data/currencyoverview?league=Mercenaries&type=Fragment")
    .then(Response => console.log(Response))
    .catch(error => console.error("Error fetching currency overview:", error))