// --- MALHAR MOBILE SHOP CORE LOGIC ---

// 1. SPLASH SCREEN TO AUTH SCREEN TRANSITION & SESSION CHECK
window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        const auth = document.getElementById('auth-screen');
        const dashboard = document.getElementById('dashboard-screen');
        const activeRole = localStorage.getItem('current_role');

        if(splash) splash.style.opacity = '0';

        setTimeout(() => {
            if(splash) splash.classList.add('hidden');
            
            // Checking if user session already exists on page refresh
            if (activeRole === 'admin' || activeRole === 'customer') {
                if(dashboard) dashboard.classList.remove('hidden');
                if (activeRole === 'admin') {
                    document.querySelector('.nav-links').innerHTML = `
                        <li onclick="loadSection('admin_orders')" class="active-nav"><i class="fas fa-list-alt"></i> All Customer Orders</li>
                        <li onclick="logout()" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Log Out</li>
                    `;
                    loadSection('admin_orders');
                } else {
                    document.querySelector('.nav-links').innerHTML = `
                        <li onclick="loadSection('home')" class="active-nav"><i class="fas fa-home"></i> Home</li>
                        <li onclick="loadSection('mobiles')"><i class="fas fa-mobile-alt"></i> Order Mobiles</li>
                        <li onclick="loadSection('profile')"><i class="fas fa-user"></i> My Profile</li>
                        <li onclick="loadSection('about')"><i class="fas fa-info-circle"></i> About Shop</li>
                        <li onclick="logout()" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Log Out</li>
                    `;
                    loadSection('home');
                }
            } else {
                if(auth) auth.classList.remove('hidden');
            }
        }, 800);
    }, 3500);
});

// 2. TOGGLE BETWEEN LOGIN & SIGNUP FORMS
function switchAuthMode(mode) {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const authTitle = document.getElementById('auth-title');
    const btnLogin = document.getElementById('btn-login-active');
    const btnSignup = document.getElementById('btn-signup');

    if (mode === 'signup') {
        if(loginForm) loginForm.classList.add('hidden');
        if(signupForm) signupForm.classList.remove('hidden');
        if(authTitle) authTitle.innerText = "CREATE ACCOUNT";
        if(btnSignup) btnSignup.classList.add('active');
        if(btnLogin) btnLogin.classList.remove('active');
    } else {
        if(signupForm) signupForm.classList.add('hidden');
        if(loginForm) loginForm.classList.remove('hidden');
        if(authTitle) authTitle.innerText = "WELCOME BACK";
        if(btnLogin) btnLogin.classList.add('active');
        if(btnSignup) btnSignup.classList.remove('active');
    }
}

// 3. REAL OTP SYSTEM LOGIC (Using EmailJS)
let generatedOTP = null;

function sendOTP() {
    const contact = document.getElementById('reg-contact').value;
    const otpBtn = document.getElementById('send-otp-btn');
    
    if (!contact || !contact.includes('@')) {
        alert("⚠️ Please enter a valid Email Address to receive the OTP!");
        return;
    }

    // 4-digit random OTP generation
    generatedOTP = Math.floor(1000 + Math.random() * 9000).toString();

    if(otpBtn) {
        otpBtn.innerText = "Sending...";
        otpBtn.disabled = true;
    }

    const templateParams = {
        to_email: contact,
        otp: generatedOTP
    };

    // NOTE: Apne EmailJS dashboard se 'service_id' aur 'template_id' yahan conformingly verify karein
    emailjs.send('service_iwf9j7a', 'template_1frvmnc', templateParams)
        .then(function(response) {
            alert(`📩 Real OTP Sent Successfully to ${contact}!\nPlease check your inbox or spam folder.`);
            const otpField = document.getElementById('otp-input-field');
            if(otpField) otpField.classList.remove('hidden');
            if(otpBtn) {
                otpBtn.innerText = "RESEND OTP";
                otpBtn.disabled = false;
            }
        }, function(error) {
            alert("❌ Failed to send OTP. Please check your Gmail Connection on EmailJS.");
            if(otpBtn) {
                otpBtn.innerText = "TRY AGAIN";
                otpBtn.disabled = false;
            }
            console.log('FAILED...', error);
        });
}

// 4. REGISTRATION WITH REAL OTP VERIFICATION
document.getElementById('signup-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    const contact = document.getElementById('reg-contact').value;
    const otp = document.getElementById('reg-otp').value;
    const password = document.getElementById('reg-password').value;

    if (otp !== generatedOTP) {
        alert("❌ Invalid OTP! Verification failed.");
        return;
    }

    localStorage.setItem('malhar_user', contact);
    localStorage.setItem('malhar_pass', password);
    localStorage.setItem('malhar_name', name);

    alert("🎉 Account Registered Successfully! Switching to Login.");
    switchAuthMode('login');
});

// 5. LOGIN AUTHENTICATION (WITH ADMIN ACCOUNT)
document.getElementById('login-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const user = document.getElementById('login-username').value;
    const pass = document.getElementById('login-password').value;

    // Secret Admin Credentials for Malhar Mobile Shop
    if (user === "admin" && pass === "malhar@admin") {
        alert("👑 Welcome Admin! Opening Master Control Panel.");
        localStorage.setItem('current_role', 'admin');
        document.getElementById('auth-screen').classList.add('hidden');
        document.getElementById('dashboard-screen').classList.remove('hidden');
        
        document.querySelector('.nav-links').innerHTML = `
            <li onclick="loadSection('admin_orders')" class="active-nav"><i class="fas fa-list-alt"></i> All Customer Orders</li>
            <li onclick="logout()" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Log Out</li>
        `;
        loadSection('admin_orders');
        return;
    }

    const savedUser = localStorage.getItem('malhar_user');
    const savedPass = localStorage.getItem('malhar_pass');

    if (user === savedUser && pass === savedPass) {
        alert(`👋 Access Granted! Welcome to Malhar Dashboard.`);
        localStorage.setItem('current_role', 'customer');
        document.getElementById('auth-screen').classList.add('hidden');
        document.getElementById('dashboard-screen').classList.remove('hidden');
        
        document.querySelector('.nav-links').innerHTML = `
            <li onclick="loadSection('home')" class="active-nav"><i class="fas fa-home"></i> Home</li>
            <li onclick="loadSection('mobiles')"><i class="fas fa-mobile-alt"></i> Order Mobiles</li>
            <li onclick="loadSection('profile')"><i class="fas fa-user"></i> My Profile</li>
            <li onclick="loadSection('about')"><i class="fas fa-info-circle"></i> About Shop</li>
            <li onclick="logout()" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Log Out</li>
        `;
        loadSection('home');
    } else {
        alert("❌ Invalid Username or Password!");
    }
});

// 6. DYNAMIC DASHBOARD CONTENT SYSTEM
const sections = {
    home: `
        <h2>🚀 Our Premium Services</h2>
        <p style="color: var(--text-gray); margin-bottom: 20px;">Quality You Trust, Service You Deserve</p>
        <div class="grid-container">
            <div class="neon-card"><h3>🛠️ Mobile Repairing</h3><p>All Types of Mobile Repair</p></div>
            <div class="neon-card"><h3>💻 Software Solutions</h3><p>Software Update & Flashing</p></div>
            <div class="neon-card"><h3>⚡ Electronic Items</h3><p>High Quality Accessories</p></div>
            <div class="neon-card"><h3>🏠 Home Appliances</h3><p>AC, Cooler, Fridge, Washing Machine</p></div>
        </div>
    `,
    mobiles: `
        <h2>📱 Stock & Online Bookings</h2>
        <p style="color: var(--text-gray); margin-bottom: 20px;">All major brands available with easy finance options</p>
        <div class="grid-container">
            <div class="neon-card">
                <h3>iPhone 15 Pro Max</h3>
                <p>Natural Titanium | 256GB Storage</p>
                <span class="badge">Bajaj Finserv EMI</span>
                <button class="btn-neon" style="margin-top:15px; padding:8px;" onclick="bookItem('iPhone 15 Pro Max')">Book Order</button>
            </div>
            <div class="neon-card">
                <h3>Samsung S24 Ultra</h3>
                <p>Titanium Gray | 12GB RAM | AI Enabled</p>
                <span class="badge">TVS Credit Available</span>
                <button class="btn-neon" style="margin-top:15px; padding:8px;" onclick="bookItem('Samsung S24 Ultra')">Book Order</button>
            </div>
            <div class="neon-card">
                <h3>OnePlus 12R</h3>
                <p>Iron Gray | 16GB RAM + 256GB</p>
                <span class="badge">Low Down Payment</span>
                <button class="btn-neon" style="margin-top:15px; padding:8px;" onclick="bookItem('OnePlus 12R')">Book Order</button>
            </div>
        </div>
    `,
    profile: `
        <h2>👤 Active Session Details</h2>
        <div class="neon-card" style="margin-top: 20px; max-width: 500px;">
            <p style="margin-bottom: 10px;"><strong>Customer Name:</strong> <span id="dash-cust-name" style="color:var(--neon-blue);"></span></p>
            <p style="margin-bottom: 10px;"><strong>Registered ID/Email:</strong> <span id="dash-cust-user" style="color:var(--gold);"></span></p>
            <p><strong>Verification Rank:</strong> <span style="color:#00ff88;">Premium Buyer Tier</span></p>
        </div>
    `,
    about: `
        <h2>🏪 Store Directory & Contact Information</h2>
        <div class="neon-card" style="margin-top: 20px;">
            <h3>👑 Managed By: Aditya Madavi</h3>
            <p style="margin-top: 10px;"><i class="fas fa-phone-alt"></i> +91 8788461756</p>
            <p><i class="fab fa-whatsapp" style="color: #25d366;"></i> +91 9112390404</p>
        </div>
    `,
    admin_orders: `
        <h2>📋 Live Customer Orders (Admin View)</h2>
        <p style="color: var(--text-gray); margin-bottom: 20px;">Manage bookings and contact details for finance/EMI verification</p>
        <div class="neon-card" style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; color: var(--text-white);">
                <thead>
                    <tr style="border-bottom: 2px solid var(--neon-blue); color: var(--gold);">
                        <th style="padding: 12px;">Customer Name</th>
                        <th style="padding: 12px;">Email ID</th>
                        <th style="padding: 12px;">Product Booked</th>
                        <th style="padding: 12px;">Action</th>
                    </tr>
                </thead>
                <tbody id="admin-orders-table"></tbody>
            </table>
        </div>
    `
};

function loadSection(sectionName) {
    const mainArea = document.getElementById('main-content');
    if(mainArea) mainArea.innerHTML = sections[sectionName];

    const links = document.querySelectorAll('.nav-links li');
    links.forEach(link => link.classList.remove('active-nav'));
    
    links.forEach(link => {
        if(link.getAttribute('onclick') && link.getAttribute('onclick').includes(sectionName)) {
            link.classList.add('active-nav');
        }
    });

    if (sectionName === 'profile') {
        const dName = document.getElementById('dash-cust-name');
        const dUser = document.getElementById('dash-cust-user');
        if(dName) dName.innerText = localStorage.getItem('malhar_name') || "N/A";
        if(dUser) dUser.innerText = localStorage.getItem('malhar_user') || "N/A";
    }

    if (sectionName === 'admin_orders') {
        renderAdminOrders();
    }
    const sidebar = document.getElementById('sidebar');
    if(sidebar) sidebar.classList.remove('active');
}

// 7. ORDER BOOKING SYSTEM WITH ADMIN STORAGE
function bookItem(itemName) {
    const custName = localStorage.getItem('malhar_name') || "Walk-in Customer";
    const custContact = localStorage.getItem('malhar_user') || "Not Provided";

    let allOrders = JSON.parse(localStorage.getItem('malhar_master_orders')) || [];

    const newOrder = {
        name: custName,
        contact: custContact,
        product: itemName
    };

    allOrders.push(newOrder);
    localStorage.setItem('malhar_master_orders', JSON.stringify(allOrders));

    alert(`🎉 Success! Your booking request for ${itemName} has been securely submitted to the Admin Panel.`);
}

function renderAdminOrders() {
    const tableBody = document.getElementById('admin-orders-table');
    if (!tableBody) return;

    let allOrders = JSON.parse(localStorage.getItem('malhar_master_orders')) || [];

    if (allOrders.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="4" style="padding: 20px; text-align: center; color: var(--text-gray);">No orders received yet. 📭</td></tr>`;
        return;
    }

    tableBody.innerHTML = "";
    allOrders.forEach((order, index) => {
        tableBody.innerHTML += `
            <tr style="border-bottom: 1px solid var(--glass-border);">
                <td style="padding: 12px;">${order.name}</td>
                <td style="padding: 12px; color: var(--neon-blue);">${order.contact}</td>
                <td style="padding: 12px; color: var(--gold);">${order.product}</td>
                <td style="padding: 12px;"><button onclick="deleteOrder(${index})" style="background:#ff4d4d; border:none; color:white; padding:5px 10px; cursor:pointer; border-radius:4px;">Complete</button></td>
            </tr>
        `;
    });
}

function deleteOrder(index) {
    let allOrders = JSON.parse(localStorage.getItem('malhar_master_orders')) || [];
    allOrders.splice(index, 1);
    localStorage.setItem('malhar_master_orders', JSON.stringify(allOrders));
    renderAdminOrders();
}

// 8. SIDEBAR RESPONSIVE TOGGLE
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if(sidebar) sidebar.classList.toggle('active');
}

// 9. LOGOUT SESSION KILLER
function logout() {
    if (confirm("Are you sure you want to log out from Malhar Mobile Shop?")) {
        document.getElementById('dashboard-screen').classList.add('hidden');
        document.getElementById('auth-screen').classList.remove('hidden');
        document.getElementById('login-form').reset();
        localStorage.removeItem('current_role');
    }
}
