// Frontend 404 Debug Script - Run this in browser console
// Copy and paste this entire script into the browser console on http://localhost:3000

console.log('🔍 Starting Frontend 404 Debug...');

// 1. Check authentication
async function checkAuth() {
    console.log('1. Checking authentication...');
    
    const token = localStorage.getItem('access_token');
    console.log('Token in localStorage:', token ? 'Present' : 'Missing');
    
    if (!token) {
        console.log('❌ No token found. Attempting login...');
        try {
            const response = await fetch('http://localhost:8000/api/v1/auth/login/access-token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: 'test@example.com',
                    password: 'testpass123'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                console.log('✅ Login successful, token stored');
                return data.access_token;
            } else {
                console.log('❌ Login failed:', response.status);
                return null;
            }
        } catch (error) {
            console.log('❌ Login error:', error);
            return null;
        }
    }
    
    return token;
}

// 2. Test specific endpoints that are causing 404s
async function testEndpoints(token) {
    console.log('2. Testing endpoints...');
    
    const endpoints = [
        { url: 'http://localhost:8000/api/v1/media/categories', name: 'Categories (media.ts:45)' },
        { url: 'http://localhost:8000/api/v1/media/scan-info', name: 'Scan Info (ScanInfo.vue:106)' },
        { url: 'http://localhost:8000/api/v1/media/', name: 'Media List (Library.vue:273)' },
        { url: 'http://localhost:8000/api/v1/playlists/', name: 'Playlists' }
    ];
    
    for (const endpoint of endpoints) {
        try {
            console.log(`Testing: ${endpoint.name}`);
            
            const response = await fetch(endpoint.url, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${endpoint.name} - SUCCESS (${response.status})`);
                console.log('   Data keys:', Object.keys(data));
            } else {
                console.log(`❌ ${endpoint.name} - FAILED (${response.status})`);
                console.log('   Response:', await response.text());
            }
        } catch (error) {
            console.log(`💥 ${endpoint.name} - ERROR:`, error);
        }
    }
}

// 3. Check Vue app state (if available)
function checkVueState() {
    console.log('3. Checking Vue app state...');
    
    // Check if Vue devtools are available
    if (window.__VUE__) {
        console.log('✅ Vue detected');
    } else {
        console.log('⚠️ Vue not detected in global scope');
    }
    
    // Check auth store
    const authData = localStorage.getItem('access_token');
    console.log('Auth token in storage:', authData ? 'Present' : 'Missing');
    
    // Check for common Vue errors
    const vueErrors = [];
    const originalError = console.error;
    console.error = function(...args) {
        if (args.some(arg => typeof arg === 'string' && arg.includes('404'))) {
            vueErrors.push(args.join(' '));
        }
        originalError.apply(console, args);
    };
    
    setTimeout(() => {
        console.error = originalError;
        if (vueErrors.length > 0) {
            console.log('🚨 Vue 404 errors detected:');
            vueErrors.forEach(error => console.log('   -', error));
        } else {
            console.log('✅ No Vue 404 errors detected in last 5 seconds');
        }
    }, 5000);
}

// 4. Monitor network requests
function monitorRequests() {
    console.log('4. Setting up network monitoring...');
    
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        console.log(`🌐 FETCH REQUEST: ${url}`);
        
        return originalFetch.apply(this, args)
            .then(response => {
                if (response.ok) {
                    console.log(`✅ FETCH SUCCESS: ${url} -> ${response.status}`);
                } else {
                    console.log(`❌ FETCH FAILED: ${url} -> ${response.status}`);
                }
                return response;
            })
            .catch(error => {
                console.log(`💥 FETCH ERROR: ${url} ->`, error);
                throw error;
            });
    };
    
    console.log('✅ Network monitoring active');
}

// 5. Check for CORS issues
async function checkCORS() {
    console.log('5. Checking CORS...');
    
    try {
        const response = await fetch('http://localhost:8000/health', {
            method: 'OPTIONS'
        });
        console.log('✅ CORS preflight successful');
    } catch (error) {
        console.log('❌ CORS preflight failed:', error);
    }
}

// Run all tests
async function runAllTests() {
    console.log('🚀 Running comprehensive frontend debug...');
    
    const token = await checkAuth();
    if (token) {
        await testEndpoints(token);
    }
    
    checkVueState();
    monitorRequests();
    await checkCORS();
    
    console.log('🏁 Debug complete. Monitor console for ongoing requests.');
    console.log('💡 If you see 404s, they should now be logged with full details.');
}

// Auto-run
runAllTests();

// Export functions for manual testing
window.debugFrontend = {
    checkAuth,
    testEndpoints,
    checkVueState,
    monitorRequests,
    checkCORS,
    runAllTests
};

console.log('🔧 Debug functions available as window.debugFrontend');
console.log('   Example: debugFrontend.testEndpoints("your-token")');
