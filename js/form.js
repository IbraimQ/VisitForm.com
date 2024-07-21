document.addEventListener('DOMContentLoaded', () => {
    const formBox = document.getElementById('form-box');
    loadInitialStep();

    function loadInitialStep() {
        formBox.innerHTML = `
            <div class="progress-bar">
                <div class="progress" id="progress"></div>
            </div>
            <h2>Fill up the form</h2>
            <label for="numVisitors">Choose the number of Visitors:</label>
            <input type="number" id="numVisitors" name="numVisitors" min="1" max="15" value="1"><br><br>

            <label for="manager">Choose a Manager:</label>
            <select id="manager" name="manager"></select><br><br>

            <label for="gateNumber">Gate Number:</label>
            <select id="gateNumber" name="gateNumber"></select><br><br>

            <div id="timeSlotsContainer">
                <label>Visit Time Slots:</label>
                <button type="button" onclick="addTimeSlot()">Add Time Slot</button>
            </div><br>

            <button type="button" onclick="nextStep()">Next</button>
        `;

        fetchManagersAndGates();
    }

    async function fetchManagersAndGates() {
        try {
            const response = await fetch('/api/managers_and_gates');
            const data = await response.json();
            populateForm(data);
        } catch (error) {
            console.error('Error fetching managers and gates:', error);
        }
    }

    function populateForm(data) {
        const managerSelect = document.getElementById('manager');
        const gateSelect = document.getElementById('gateNumber');

        data.managers.forEach(manager => {
            const option = document.createElement('option');
            option.value = manager.id;
            option.textContent = manager.name + " (" + manager.department + ")";
            managerSelect.appendChild(option);
        });

        data.gates.forEach(gate => {
            const option = document.createElement('option');
            option.value = gate.id;
            option.textContent = gate.gate_number;
            gateSelect.appendChild(option);
        });
    }

    window.addTimeSlot = function() {
        const timeSlotContainer = document.getElementById('timeSlotsContainer');
        const timeSlotDiv = document.createElement('div');
        timeSlotDiv.style.display = 'flex';
        timeSlotDiv.style.alignItems = 'center';
        timeSlotDiv.style.marginBottom = '10px';
        timeSlotDiv.innerHTML = `
            <label for="visitDate" style="margin-right: 5px;">Visit Date:</label>
            <input type="date" name="visitDate[]" required style="margin-right: 10px;">
            <label for="startTime" style="margin-right: 5px;">From:</label>
            <input type="time" name="startTime[]" required style="margin-right: 10px;">
            <label for="endTime" style="margin-right: 5px;">To:</label>
            <input type="time" name="endTime[]" required style="margin-right: 10px;">
            <button type="button" onclick="removeTimeSlot(this)" style="margin-left: 10px;">Remove</button>
        `;
        timeSlotContainer.appendChild(timeSlotDiv);
    }

    window.removeTimeSlot = function(button) {
        const timeSlotContainer = document.getElementById('timeSlotsContainer');
        timeSlotContainer.removeChild(button.parentElement);
    }

    window.nextStep = function() {
        const numVisitors = document.getElementById('numVisitors').value;
        formBox.innerHTML = `
            <div class="progress-bar">
                <div class="progress" id="progress" style="width: 33%;"></div>
            </div>
            <h2>Visitor 1:</h2>
            <label for="firstName">First Name:</label>
            <input type="text" id="firstName" name="firstName[0]" required><br><br>

            <label for="lastName">Last Name:</label>
            <input type="text" id="lastName" name="lastName[0]" required><br><br>

            <label for="phoneNumber">Phone Number:</label>
            <input type="text" id="phoneNumber" name="phoneNumber[0]" required><br><br>

            <label for="idNumber">ID/Iqama Number:</label>
            <input type="text" id="idNumber" name="idNumber[0]" required><br><br>

            <label for="email">Email:</label>
            <input type="email" id="email" name="email[0]" required><br><br>

            <label for="idAttachment">ID Attachment:</label>
            <input type="file" id="idAttachment" name="idAttachment[0]" required><br><br>

            <button type="button" onclick="nextVisitor(1, ${numVisitors})">Next</button>
        `;
    }

    window.nextVisitor = function(visitorIndex, totalVisitors) {
        if (visitorIndex < totalVisitors) {
            formBox.innerHTML = `
                <div class="progress-bar">
                    <div class="progress" id="progress" style="width: ${(visitorIndex + 1) / totalVisitors * 100}%;"></div>
                </div>
                <h2>Visitor ${visitorIndex + 1}:</h2>
                <label for="firstName">First Name:</label>
                <input type="text" id="firstName" name="firstName[${visitorIndex}]" required><br><br>

                <label for="lastName">Last Name:</label>
                <input type="text" id="lastName" name="lastName[${visitorIndex}]" required><br><br>

                <label for="phoneNumber">Phone Number:</label>
                <input type="text" id="phoneNumber" name="phoneNumber[${visitorIndex}]" required><br><br>

                <label for="idNumber">ID/Iqama Number:</label>
                <input type="text" id="idNumber" name="idNumber[${visitorIndex}]" required><br><br>

                <label for="email">Email:</label>
                <input type="email" id="email" name="email[${visitorIndex}]" required><br><br>

                <label for="idAttachment">ID Attachment:</label>
                <input type="file" id="idAttachment" name="idAttachment[${visitorIndex}]" required><br><br>

                ${visitorIndex < totalVisitors - 1 ? `<button type="button" onclick="nextVisitor(${visitorIndex + 1}, ${totalVisitors})">Next</button>` : `<button type="submit">Submit</button>`}
            `;
        } else {
            // Last visitor, show the submit button
            formBox.innerHTML += `<button type="submit">Submit</button>`;
        }
    }
});
