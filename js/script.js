function updateVisitorFields() {
    const visitorCount = document.getElementById('visitor-count').value;
    const visitorsContainer = document.getElementById('visitors-container');
    visitorsContainer.innerHTML = ''; // Clear previous fields

    for (let i = 1; i <= visitorCount; i++) {
        visitorsContainer.innerHTML += `
            <div class="visitor-section">
                <h3>Visitor ${i}</h3>
                <label for="name${i}">Name:</label>
                <input type="text" id="name${i}" name="name${i}" required>
                
                <label for="phone${i}">Phone Number:</label>
                <input type="text" id="phone${i}" name="phone${i}" maxlength="10" required>
                
                <label for="email${i}">Email:</label>
                <input type="email" id="email${i}" name="email${i}" required>
                
                <label for="id${i}">ID/Iqama:</label>
                <input type="text" id="id${i}" name="id${i}" maxlength="10" required>
                
                <label for="file${i}">Attach an ID:</label>
                <input type="file" id="file${i}" name="file${i}" required>
            </div>
        `;
    }
}

// Initial call to ensure the fields are displayed for the default value of 1 visitor
document.addEventListener('DOMContentLoaded', function() {
    updateVisitorFields();
    document.getElementById('visitor-count').addEventListener('input', updateVisitorFields);
});
