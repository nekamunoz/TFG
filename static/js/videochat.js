const username = document.body.dataset.username;
const serverIp = document.body.dataset.server;
const port = document.body.dataset.port;
var mapPeers = {};
var offerPeers = {};
var webSocket;
var localStream = new MediaStream();
const constraints = {video: true, audio: true};
let localStreamReady = false;
let flag = true;

const localVideo = document.querySelector("#local-video");
const btnToggleAudio = document.querySelector("#btn-toggle-audio");
const btnToggleVideo = document.querySelector("#btn-toggle-video");

function waitForLocalStream() {
    return new Promise((resolve) => {
        if (localStream && localStream.getTracks().length > 0) {
        resolve();
        } else {
        const check = setInterval(() => {
            if (localStream && localStream.getTracks().length > 0) {
            clearInterval(check);
            resolve();
            }
        }, 100); 
        }
    });
}

async function webSocketOnMessage(event) {
	
    var parsedData = JSON.parse(event.data);
    var peerUsername = parsedData['peer'];
    var action = parsedData['action'];
	
    if (username === peerUsername) {
        return;
    }

    var receiver_channel_name = parsedData['message']['receiver_channel_name'];
		if (action === 'new-peer' && peerUsername !== username) {
				createOfferer(peerUsername, receiver_channel_name);
			return;
		}
		if (action === 'new-offer') {
			var offer = parsedData['message']['sdp'];
			await waitForLocalStream();
			createAnswerer(offer, peerUsername, receiver_channel_name);
			return;
		}
		if (action === 'new-answer') {
			var answer = parsedData['message']['sdp'];
			var peer = mapPeers[peerUsername][0];

			peer.setRemoteDescription(new RTCSessionDescription(answer))
			.then(() => {
				console.log("Respuesta remota aplicada correctamente:", peerUsername);
			})
			.catch(err => {
				console.error("Error al aplicar setRemoteDescription en offerer:", err);
			});
			return;
		}
}

navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        localStream = stream;
        localVideo.srcObject = localStream;
        localVideo.muted = true;
		
        var audioTracks = stream.getAudioTracks();
        var videoTracks = stream.getVideoTracks();

        audioTracks[0].enabled = true;
        videoTracks[0].enabled = true;

        btnToggleAudio.addEventListener("click", () => {
            audioTracks[0].enabled = !audioTracks[0].enabled;
            btnToggleAudio.innerHTML = audioTracks[0].enabled ? "Audio Mute" : "Audio Unmute";
        });

        btnToggleVideo.addEventListener("click", () => {
            videoTracks[0].enabled = !videoTracks[0].enabled;
            btnToggleVideo.innerHTML = videoTracks[0].enabled ? "Video Off" : "Video On";
        });
    })
    .catch(error => {
        console.error('Error accessing media devices.', error);
    });

function sendSignal(action, message) {
    const currentUsername = username || "anonymous";

    var jsonStr = JSON.stringify({
        peer: currentUsername,
        action: action,
        message: message,
    });

    if (webSocket && webSocket.readyState === WebSocket.OPEN) {
        webSocket.send(jsonStr);
    } else {
        console.error("WebSocket not connected. Cannot send message.");
    }
}

function createOfferer(peerUsername, receiver_channel_name) {
    offerPeers[peerUsername] = true;
	var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);

    var dc = peer.createDataChannel('channel');
    dc.addEventListener('open', () => {
        console.log('Data channel opened!');
    });

    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);
    mapPeers[peerUsername] = [peer, dc];

    peer.addEventListener('iceconnectionstatechange', () => {
		console.log("Pasa por aqui desconexión");
        var iceConnectionState = peer.iceConnectionState;
        if (['failed', 'disconnected', 'closed'].includes(iceConnectionState)) {
            delete mapPeers[peerUsername];
			console.log("-- DC de verdad");
			offerPeers[peerUsername] = false;
            if (iceConnectionState !== 'closed') {
                peer.close();
            }
            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            return;
        }
        sendSignal('new-offer', {
            sdp: peer.localDescription,
            receiver_channel_name: receiver_channel_name
        });
    });

    peer.createOffer()
        .then(o => peer.setLocalDescription(o))
        .then(() => {
            console.log('Local description (offer) set successfully!');
        });
}

function addLocalTracks(peer) {
    localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream);
    });
}

function createVideo(peerUsername) {
    var videoContainer = document.querySelector("#video-container");

    var remoteVideo = document.createElement('video');
    remoteVideo.id = peerUsername + '-video';
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;
    remoteVideo.classList.add("rounded");

    var videoWrapper = document.createElement('div');
    videoWrapper.className = "video-wrapper";

    videoContainer.appendChild(videoWrapper);
    videoWrapper.appendChild(remoteVideo);

    return remoteVideo;
}

function setOnTrack(peer, remoteVideo) {
    var remoteStream = new MediaStream();
    remoteVideo.srcObject = remoteStream;

    peer.addEventListener('track', event => {
        remoteStream.addTrack(event.track);
    });
}


function removeVideo(video) {
    var videoWrapper = video.parentNode;
    if (videoWrapper && videoWrapper.parentNode) {
        videoWrapper.parentNode.removeChild(videoWrapper);
    }
}

function createAnswerer(offer, peerUsername, receiver_channel_name) {

    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);
    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    mapPeers[peerUsername] = [peer, null];

    peer.addEventListener('datachannel', (e) => {
        peer.dc = e.channel;
        peer.dc.addEventListener('open', () => {
            console.log('Data channel opened!');
        });
        mapPeers[peerUsername][1] = peer.dc;
    });

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;
        if (['failed', 'disconnected', 'closed'].includes(iceConnectionState)) {
            delete mapPeers[peerUsername];

            if (iceConnectionState !== 'closed') {
                peer.close();
            }
            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            return;
        }
        sendSignal('new-answer', {
            sdp: peer.localDescription,
            receiver_channel_name: receiver_channel_name
        });
    });

    peer.setRemoteDescription(new RTCSessionDescription(offer))
        .then(() => {
            console.log('Remote description (offer) set successfully for %s.', peerUsername);
            return peer.createAnswer();
        })
        .then(answer => {
            console.log('Answer created!');
            return peer.setLocalDescription(answer);
        })
        .catch(error => {
            console.error("Error creando respuesta:", error);
        });
}

// Event Listeners
document.addEventListener("DOMContentLoaded", function () {
    var loc = window.location;
    var wsStart = "wss://";
    var endpoint = wsStart + serverIp + ":" + port + loc.pathname;
	
    console.log("Attempting connection to:", endpoint);
    webSocket = new WebSocket(endpoint);

    webSocket.addEventListener("open", (event) => {
        console.log("WebSocket connection opened!", event);
        sendSignal('new-peer', {});
    });
    webSocket.addEventListener("message", webSocketOnMessage);
    webSocket.addEventListener("close", (event) => {
        console.log("WebSocket connection closed!", event);
    });
    webSocket.addEventListener("error", (event) => {
        console.error("WebSocket error:", event);
    });
});