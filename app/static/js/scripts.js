// Function to show neck tag preview
function printNeckTag(firstName, lastName, occupation, company) {
    const neckTag = `
        <div style="border: 2px solid #000; padding: 20px; text-align: center; font-family: Arial, sans-serif;">
            <h1>${firstName} ${lastName}</h1>
            <h3>${occupation}</h3>
            <h4>${company}</h4>
        </div>
    `;
    document.getElementById('neckTagPreview').innerHTML = neckTag;
    document.getElementById('neckTagModal').classList.remove('hidden');
}

// Function to close modal
function closeModal() {
    document.getElementById('neckTagModal').classList.add('hidden');
}

// Function to print neck tag
function printContent(elementId) {
    const content = document.getElementById(elementId).innerHTML;
    const printWindow = window.open('', '', 'width=600,height=400');
    printWindow.document.write('<html><head><title>Print</title></head><body>');
    printWindow.document.write(content);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}

// Function to delete a participant
function deleteParticipant(id) {
    if (confirm('Are you sure you want to delete this participant?')) {
        window.location.href = `/delete/${id}`;
    }
}

// Function to update a participant
function updateParticipant(id) {
    window.location.href = `/update/${id}`;
}
