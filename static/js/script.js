// Chat functionality
let selectedAccountId = null;

// Initialize chat on page load
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const accountSelect = document.getElementById('accountSelect');
    const profileBtn = document.getElementById('profileBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    
    // Send message on form submit
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage(userInput.value);
        userInput.value = '';
        userInput.focus();
    });
    
    // Update selected account
    accountSelect.addEventListener('change', (e) => {
        selectedAccountId = e.target.value || null;
    });
    
    // Profile button
    profileBtn.addEventListener('click', loadProfile);
    
    // Logout button
    logoutBtn.addEventListener('click', () => {
        window.location.href = '/logout';
    });
    
    // Allow Enter to send message
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Focus input on load
    userInput.focus();
});

async function sendMessage(message) {
    if (!message.trim()) return;
    
    const chatMessages = document.getElementById('chatMessages');
    
    // Add user message to chat
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user-message';
    userMessageDiv.innerHTML = `<div class="message-content">${escapeHtml(message)}</div>`;
    chatMessages.appendChild(userMessageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    try {
        // Send message to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                account_id: selectedAccountId ? parseInt(selectedAccountId) : null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Add bot response
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'message bot-message';
            
            let responseContent = data.response;
            
            // Handle special actions
            if (data.data) {
                responseContent = formatResponseWithData(data.response, data.data, data.action);
            }
            
            botMessageDiv.innerHTML = `<div class="message-content">${responseContent}</div>`;
            chatMessages.appendChild(botMessageDiv);
        } else {
            // Add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message bot-message';
            errorDiv.innerHTML = `<div class="message-content" style="color: #c33;">${escapeHtml(data.error || 'An error occurred')}</div>`;
            chatMessages.appendChild(errorDiv);
        }
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
    } catch (error) {
        console.error('Error:', error);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message bot-message';
        errorDiv.innerHTML = `<div class="message-content" style="color: #c33;">An error occurred. Please try again.</div>`;
        chatMessages.appendChild(errorDiv);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function formatResponseWithData(response, data, action) {
    let formattedResponse = escapeHtml(response) + '<br><br>';
    
    if (action === 'display_balances' && data.accounts) {
        formattedResponse += '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">';
        data.accounts.forEach(acc => {
            formattedResponse += `<div style="margin: 5px 0;"><strong>${acc.account_type}:</strong> ₹${formatCurrency(acc.balance)}</div>`;
        });
        formattedResponse += '</div>';
    }
    
    if (action === 'display_transactions' && data.transactions) {
        formattedResponse += '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto;">';
        data.transactions.slice(0, 5).forEach(trans => {
            formattedResponse += `<div style="margin: 8px 0; border-bottom: 1px solid #ddd; padding-bottom: 8px;">
                <strong>${trans.description}</strong><br>
                Amount: ₹${formatCurrency(trans.amount)}<br>
                <small>${trans.timestamp}</small>
            </div>`;
        });
        formattedResponse += '</div>';
    }
    
    if (action === 'display_offers' && data.offers) {
        formattedResponse += '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">';
        data.offers.forEach((offer, i) => {
            formattedResponse += `<div style="margin: 10px 0; padding: 8px; background: white; border-radius: 3px;">
                <strong>${i + 1}. ${escapeHtml(offer.title)}</strong><br>
                <small>${escapeHtml(offer.description)}</small><br>
                Code: <code>${escapeHtml(offer.code)}</code>
            </div>`;
        });
        formattedResponse += '</div>';
    }
    
    if (action === 'display_alerts' && data.alerts) {
        formattedResponse += '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">';
        if (data.alerts.length === 0) {
            formattedResponse += '<p>No alerts at this time.</p>';
        } else {
            data.alerts.forEach(alert => {
                const alertClass = alert.type === 'fraud' ? 'background: #fee;' : 'background: white;';
                formattedResponse += `<div style="margin: 8px 0; padding: 8px; ${alertClass} border-radius: 3px;">
                    <strong>${escapeHtml(alert.title)}</strong><br>
                    <small>${escapeHtml(alert.message)}</small>
                </div>`;
            });
        }
        formattedResponse += '</div>';
    }
    
    if (action === 'display_loan_products' && data.loans) {
        formattedResponse += '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">';
        data.loans.forEach(loan => {
            formattedResponse += `<div style="margin: 10px 0; padding: 8px; background: white; border-radius: 3px;">
                <strong>${escapeHtml(loan.product)}</strong><br>
                Amount: ${escapeHtml(loan.amount_range)}<br>
                Interest: ${escapeHtml(loan.interest_rate)}<br>
                Tenure: ${escapeHtml(loan.tenure)}
            </div>`;
        });
        formattedResponse += '</div>';
    }
    
    return formattedResponse;
}

async function loadProfile() {
    try {
        const response = await fetch('/api/profile');
        const data = await response.json();
        
        if (data.success) {
            const user = data.user;
            const profileContent = document.getElementById('profileContent');
            
            profileContent.innerHTML = `
                <div class="profile-info">
                    <div class="info-item">
                        <span class="info-label">Name:</span>
                        <span class="info-value">${escapeHtml(user.full_name)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Username:</span>
                        <span class="info-value">${escapeHtml(user.username)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span>
                        <span class="info-value">${escapeHtml(user.email)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Phone:</span>
                        <span class="info-value">${user.phone ? escapeHtml(user.phone) : 'Not provided'}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Member Since:</span>
                        <span class="info-value">${new Date(user.created_at).toLocaleDateString()}</span>
                    </div>
                </div>
            `;
            
            document.getElementById('profileModal').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function closeProfileModal() {
    document.getElementById('profileModal').style.display = 'none';
}

function formatCurrency(amount) {
    return amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const modal = document.getElementById('profileModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
