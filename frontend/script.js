const submitButton = document.getElementById('submitBtn');
const inputBox = document.getElementById('inputBox');
const outputBox = document.getElementById('outputBox');
const outputDiv = document.getElementById('output');
const userInput = document.getElementById('userInput');
const showHistoryButton = document.getElementById('showHistoryBtn');
const historyList = document.getElementById('historyList');
const historySection = document.getElementById('history');

let historyData = [];

// Handle submitting the input
submitButton.addEventListener('click', async function () {
    const inputText = userInput.value.trim();
    if (inputText === '') return;

    // Hide input box and show output box
    inputBox.style.transform = 'translateX(-100%)';
    outputBox.classList.add('visible');

    // Clear the output initially
    outputDiv.textContent = 'Processing...';

    try {
        // Send input to FastAPI backend
        const response = await fetch('http://127.0.0.1:8000/process-claim', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ claim: inputText }) // Send the claim in the request body
        });

        // Check for errors in the response
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        outputDiv.textContent = result.final_result || "No result returned"; // Show the response or a fallback message

        // Save to history
        historyData.push({ input: inputText, output: result.final_result });

        // Update history if visible
        if (historySection.style.display === 'block') {
            const historyItem = document.createElement('div');
            historyItem.classList.add('history-item');
            historyItem.innerHTML = `
                <div class="input">Input: ${inputText}</div>
                <div class="output">Output: ${result.final_result}</div>
            `;
            historyList.appendChild(historyItem);
        }

    } catch (error) {
        outputDiv.textContent = `Error: ${error.message}`;
        console.error("Error:", error);
    }

    // Clear input field after submission
    userInput.value = '';
});

// Handle showing/hiding history
showHistoryButton.addEventListener('click', function () {
    if (historySection.style.display === 'none' || historySection.style.display === '') {
        historySection.style.display = 'block';
        historyList.innerHTML = '';

        // Display history
        historyData.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.classList.add('history-item');
            historyItem.innerHTML = `
                <div class="input">Input: ${item.input}</div>
                <div class="output">Output: ${item.output}</div>
            `;
            historyList.appendChild(historyItem);
        });
    } else {
        historySection.style.display = 'none';
    }
});
