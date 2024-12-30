document.getElementById("convert-button").addEventListener("click", async () => {
    const oracleInput = document.getElementById("oracle-input").value;
    const postgresOutput = document.getElementById("postgres-output");

    const response = await fetch("/convert", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ oracle_code: oracleInput }),
    });

    const data = await response.json();
    postgresOutput.value = data.postgres_code;
});
