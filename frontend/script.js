const submitButton = document.getElementById('submitBtn');
const inputBox = document.getElementById('inputBox');
const outputBox = document.getElementById('outputBox');
const outputDiv = document.getElementById('output');
const userInput = document.getElementById('userInput');
const showHistoryButton = document.getElementById('showHistoryBtn');
const historyList = document.getElementById('historyList');
const historySection = document.getElementById('history');

let historyData = [];

submitButton.addEventListener('click', function () {
    const inputText = userInput.value;
    if (inputText.trim() === '') return;

    // Hide input box and show output box
    inputBox.style.transform = 'translateX(-100%)';
    outputBox.classList.add('visible');

    // Clear the output initially
    outputDiv.textContent = '';

    // Function to print one letter at a time
    let index = 0;
    function printOutput() {
        if (index < inputText.length) {
            outputDiv.textContent += inputText[index];
            index++;
            setTimeout(printOutput, 100);
        }
    }

    // Start printing the output
    printOutput();

    // Save the input-output pair in history (using inputText first)
    historyData.push({ input: inputText, output: inputText });

    // Update history in real-time if history section is visible
    if (historySection.style.display === 'block') {
        const historyItem = document.createElement('div');
        historyItem.classList.add('history-item');
        historyItem.innerHTML = ` 
            <div class="input">Input: ${inputText}</div>
            <div class="output">Output: ${inputText}</div>
        `;
        historyList.appendChild(historyItem);
    }

    // Clear the input field
    userInput.value = '';

    // Send the input claim to the backend and get the verified subclaims
    fetch('http://127.0.0.1:8000/generate_subclaims', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ claim: inputText })
    })
    .then(response => response.json())
    .then(data => {
        const verifiedSubclaims = data.verified_subclaims;

        // Display the verified subclaims
        outputDiv.textContent = verifiedSubclaims;

        // Save the input-output pair in history with subclaims output
        historyData.push({ input: inputText, output: verifiedSubclaims });

        // Update history in real-time if history section is visible
        if (historySection.style.display === 'block') {
            const historyItem = document.createElement('div');
            historyItem.classList.add('history-item');
            historyItem.innerHTML = ` 
                <div class="input">Input: ${inputText}</div>
                <div class="output">Output: ${verifiedSubclaims}</div>
            `;
            historyList.appendChild(historyItem);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        outputDiv.textContent = "There was an error processing your request. Please try again later.";
    });
});

showHistoryButton.addEventListener('click', function () {
    // Toggle the visibility of the history section
    if (historySection.style.display === 'none' || historySection.style.display === '') {
        historySection.style.display = 'block';
        historyList.innerHTML = '';

        // Display all history items
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
