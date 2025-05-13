document.addEventListener('DOMContentLoaded', function() {
    // View robots.txt modal functionality
    const robotsModal = document.getElementById('robotsModal');
    if (robotsModal) {
        robotsModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const url = button.getAttribute('data-url');
            const content = button.getAttribute('data-content');
            
            document.getElementById('modalUrl').textContent = url;
            document.getElementById('robotsContent').textContent = content;
        });
    }

    // Filter buttons functionality
    const showAllBtn = document.getElementById('showAll');
    const showDisallowedBtn = document.getElementById('showDisallowed');
    const showAllowedBtn = document.getElementById('showAllowed');
    const showErrorsBtn = document.getElementById('showErrors');
    const resultsTable = document.getElementById('resultsTable');

    if (showAllBtn && showDisallowedBtn && showAllowedBtn && showErrorsBtn && resultsTable) {
        // Filter function
        function filterResults(filterClass) {
            const rows = document.querySelectorAll('#resultsTable tbody tr');
            
            rows.forEach(row => {
                if (filterClass === 'all' || row.classList.contains(filterClass)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        // Add event listeners to filter buttons
        showAllBtn.addEventListener('click', () => {
            filterResults('all');
            setActiveFilter(showAllBtn);
        });
        
        showDisallowedBtn.addEventListener('click', () => {
            filterResults('disallowed');
            setActiveFilter(showDisallowedBtn);
        });
        
        showAllowedBtn.addEventListener('click', () => {
            filterResults('allowed');
            setActiveFilter(showAllowedBtn);
        });
        
        showErrorsBtn.addEventListener('click', () => {
            filterResults('error');
            setActiveFilter(showErrorsBtn);
        });

        // Set active filter button
        function setActiveFilter(activeBtn) {
            [showAllBtn, showDisallowedBtn, showAllowedBtn, showErrorsBtn].forEach(btn => {
                btn.classList.remove('active', 'btn-light');
                btn.classList.add('btn-outline-light');
            });
            
            activeBtn.classList.remove('btn-outline-light');
            activeBtn.classList.add('active', 'btn-light');
        }

        // Set "All" as default active filter
        setActiveFilter(showAllBtn);
    }

    // Table sorting functionality
    const sortableHeaders = document.querySelectorAll('.sortable');
    
    if (sortableHeaders.length > 0) {
        sortableHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const sortKey = this.getAttribute('data-sort');
                const tbody = document.querySelector('#resultsTable tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const currentDir = this.getAttribute('data-dir') || 'asc';
                const newDir = currentDir === 'asc' ? 'desc' : 'asc';
                
                // Reset all headers
                sortableHeaders.forEach(h => {
                    h.setAttribute('data-dir', '');
                    h.querySelector('i').className = 'fas fa-sort ms-1';
                });
                
                // Set the current header
                this.setAttribute('data-dir', newDir);
                this.querySelector('i').className = newDir === 'asc' 
                    ? 'fas fa-sort-up ms-1' 
                    : 'fas fa-sort-down ms-1';
                
                // Sort the rows
                rows.sort((a, b) => {
                    let aValue, bValue;
                    
                    if (sortKey === 'url') {
                        aValue = a.cells[0].textContent.trim().toLowerCase();
                        bValue = b.cells[0].textContent.trim().toLowerCase();
                    } else if (sortKey === 'status') {
                        aValue = a.cells[1].textContent.trim().toLowerCase();
                        bValue = b.cells[1].textContent.trim().toLowerCase();
                    } else if (sortKey === 'google') {
                        aValue = a.cells[2].textContent.trim().toLowerCase();
                        bValue = b.cells[2].textContent.trim().toLowerCase();
                    }
                    
                    if (aValue < bValue) return newDir === 'asc' ? -1 : 1;
                    if (aValue > bValue) return newDir === 'asc' ? 1 : -1;
                    return 0;
                });
                
                // Reappend rows in the new order
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    }

    // Form submission - show loading indicator
    const analyzeForm = document.getElementById('analyzeForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (analyzeForm && analyzeBtn) {
        analyzeForm.addEventListener('submit', function() {
            // Count how many URLs are being analyzed
            const urlsTextarea = document.getElementById('urls');
            const urlsCount = urlsTextarea.value.split('\n')
                .filter(line => line.trim().length > 0).length;
            
            const originalText = analyzeBtn.innerHTML;
            analyzeBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing ${urlsCount} domains...`;
            analyzeBtn.disabled = true;
            
            // Show alert for large batches
            if (urlsCount > 50) {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-info alert-dismissible fade show mt-3';
                alertDiv.role = 'alert';
                alertDiv.innerHTML = `
                    <strong>Processing ${urlsCount} domains...</strong> This may take a minute or two. Please be patient.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                analyzeForm.appendChild(alertDiv);
            }
            
            // Calculate an appropriate timeout based on the number of URLs
            // Assume about 1-3 seconds per URL with a minimum of 60 seconds
            const timeout = Math.max(60000, urlsCount * 3000);
            
            // Re-enable button after timeout in case of a problem
            setTimeout(() => {
                analyzeBtn.innerHTML = originalText;
                analyzeBtn.disabled = false;
                
                // Add timeout message
                const timeoutAlert = document.createElement('div');
                timeoutAlert.className = 'alert alert-warning alert-dismissible fade show mt-3';
                timeoutAlert.role = 'alert';
                timeoutAlert.innerHTML = `
                    <strong>Still processing?</strong> The server may be taking longer than expected. You can refresh and try a smaller batch if needed.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                analyzeForm.appendChild(timeoutAlert);
            }, timeout);
        });
    }
});
